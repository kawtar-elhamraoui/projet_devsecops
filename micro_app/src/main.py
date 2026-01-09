import sqlite3
import pickle
import subprocess
from fastapi import FastAPI, HTTPException
from datetime import datetime
import json

app = FastAPI(title="Test API Sécurité", version="1.0.0")

# Initialiser une base SQLite pour les tests
def init_db():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES ('admin', 'admin@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES ('user', 'user@example.com')")
    conn.commit()
    conn.close()

init_db()

# ========== ENDPOINT 1: INJECTION SQL ==========
@app.get("/vuln/sql/{user_input}")
def sql_injection(user_input: str):
    """⚠️ VULNÉRABLE : Injection SQL"""
    conn = sqlite3.connect("test.db")
    # VULNÉRABLE : concaténation directe
    cursor = conn.execute(f"SELECT * FROM users WHERE username = '{user_input}'")
    results = cursor.fetchall()
    conn.close()
    
    return {
        "vulnerability": "SQL Injection",
        "query": f"SELECT * FROM users WHERE username = '{user_input}'",
        "results": results,
        "example_exploit": "Essayez avec: admin' OR '1'='1"
    }

# ========== ENDPOINT 2: DÉSÉRIALISATION PICKLE ==========
@app.post("/vuln/deserialize")
def pickle_deserialize(data: str):
    """⚠️ VULNÉRABLE : Désérialisation pickle"""
    try:
        # VULNÉRABLE : pickle avec données utilisateur
        loaded = pickle.loads(data.encode())
        return {
            "vulnerability": "Pickle Deserialization",
            "data": str(loaded),
            "risk": "Code execution possible",
            "secure_alternative": "Utiliser json.loads()"
        }
    except Exception as e:
        return {"error": str(e)}

# ========== ENDPOINT 3: COMMAND INJECTION ==========
@app.get("/vuln/command/{cmd}")
def command_injection(cmd: str):
    """⚠️ VULNÉRABLE : Command Injection"""
    # VULNÉRABLE : shell=True avec input utilisateur
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "vulnerability": "Command Injection",
        "command": cmd,
        "output": result.stdout,
        "error": result.stderr,
        "example_exploit": "Essayez avec: ls; cat /etc/passwd"
    }

# ========== ENDPOINTS SÉCURISÉS (CONTRE-EXEMPLES) ==========
@app.get("/secure/sql/{user_input}")
def secure_sql(user_input: str):
    """✅ SÉCURISÉ : Pas d'injection SQL"""
    conn = sqlite3.connect("test.db")
    # SÉCURISÉ : requête paramétrée
    cursor = conn.execute("SELECT * FROM users WHERE username = ?", (user_input,))
    results = cursor.fetchall()
    conn.close()
    
    return {
        "security": "SQL sécurisé",
        "query": "SELECT * FROM users WHERE username = ?",
        "param": user_input,
        "results": results
    }

@app.post("/secure/deserialize")
def secure_deserialize(data: str):
    """✅ SÉCURISÉ : JSON au lieu de pickle"""
    try:
        loaded = json.loads(data)
        return {
            "security": "JSON sécurisé",
            "data": loaded
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

@app.get("/secure/command/{cmd}")
def secure_command(cmd: str):
    """✅ SÉCURISÉ : Pas de command injection"""
    allowed = ["echo", "date", "pwd"]
    if cmd not in allowed:
        raise HTTPException(status_code=400, detail="Commande non autorisée")
    
    result = subprocess.run([cmd], shell=False, capture_output=True, text=True)
    return {
        "security": "Commande sécurisée",
        "output": result.stdout
    }

# ========== ENDPOINTS UTILES ==========
@app.get("/")
def root():
    return {
        "api": "Test de sécurité API",
        "vulnerabilities": [
            "/vuln/sql/{input} - Injection SQL",
            "/vuln/deserialize - Désérialisation pickle (POST)",
            "/vuln/command/{cmd} - Command injection"
        ],
        "secure": [
            "/secure/sql/{input} - SQL sécurisé",
            "/secure/deserialize - JSON sécurisé (POST)",
            "/secure/command/{cmd} - Commande sécurisée"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

# Dans micro_app/src/main.py, ajoutez UN SEUL endpoint :

@app.get("/demo/dast/{input}")
def dast_demo_endpoint(input: str):
    """Endpoint spécial pour démontrer DAST"""
    
    # Réponse différente selon l'input
    if input == "safe":
        return {"status": "safe", "message": "Normal operation"}
    
    # Si l'input contient du SQL
    elif "' OR '" in input:
        return {
            "status": "vulnerable",
            "warning": "SQL_INJECTION_DETECTED",
            "input": input,
            "debug": "This would be dangerous in production!",
            "risk": "HIGH"
        }
    
    # Si l'input contient des commandes
    elif ";" in input or "&&" in input:
        return {
            "status": "vulnerable", 
            "warning": "COMMAND_INJECTION_DETECTED",
            "input": input,
            "debug": "Shell commands detected!",
            "risk": "CRITICAL"
        }
    
    return {"status": "processed", "input": input}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)