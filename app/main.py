# app/main.py
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from . import database, endpoints

load_dotenv()
APP_NAME = os.getenv("APP_NAME", "Default App Title")
app = FastAPI(title=APP_NAME)
app.include_router(endpoints.router)

# Create the database and table if they don't exist on real startup
conn = database.get_db_connection()
database.initialize_db(conn) # We'll create an initialize_db in the next step
conn.close()