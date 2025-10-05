from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.email_routes import router as email_router

load_dotenv()

app = FastAPI(title="SMTP Email Service")

# Include the email routes
app.include_router(email_router, prefix="/api", tags=["email"])
