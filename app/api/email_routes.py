from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional
import threading
import asyncio

from app.model.email import EmailRequest
from app.services.email_service import EmailService

router = APIRouter()


@router.post("/send-email/")
async def send_email_route(
    to_emails: List[str] = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    cc_emails: Optional[List[str]] = Form(None),
    bcc_emails: Optional[List[str]] = Form(None),
    attachment: Optional[UploadFile] = File(None),
):
    """
    Submit as form-data.
    - to_emails/cc_emails/bcc_emails support multiple values by repeating the same key.
    - attachment is optional.
    """
    try:
        attachment_content = None
        attachment_filename = None

        if attachment:
            attachment_content = await attachment.read()
            attachment_filename = attachment.filename

        asyncio.create_task(
            EmailService.send_email(
                to_emails=to_emails,
                subject=subject,
                body=body,
                cc_emails=cc_emails,
                bcc_emails=bcc_emails,
                attachment_filename=attachment_filename,
                attachment_content=attachment_content,
            )
        )
        return {"status": True, "message": "Email is being sent in the background!"}
    except Exception as e:
        return {"status": False, "message": f"Exception {e}"}


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
