from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "API DevSecOps" in response.json()["message"]

def test_create_item():
    response = client.post("/items?name=Test&description=Pour%20test")
    assert response.status_code == 201
    assert response.json()["name"] == "Test"

def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)