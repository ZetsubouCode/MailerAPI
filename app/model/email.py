from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EmailRequest(BaseModel):
    to_emails: List[EmailStr]
    subject: str
    body: str
    cc_emails: Optional[List[EmailStr]] = None
    bcc_emails: Optional[List[EmailStr]] = None