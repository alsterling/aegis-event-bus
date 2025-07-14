# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from . import db, endpoints, security

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()          # creates tables for SQLite tests only
    yield

app = FastAPI(title="Aegis Event Bus", lifespan=lifespan)
app.include_router(endpoints.router)
app.include_router(security.router)
