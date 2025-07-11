# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from . import database, endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup events."""
    database.initialize_db()
    print("INFO:     Application startup complete.")
    yield
    print("INFO:     Application shutdown.")

app = FastAPI(title="Aegis Event Bus", lifespan=lifespan)
app.include_router(endpoints.router)