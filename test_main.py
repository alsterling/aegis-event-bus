from fastapi.testclient import TestClient
from main import app # This imports the 'app' object from your main.py file

# This creates a special client that can call your API directly for tests
client = TestClient(app)

# --- TEST 1: The "Is the Server Online?" Test ---
def test_read_root_endpoint():
    """Tests if the main GET / endpoint is working."""
    # Send a virtual request to the "/" endpoint
    response = client.get("/")
    # Assert (check) that the HTTP status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the JSON response is exactly what we expect
    assert response.json() == {"status": "Aegis Event Bus is online"}

# --- TEST 2: The "Does Job Creation Work?" Test ---
def test_create_new_job_endpoint():
    """Tests if the POST /job endpoint creates a valid job."""
    # Send a virtual POST request to the "/job" endpoint
    response = client.post("/job")
    # Assert that the request was successful
    assert response.status_code == 200
    # Check the response data
    data = response.json()
    assert "job_id" in data # Check if the 'job_id' key is in the response
    assert data["job_id"].startswith("FC-") # Check if the ID has the correct prefix