# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import structlog

# Import all the necessary modules from your 'app' package
from . import database, endpoints, security, logging_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup events."""
    # This single line sets up your professional logging system
    logging_config.setup_logging()
    
    logger = structlog.get_logger(__name__)
    logger.info("application.startup.begin")
    
    database.initialize_db()
    
    logger.info("application.startup.complete")
    yield
    # Code below yield runs on shutdown
    logger.info("application.shutdown.complete")


# Create the main app object and tell it to use our lifespan function
app = FastAPI(title="Aegis Event Bus", lifespan=lifespan)

# Include the routers from your other files
app.include_router(endpoints.router)
app.include_router(security.router)