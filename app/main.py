# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from . import database, endpoints, logging_config, security # Added security import

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup events."""
    logging_config.setup_logging()
    database.initialize_db()
    print("INFO:     Application startup complete.")
    yield
    print("INFO:     Application shutdown.")

# This creates the main app object and tells it to use our lifespan function
app = FastAPI(title="Aegis Event Bus", lifespan=lifespan)

# This includes all the routes from endpoints.py
app.include_router(endpoints.router)
app.include_router(security.router) # We must also include the security router