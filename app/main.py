from fastapi import FastAPI
from app.api.email_routes import router as email_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Include the email routes
app.include_router(email_router)
