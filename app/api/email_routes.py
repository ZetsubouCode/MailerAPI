import os
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import threading

from app.model.email import EmailRequest
from app.services.email_service import EmailService, EmailServiceError

router = APIRouter()
logger = logging.getLogger("mailer.api")

_MAX_ATTACHMENT_MB = int(os.getenv("ATTACHMENT_MAX_MB", "20"))
_MAX_ATTACHMENT_BYTES = _MAX_ATTACHMENT_MB * 1024 * 1024
_READ_CHUNK_BYTES = 1024 * 1024


async def _read_upload_limited(upload: UploadFile) -> bytes:
    total = 0
    chunks = []
    try:
        while True:
            chunk = await upload.read(_READ_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if total > _MAX_ATTACHMENT_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"Attachment '{upload.filename}' exceeds {_MAX_ATTACHMENT_MB}MB limit",
                )
            chunks.append(chunk)
    finally:
        await upload.close()
    return b"".join(chunks)


async def _handle_send_email(
    to_emails: List[str] = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    cc_emails: Optional[List[str]] = Form(None),
    bcc_emails: Optional[List[str]] = Form(None),
    attachment: Optional[List[UploadFile]] = File(None),
    attachment_inline: Optional[List[str]] = Form(None),
    attachment_cid: Optional[List[str]] = Form(None),
):
    """
    Submit as form-data.
    - to_emails/cc_emails/bcc_emails support multiple values by repeating the same key.
    - attachment is optional.
    """
    try:
        logger.info(
            "API.send_email received | to=%d cc=%d bcc=%d subject_len=%d attachments=%d",
            len(to_emails or []),
            len(cc_emails or []) if cc_emails else 0,
            len(bcc_emails or []) if bcc_emails else 0,
            len(subject or ""),
            len(attachment or []),
        )
        attachments = []
        if attachment:
            for idx, item in enumerate(attachment):
                content = await _read_upload_limited(item)
                inline = False
                cid = None
                if attachment_inline and idx < len(attachment_inline):
                    inline = str(attachment_inline[idx]).strip().lower() in {"1", "true", "yes"}
                if attachment_cid and idx < len(attachment_cid):
                    cid = attachment_cid[idx] or None
                attachments.append({
                    "filename": item.filename,
                    "content": content,
                    "inline": inline,
                    "cid": cid,
                })

        result = await EmailService.send_email(
            to_emails=to_emails,
            subject=subject,
            body=body,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
            attachments=attachments,
        )
        return result
    except HTTPException:
        raise
    except EmailServiceError as e:
        request_id = getattr(e, "request_id", None)
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": False,
                "smtp_accepted": False,
                "code": e.code,
                "message": e.safe_message,
                "request_id": request_id,
            },
        )
    except Exception as e:
        logger.exception("API.send_email failed")
        return JSONResponse(
            status_code=500,
            content={
                "status": False,
                "smtp_accepted": False,
                "code": "INTERNAL_ERROR",
                "message": "Internal mailer error.",
            },
        )

@router.post("/send-email/")
async def send_email_route(
    to_emails: List[str] = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    cc_emails: Optional[List[str]] = Form(None),
    bcc_emails: Optional[List[str]] = Form(None),
    attachment: Optional[List[UploadFile]] = File(None),
    attachment_inline: Optional[List[str]] = Form(None),
    attachment_cid: Optional[List[str]] = Form(None),
):
    return await _handle_send_email(
        to_emails=to_emails,
        subject=subject,
        body=body,
        cc_emails=cc_emails,
        bcc_emails=bcc_emails,
        attachment=attachment,
        attachment_inline=attachment_inline,
        attachment_cid=attachment_cid,
    )

@router.post("/send-email", include_in_schema=False)
async def send_email_route_no_slash(
    to_emails: List[str] = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    cc_emails: Optional[List[str]] = Form(None),
    bcc_emails: Optional[List[str]] = Form(None),
    attachment: Optional[List[UploadFile]] = File(None),
    attachment_inline: Optional[List[str]] = Form(None),
    attachment_cid: Optional[List[str]] = Form(None),
):
    return await _handle_send_email(
        to_emails=to_emails,
        subject=subject,
        body=body,
        cc_emails=cc_emails,
        bcc_emails=bcc_emails,
        attachment=attachment,
        attachment_inline=attachment_inline,
        attachment_cid=attachment_cid,
    )


@router.post("/schedule_email")
async def schedule_email_route(email_request: EmailRequest):
    """
    Pass a JSON body matching EmailRequest, including ISO8601 'send_time'.
    This spawns a background thread that sleeps until the time and then sends.
    """
    thread = threading.Thread(target=EmailService.schedule_email, args=(email_request,))
    thread.daemon = True
    thread.start()
    return {"status": True, "message": "Email scheduled successfully."}


@router.get("/health")
async def health():
    return {"status": True, "service": "mailer-api"}
