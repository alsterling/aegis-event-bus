# app/schemas.py

from pydantic import BaseModel
import datetime

# This class defines the structure of the data your API will return.
# It inherits from Pydantic's BaseModel.
class Job(BaseModel):
    job_id: str