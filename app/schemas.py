# app/schemas.py
from pydantic import BaseModel, ConfigDict
import datetime


class AuditLog(BaseModel):
    id: int
    job_id: str
    action: str
    timestamp: datetime.datetime

    # This is the new, modern way to configure Pydantic models
    model_config = ConfigDict(from_attributes=True)


class Job(BaseModel):
    job_id: str


class Token(BaseModel):
    access_token: str
    token_type: str
