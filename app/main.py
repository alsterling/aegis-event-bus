# app/main.py

from fastapi import FastAPI
import os
from dotenv import load_dotenv
# The '.' means "import from the same app folder"
from . import database, endpoints

# --- Application Setup ---
load_dotenv()

# Get the app title from the .env file
APP_NAME = os.getenv("APP_NAME", "Default App Title")

# Create the main FastAPI application object
app = FastAPI(title=APP_NAME)

# This function will run once when the application starts
@app.on_event("startup")
def startup_event():
    database.initialize_db()

# Include the API endpoints from the endpoints.py file
app.include_router(endpoints.router)