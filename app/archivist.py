# app/archivist.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# We still define DATA_ROOT here to be used by the main application
DATA_ROOT = Path(os.getenv("DATA_ROOT", "projects_data"))


def create_job_folders(job_id: str, base_path: Path):
    """
    Creates the standard folder structure for a new job inside a given base_path.
    """
    job_root = base_path / job_id
    subfolders = ["01_raw_data", "02_processed_data", "03_reports"]

    # Ensure the main data root directory exists
    base_path.mkdir(exist_ok=True)

    for sub in subfolders:
        (job_root / sub).mkdir(parents=True, exist_ok=True)
