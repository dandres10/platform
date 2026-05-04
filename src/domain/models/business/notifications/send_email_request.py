# SPEC-006 T2
from typing import Dict, Optional

from pydantic import BaseModel


class SendEmailRequest(BaseModel):
    to: str
    subject_key: str
    body_key: str
    template_vars: Optional[Dict[str, str]] = None
    language: Optional[str] = None
