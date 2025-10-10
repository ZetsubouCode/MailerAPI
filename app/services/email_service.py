import os
import time
import smtplib
import ssl
import asyncio
import logging
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Optional

from app.model.email import EmailRequest

# ---------------------------
# Logging setup
# ---------------------------
_LOG_NAME = "mailer"
logger = logging.getLogger(_LOG_NAME)
if not logger.handlers:
    # Basic console logging; level can be overridden by LOG_LEVEL env
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

def _mask_addr(addr: str) -> str:
    """Mask an email like 'john.doe@example.com' -> 'j***e@example.com'."""
    try:
        local, domain = addr.split("@", 1)
    except ValueError:
        return "***"
    if len(local) <= 2:
        masked_local = local[0] + "*" if local else "*"
    else:
        masked_local = f"{local[0]}***{local[-1]}"
    return f"{masked_local}@{domain}"

def _mask_list(addrs: Optional[List[str]]) -> List[str]:
    return [] if not addrs else [_mask_addr(a) for a in addrs]

class EmailService:
    @staticmethod
    def _smtp_config():
        """
        Generic SMTP config via environment variables.
        Works for Gmail, Hostinger, Niagahoster, etc.
        """
        host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        port = int(os.getenv("SMTP_PORT", "465"))
        user = os.getenv("SMTP_USER") or os.getenv("GMAIL_USER")
        password = os.getenv("SMTP_PASSWORD") or os.getenv("GMAIL_PASSWORD")
        security = (os.getenv("SMTP_SECURITY") or "ssl").lower()  # ssl | starttls | none
        mail_from = os.getenv("SMTP_FROM") or user
        if not user or not password:
            logger.error("SMTP credentials missing: set SMTP_USER and SMTP_PASSWORD (or GMAIL_*).")
            raise RuntimeError("SMTP_USER/SMTP_PASSWORD (or GMAIL_*) must be set")

        logger.debug(
            "SMTP config loaded | host=%s port=%s security=%s user=%s from=%s",
            host, port, security, _mask_addr(user) if user else None, mail_from
        )
        return host, port, user, password, security, mail_from

    @staticmethod
    def _build_message(
        mail_from: str,
        to_emails: List[str],
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
        attachment_filename: Optional[str] = None,
        attachment_content: Optional[bytes] = None,
    ):
        msg = MIMEMultipart()
        msg["From"] = mail_from
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject
        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)
        msg.attach(MIMEText(body, "html"))

        if attachment_content and attachment_filename:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_content)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{attachment_filename}"',
            )
            msg.attach(part)

        logger.debug(
            "MIME message built | subject_len=%d body_len=%d attachment=%s",
            len(subject) if subject else 0,
            len(body) if body else 0,
            f"{attachment_filename} ({len(attachment_content)} bytes)" if attachment_content else "none",
        )
        return msg

    @staticmethod
    def _send_now(
        to_emails: List[str],
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachment_filename: Optional[str] = None,
        attachment_content: Optional[bytes] = None,
    ):
        req_id = uuid.uuid4().hex[:8]
        t0 = time.perf_counter()
        host, port, user, password, security, mail_from = EmailService._smtp_config()

        masked_to = _mask_list(to_emails)
        masked_cc = _mask_list(cc_emails)
        masked_bcc = _mask_list(bcc_emails)
        logger.info(
            "[%s] Sending email | from=%s to=%s cc=%s bcc=%s subject=%r",
            req_id, _mask_addr(mail_from), to_emails, cc_emails, bcc_emails, subject
        )

        msg = EmailService._build_message(
            mail_from, to_emails, subject, body, cc_emails, attachment_filename, attachment_content
        )
        all_recipients = list(to_emails) + (cc_emails or []) + (bcc_emails or [])

        # Connect
        server = None
        try:
            if security == "ssl":
                logger.debug("[%s] Connecting with SSL to %s:%s", req_id, host, port)
                server = smtplib.SMTP_SSL(host, port, timeout=30)
            else:
                logger.debug("[%s] Connecting (plain) to %s:%s", req_id, host, port)
                server = smtplib.SMTP(host, port, timeout=30)
                server.ehlo()
                if security == "starttls":
                    logger.debug("[%s] Starting TLS", req_id)
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()

            # Login
            logger.debug("[%s] Logging in as %s", req_id, _mask_addr(user))
            server.login(user, password)

            # Send
            logger.debug("[%s] Sending message to %d recipient(s)", req_id, len(all_recipients))
            refused = server.sendmail(mail_from, all_recipients, msg.as_string())
            # Per smtplib docs, 'refused' is a dict of {recipient: (code, resp)} for any failures
            if refused:
                logger.warning("[%s] Some recipients were refused: %s", req_id, refused)
            else:
                logger.info("[%s] Email accepted by server for all recipients", req_id)

        except smtplib.SMTPAuthenticationError as e:
            logger.error("[%s] SMTP auth failed: %s", req_id, str(e))
            raise
        except smtplib.SMTPException as e:
            logger.error("[%s] SMTP error: %s", req_id, str(e))
            raise
        except Exception as e:
            logger.exception("[%s] Unexpected error during send: %s", req_id, str(e))
            raise
        finally:
            if server:
                try:
                    server.quit()
                    logger.debug("[%s] SMTP connection closed", req_id)
                except Exception:
                    logger.debug("[%s] SMTP connection close raised; ignoring", req_id)
            t1 = time.perf_counter()
            logger.info("[%s] Done in %.3fs", req_id, t1 - t0)

    # Keep async signature to match your route's create_task usage
    @staticmethod
    async def send_email(
        to_emails: List[str],
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachment_filename: Optional[str] = None,
        attachment_content: Optional[bytes] = None,
    ):
        # smtplib is blocking; run it in a thread to avoid blocking the event loop
        logger.debug("Dispatching send_email to thread executor (async wrapper)")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            EmailService._send_now,
            to_emails,
            subject,
            body,
            cc_emails,
            bcc_emails,
            attachment_filename,
            attachment_content,
        )

    @staticmethod
    def schedule_email(email_request: EmailRequest):
        """
        Very simple scheduler: sleeps until send_time, then sends.
        Runs inside a thread started by the route.
        """
        req_id = uuid.uuid4().hex[:8]
        try:
            send_time = datetime.fromisoformat(email_request.send_time)
        except Exception:
            logger.error("[%s] Invalid send_time format: %r", req_id, getattr(email_request, "send_time", None))
            raise

        now = datetime.now()
        delay = (send_time - now).total_seconds()
        logger.info(
            "[%s] Scheduling email | now=%s target=%s delay=%.3fs to=%s subject=%r",
            req_id, now.isoformat(), send_time.isoformat(), max(delay, 0.0),
            _mask_list(email_request.to_emails), email_request.subject
        )

        if delay > 0:
            time.sleep(delay)
        else:
            logger.warning("[%s] send_time is in the past; sending immediately", req_id)

        # Call the same send_email logic synchronously from this thread
        # (spin a private event loop and run the async method once)
        try:
            asyncio.run(
                EmailService.send_email(
                    to_emails=email_request.to_emails,
                    subject=email_request.subject,
                    body=email_request.body,
                    cc_emails=getattr(email_request, "cc_emails", None),
                    bcc_emails=getattr(email_request, "bcc_emails", None),
                    # Attachments aren't part of EmailRequest in this project; skip by default
                )
            )
            logger.info("[%s] Scheduled email sent", req_id)
        except Exception as e:
            logger.exception("[%s] Scheduled send failed: %s", req_id, str(e))
            raise
