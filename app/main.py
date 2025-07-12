# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from . import database, endpoints, security

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup events."""
    database.initialize_db()
    print("INFO:     Application startup complete.")
    yield
    print("INFO:     Application shutdown.")

app = FastAPI(title="Aegis Event Bus", lifespan=lifespan)

# Include the main API router
app.include_router(endpoints.router)

# THIS IS THE FIX: Explicitly include the security router
app.include_router(security.router)