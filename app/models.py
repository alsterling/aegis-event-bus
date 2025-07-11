# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    # SQLAlchemy handles the SERIAL/AUTOINCREMENT automatically
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    # Use DateTime with timezone for robust timestamping
    timestamp = Column(DateTime(timezone=True), nullable=False)