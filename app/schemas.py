# app/schemas.py
from pydantic import BaseModel

class Job(BaseModel):
    job_id: str

class Token(BaseModel):
    access_token: str
    token_type: str