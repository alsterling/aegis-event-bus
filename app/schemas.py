# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from .models import AuditLog


class Job(BaseModel):
    job_id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class JobsPage(BaseModel):
    items: List[AuditLog]
    next_cursor: Optional[int] = None
