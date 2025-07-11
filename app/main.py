# app/main.py
from fastapi import FastAPI
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from . import database, endpoints
from .logging_config import setup_logging

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    setup_logging()
    database.initialize_db()
    print("INFO:     Application startup complete.")
    yield
    print("INFO:     Application shutdown.")

APP_NAME = os.getenv("APP_NAME", "Default App Title")
app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.include_router(endpoints.router)