import httpx
from app.core.config import settings

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

async def send_email(to_email: str, subject: str, body: str):
    headers = {
        "accept": "application/json",
        "api-key": settings.api_key,
        "content-type": "application/json"
    }

    data = {
        "sender": {"email": settings.sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": body
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(BREVO_API_URL, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for bad responses

    return response.json()
