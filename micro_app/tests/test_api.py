import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    # Vérifie la structure de base
    assert "api" in data
    assert "vulnerabilities" in data
    assert "secure" in data
    
def test_get_items():
    """Test l'endpoint GET /items"""
    response = client.get("/items")
    assert response.status_code == 200
    
    items = response.json()
    # Vérifie que c'est une liste
    assert isinstance(items, list)
    
def test_create_item():
    """Test l'endpoint POST /items"""
    response = client.post("/items", params={"name": "TestItem", "description": "For testing"})
    
    # Votre API retourne probablement 200, pas 201
    # Vérifiez ce que retourne vraiment votre API
    if response.status_code == 200:
        data = response.json()
        assert "name" in data
        assert data["name"] == "TestItem"
    elif response.status_code == 201:
        data = response.json()
        assert "id" in data
    else:
        # Si un autre code, c'est peut-être normal aussi
        print(f"Code de statut: {response.status_code}")
        assert response.status_code in [200, 201]

def test_api_structure():
    """Test que l'API expose les bonnes routes"""
    response = client.get("/")
    data = response.json()
    
    # Vérifie que les routes vulnérables sont documentées
    if "vulnerabilities" in data:
        vuln_routes = data["vulnerabilities"]
        assert any("sql" in route.lower() for route in vuln_routes)
        assert any("command" in route.lower() for route in vuln_routes)