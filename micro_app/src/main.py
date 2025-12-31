# micro_app/src/main.py - AJOUTEZ CES VULNÉRABILITÉS
import sqlite3
import pickle
import subprocess
from fastapi import FastAPI

app = FastAPI()

# VULNÉRABILITÉ 1 : Injection SQL
@app.get("/search/{query}")
def search(query: str):
    conn = sqlite3.connect("test.db")
    # VULNÉRABLE : concaténation directe
    cursor = conn.execute(f"SELECT * FROM products WHERE name = '{query}'")
    return {"results": cursor.fetchall()}

# VULNÉRABILITÉ 2 : Désérialisation non sécurisée
@app.post("/load_data")
def load_data(data: str):
    # VULNÉRABLE : pickle non sécurisé
    loaded = pickle.loads(data.encode())
    return {"data": loaded}

# VULNÉRABILITÉ 3 : Command Injection
@app.get("/run/{command}")
def run_command(command: str):
    # VULNÉRABLE : commande système
    result = subprocess.run(command, shell=True, capture_output=True)
    return {"output": result.stdout.decode()}


# Ajoutez ce endpoint
@app.get("/health")
def health_check():
    """Endpoint pour vérifier que l'API fonctionne"""
    return {
        "status": "healthy",
        "service": "DevSecOps API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test/vulnerable")
def test_vulnerable(param: str = ""):
    """Endpoint de test avec vulnérabilité INTENTIONNELLE"""
    # NE FAITES PAS ÇA EN PRODUCTION !
    # Simule une vulnérabilité pour les tests SAST
    import subprocess
    result = subprocess.run(f"echo {param}", shell=True, capture_output=True)
    return {"output": result.stdout.decode()}