# app/main.py

from fastapi import FastAPI
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import our own modules
from . import endpoints
from .logging_config import setup_logging
from .database import initialize_db

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup events."""
    setup_logging()
    # Initialize the database and create tables if they don't exist
    initialize_db()
    print("INFO:     Application startup complete.")
    yield
    print("INFO:     Application shutdown.")

APP_NAME = os.getenv("APP_NAME", "Default App Title")
app = FastAPI(title=APP_NAME, lifespan=lifespan)

# Include the API endpoints from the endpoints.py file
app.include_router(endpoints.router)