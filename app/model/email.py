from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EmailRequest(BaseModel):
    to_emails: List[str]
    subject: str
    body: str
    cc_emails: Optional[List[str]] = None
    bcc_emails: Optional[List[str]] = None