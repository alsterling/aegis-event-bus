# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base
import datetime

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)