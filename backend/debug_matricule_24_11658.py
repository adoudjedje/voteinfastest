import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def debug_matricule_24_11658():
    """Diagnostic spécifique pour le matricule 24-11658"""
    matricule = "24-11658"
    
    print(f"🔍 DIAGNOSTIC SPÉCIFIQUE POUR {matricule}")
    print("=" * 60)
    
    # 1. Vérifier si l'étudiant existe
    print(f"\n1️⃣ VÉRIFICATION EXISTENCE ÉTUDIANT")
    print("-" * 40)
    
    try:
        student_doc = db.collection('etudiants').document(matricule).get()
        if student_doc.exists:
            student_data = student_doc.to_dict()
            print("✅ Étudiant trouvé!")
            print(f"   Nom: {student_data.get('nom', 'N/A')}")
            print(f"   Prénom: {student_data.get('prenom', 'N/A')}")
            print(f"   Filière: {student_data.get('filiere', 'N/A')}")
            print(f"   Numéro: {student_data.get('numero', 'N/A')}")
            print(f"   Téléphone: {student_data.get('telephone', 'N/A')}")
        else:
            print("❌ Étudiant NON TROUVÉ!")
            print("   → C'est la cause de l'erreur!")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # 2. Vérifier le statut de la session
    print(f"\n2️⃣ VÉRIFICATION SESSION DE VOTE")
    print("-" * 40)
    
    try:
        session_doc = db.collection('vote_sessions').document('default_session').get()
        if session_doc.exists:
            session_data = session_doc.to_dict()
            is_active = session_data.get('is_active', False)
            print(f"   Session active: {is_active}")
            if is_active:
                print("✅ Session active - OK")
            else:
                print("❌ Session inactive - Problème!")
                return False
        else:
            print("❌ Session non trouvée!")
            return False
    except Exception as e:
        print(f"❌ Erreur session: {e}")
        return False
    
    # 3. Vérifier si l'étudiant a déjà voté
    print(f"\n3️⃣ VÉRIFICATION VOTES EXISTANTS")
    print("-" * 40)
    
    try:
        votes = db.collection('votes').where('student_matricule', '==', matricule).stream()
        vote_list = list(votes)
        
        if vote_list:
            print(f"   Votes trouvés: {len(vote_list)}")
            for i, vote_doc in enumerate(vote_list, 1):
                vote_data = vote_doc.to_dict()
                is_valid = vote_data.get('is_valid', False)
                print(f"   Vote {i}: Valide = {is_valid}")
                if is_valid:
                    print("❌ Étudiant a déjà voté - Problème!")
                    return False
        else:
            print("✅ Aucun vote trouvé - OK")
    except Exception as e:
        print(f"❌ Erreur votes: {e}")
        return False
    
    # 4. Vérifier la connexion backend
    print(f"\n4️⃣ VÉRIFICATION BACKEND")
    print("-" * 40)
    
    try:
        import requests
        import socket
        
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"   IP locale: {local_ip}")
        
        # Tester différentes URLs
        urls_to_test = [
            f"http://localhost:5000/health",
            f"http://127.0.0.1:5000/health",
            f"http://{local_ip}:5000/health"
        ]
        
        backend_accessible = False
        for url in urls_to_test:
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    print(f"✅ Backend accessible via: {url}")
                    backend_accessible = True
                    break
            except:
                continue
        
        if not backend_accessible:
            print("❌ Backend non accessible!")
            print("   → Le backend Flask n'est probablement pas démarré")
            return False
            
    except ImportError:
        print("⚠️  Module 'requests' non installé")
    except Exception as e:
        print(f"❌ Erreur backend: {e}")
        return False
    
    print(f"\n✅ TOUTES LES VÉRIFICATIONS PASSÉES")
    print("   Le problème vient probablement du frontend ou de la logique de validation")
    return True

def check_backend_routes():
    """Vérifier les routes du backend"""
    print(f"\n🔌 VÉRIFICATION DES ROUTES BACKEND")
    print("-" * 40)
    
    try:
        import requests
        
        # Tester la route de validation d'étudiant
        test_data = {"matricule": "24-11658"}
        
        urls_to_test = [
            "http://localhost:5000/validate_student",
            "http://127.0.0.1:5000/validate_student"
        ]
        
        for url in urls_to_test:
            try:
                response = requests.post(url, json=test_data, timeout=5)
                print(f"   {url}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Réponse: {response.json()}")
                else:
                    print(f"   Erreur: {response.text}")
            except Exception as e:
                print(f"   {url}: Erreur - {e}")
                
    except Exception as e:
        print(f"❌ Erreur test routes: {e}")

def check_frontend_config():
    """Vérifier la configuration du frontend"""
    print(f"\n🌐 VÉRIFICATION CONFIGURATION FRONTEND")
    print("-" * 40)
    
    try:
        # Vérifier le fichier de configuration API
        import os
        frontend_dir = "../src/services"
        api_file = os.path.join(frontend_dir, "api.js")
        
        if os.path.exists(api_file):
            print(f"✅ Fichier API trouvé: {api_file}")
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "localhost:5000" in content or "127.0.0.1:5000" in content:
                    print("✅ Configuration backend détectée")
                else:
                    print("⚠️  Configuration backend non trouvée")
        else:
            print(f"❌ Fichier API non trouvé: {api_file}")
            
    except Exception as e:
        print(f"❌ Erreur config frontend: {e}")

def main():
    print("🔍 DIAGNOSTIC COMPLET - ERREUR PERSISTANTE")
    print("=" * 70)
    
    # Diagnostic principal
    all_checks_passed = debug_matricule_24_11658()
    
    if all_checks_passed:
        # Vérifications supplémentaires
        check_backend_routes()
        check_frontend_config()
        
        print(f"\n" + "="*70)
        print("📋 DIAGNOSTIC FINAL:")
        print("-" * 30)
        print("✅ Toutes les vérifications de base sont OK")
        print("❌ Le problème vient probablement de:")
        print("   1. Backend Flask non démarré")
        print("   2. Mauvaise configuration frontend")
        print("   3. Problème de réseau/CORS")
        print("   4. Logique de validation dans le frontend")
        
        print(f"\n💡 SOLUTIONS À ESSAYER:")
        print("-" * 30)
        print("1. Démarrer le backend Flask: python app.py")
        print("2. Vérifier la console du navigateur (F12)")
        print("3. Vérifier les logs du backend")
        print("4. Tester avec un autre matricule valide")
        
    else:
        print(f"\n❌ PROBLÈME IDENTIFIÉ DANS LES VÉRIFICATIONS DE BASE")

if __name__ == "__main__":
    main() 