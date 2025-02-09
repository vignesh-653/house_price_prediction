import json
import pytest
import sys
import os
from fastapi.testclient import TestClient
# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Now import the app from the correct location
from main12 import app

# Create a TestClient instance for the app
client = TestClient(app)

# Load test cases from a JSON file
with open(r"app\tests\data\test_login_data.json") as f:
    test_cases = json.load(f)

@pytest.mark.parametrize("test_case", test_cases)
def test_login(test_case):
    # Send a POST request with form data instead of JSON
    response = client.post("/login", data=test_case["input_data"])  # Use `data` for form data
    assert response.status_code == test_case["expected_status"]

