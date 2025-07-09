# app/main.py

from fastapi import FastAPI
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from . import database, endpoints

load_dotenv()

# --- 1. Lifespan Manager (The New Way to handle startup/shutdown) ---
# This is the modern replacement for on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This part runs when the application starts up
    print("Application startup...")
    database.initialize_db()
    yield
    # This part runs when the application shuts down (we don't need anything here yet)
    print("Application shutdown...")

# --- 2. Application Setup ---
APP_NAME = os.getenv("APP_NAME", "Default App Title")
app = FastAPI(title=APP_NAME, lifespan=lifespan)

# --- 3. Include Routers ---
app.include_router(endpoints.router)