from fastapi import FastAPI
from app.api.email_routes import router as email_router

app = FastAPI()

# Include the email routes
app.include_router(email_router)
