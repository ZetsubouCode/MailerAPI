from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form
from typing import List, Optional
from app.model.email import EmailRequest
from app.services.email_service import EmailService

import schedule, threading,asyncio

router = APIRouter()

@router.post("/send-email/")
async def send_email_route(to_emails: List[str] = Form(...),
                           subject: str = Form(...),
                            body: str = Form(...),
                            cc_emails: Optional[List[str]] = Form(None),
                            bcc_emails: Optional[List[str]] = Form(None),
                            attachment: Optional[UploadFile|str] = File(None)):
    try:
        attachment_content = None
    
        if attachment:
            # Read the attachment content immediately before the file gets closed
            attachment_content = await attachment.read()

        asyncio.create_task(
        EmailService.send_email(
            to_emails=to_emails,
            subject=subject,
            body=body,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
            attachment_filename=attachment.filename if attachment else None,
            attachment_content=attachment_content
        )
    )
        return {"status":True,"message": "Email is being sent in the background!"}
    except Exception as e:
        return {"status":False,"message": f"Exception {e}"}

@router.post("/schedule_email")
async def schedule_email_route(email_request: EmailRequest):
    # Start a new thread to handle scheduling
    thread = threading.Thread(target=EmailService.schedule_email, args=(email_request,))
    thread.start()
    return {"message": "Email scheduled successfully."}