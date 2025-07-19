import requests

print("🔌 Test de connexion au backend...")

try:
    response = requests.get("http://localhost:5000/api/health", timeout=3)
    print(f"✅ Backend accessible! Code: {response.status_code}")
    
    # Test de connexion étudiant
    test_data = {"matricule": "24-11661"}
    response = requests.post("http://localhost:5000/api/login", json=test_data, timeout=5)
    
    print(f"Test login '24-11661': Code {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Connexion réussie: {data}")
    else:
        print(f"❌ Erreur: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Backend non accessible - vérifiez qu'il est démarré")
except Exception as e:
    print(f"❌ Erreur: {e}") 