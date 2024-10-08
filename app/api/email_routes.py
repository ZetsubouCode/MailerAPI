from fastapi import APIRouter, BackgroundTasks, UploadFile,File
from app.model.email import EmailRequest
from app.services.email_service import EmailService

import schedule, threading

router = APIRouter()

@router.post("/send-email/")
async def send_email_route(email: EmailRequest, background_tasks: BackgroundTasks,attachment: UploadFile = File(None)):
    try:
        # Add email sending to background tasks
        background_tasks.add_task(EmailService.send_email, email.to_emails, email.subject, email.body,email.cc_emails,email.bcc_emails,attachment)
        return {"status":False,"message": "Email is being sent in the background!"}
    except Exception as e:
        return {"status":False,"message": f"Exception {e}"}

@app.post("/schedule_email")
async def schedule_email_route(email_request: EmailRequest):
    # Start a new thread to handle scheduling
    thread = threading.Thread(target=EmailService.schedule_email, args=(email_request,))
    thread.start()
    return {"message": "Email scheduled successfully."}