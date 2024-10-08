from fastapi import APIRouter, BackgroundTasks, UploadFile,File
from app.model.email import EmailRequest
from app.services.email_service import send_email

router = APIRouter()

@router.post("/send-email/")
async def send_email_route(email: EmailRequest, background_tasks: BackgroundTasks,attachment: UploadFile = File(None)):
    try:
        # Add email sending to background tasks
        background_tasks.add_task(send_email, email.to_email, email.subject, email.body,email.cc_emails,email.bcc_emails,attachment)
        return {"status":False,"message": "Email is being sent in the background!"}
    except Exception as e:
        return {"status":False,"message": f"Exception {e}"}
