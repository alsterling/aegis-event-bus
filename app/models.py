# app/models.py
import datetime as dt
from typing import Optional
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    action: str
    timestamp: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
