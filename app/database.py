# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import structlog
from dotenv import load_dotenv

load_dotenv()
logger = structlog.get_logger(__name__)

# Get the URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine for PostgreSQL
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models (tables)
Base = declarative_base()

def get_db():
    """FastAPI dependency to provide a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_db():
    """Creates the database tables if they don't exist."""
    try:
        # Import models here to ensure they are registered with Base
        from . import models 
        Base.metadata.create_all(bind=engine)
        logger.info("database.initialize.success")
    except Exception as e:
        logger.error("database.initialize.failed", error=str(e))