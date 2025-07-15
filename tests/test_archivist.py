# tests/test_archivist.py

from pathlib import Path
import shutil
from app.archivist import create_job_folders

# Define a temporary folder name for our tests to use
TEST_DATA_ROOT = Path("test_projects_data_temp")


def test_folder_creation():
    """
    Tests if the create_job_folders function correctly creates the
    required directory structure.
    """
    job_id = "TEST-JOB-123"

    # --- Run the function we are testing, providing the base_path ---
    create_job_folders(job_id=job_id, base_path=TEST_DATA_ROOT)

    # --- Assert that the folders now exist ---
    assert (TEST_DATA_ROOT / job_id).is_dir()
    assert (TEST_DATA_ROOT / job_id / "01_raw_data").is_dir()

    # --- Clean up after the test is done ---
    shutil.rmtree(TEST_DATA_ROOT)
