import requests
import time

def test_backend():
    """Test rapide du backend Flask"""
    print("🔌 TEST RAPIDE DU BACKEND")
    print("=" * 40)
    
    try:
        # Test de santé du backend
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"✅ Backend accessible (code: {response.status_code})")
        
        # Test de connexion étudiant
        test_data = {"matricule": "24-11661"}
        response = requests.post("http://localhost:5000/api/login", json=test_data, timeout=5)
        
        print(f"Test login matricule '24-11661':")
        print(f"Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion réussie!")
            print(f"   Étudiant: {data.get('nom', '')} {data.get('prenom', '')}")
        else:
            print(f"❌ Échec de connexion")
            try:
                error = response.json()
                print(f"   Erreur: {error.get('error', 'Erreur inconnue')}")
            except:
                print(f"   Erreur: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Backend non accessible")
        print("   Le backend Flask n'est pas démarré")
        print("   Démarrez avec: python app.py")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_backend() 