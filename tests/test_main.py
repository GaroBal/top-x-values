from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get():
    # Send a GET request to the root endpoint
    response = client.get("/ping")

    assert response.status_code == 200

    # Assert the response JSON matches the expected output
    assert response.json() == ["pong"]