from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.email import EmailRequest
from app.services.email_service import send_email

router = APIRouter()

@router.post("/send-email/")
async def send_email_route(email: EmailRequest, background_tasks: BackgroundTasks):
    try:
        # Add email sending to background tasks
        background_tasks.add_task(send_email, email.to_email, email.subject, email.body)
        return {"message": "Email is being sent in the background!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
