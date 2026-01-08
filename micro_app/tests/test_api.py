import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root():
    """Test endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "API DevSecOps" in data["message"]

def test_health():
    """Test endpoint santé"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "endpoints" in data

def test_items():
    """Test gestion des items"""
    # GET items (vide au début)
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []
    
    # POST item
    response = client.post("/items?name=TestItem&description=TestDesc")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "TestItem"
    assert "id" in data
    
    # GET items après création
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_vulnerable_endpoints():
    """Test des endpoints vulnérables (pour démonstration)"""
    # SQL Injection
    response = client.get("/search/test")
    assert response.status_code == 200
    assert "warning" in response.json()
    
    # Command Injection
    response = client.get("/run/echo%20test")
    assert response.status_code == 200
    assert "output" in response.json()

def test_secure_endpoints():
    """Test des endpoints sécurisés"""
    response = client.get("/secure/search/test")
    assert response.status_code == 200
    assert "security" in response.json()
    
    response = client.get("/secure/run/echo")
    assert response.status_code == 200

def test_devsecops_info():
    """Test info DevSecOps"""
    response = client.get("/devsecops/info")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "security_showcase" in data

# Test minimal qui passe toujours
def test_minimal():
    """Test minimal de validation"""
    assert 1 + 1 == 2
    print("✅ Validation mathématique réussie")