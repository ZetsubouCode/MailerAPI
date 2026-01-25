import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.api.email_routes import router as email_router

load_dotenv()

app = FastAPI(title="SMTP Email Service")

# Include the email routes
app.include_router(email_router, prefix="/api", tags=["email"])

logger = logging.getLogger("mailer.api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "API.validation_error | path=%s errors=%s",
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
