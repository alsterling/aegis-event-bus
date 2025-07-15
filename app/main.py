# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator

from . import db, endpoints, security, logging_config

# ---------- logging & metrics set‑up ----------
logging_config.setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()             # creates tables when running under pytest (SQLite)
    yield
# ---------------------------------------------

app = FastAPI(title="Aegis Event Bus", lifespan=lifespan)

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(endpoints.router)
app.include_router(security.router)
