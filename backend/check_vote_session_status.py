import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def check_vote_session_status():
    """Vérifier le statut de la session de vote"""
    print("🗳️  VÉRIFICATION DU STATUT DE LA SESSION DE VOTE")
    print("=" * 60)
    
    try:
        # Récupérer la session de vote
        session_doc = db.collection('vote_sessions').document('default_session').get()
        
        if session_doc.exists:
            session_data = session_doc.to_dict()
            print("✅ SESSION DE VOTE TROUVÉE")
            print(f"  Nom: {session_data.get('name', 'N/A')}")
            print(f"  ID: {session_data.get('id', 'N/A')}")
            print(f"  Active: {session_data.get('is_active', 'N/A')}")
            print(f"  Description: {session_data.get('description', 'N/A')}")
            print(f"  Max votes par étudiant: {session_data.get('max_votes_per_student', 'N/A')}")
            print(f"  Date de début: {session_data.get('start_date', 'N/A')}")
            print(f"  Date de fin: {session_data.get('end_date', 'N/A')}")
            
            # Vérifier si la session est active
            is_active = session_data.get('is_active', False)
            if is_active:
                print("\n✅ SESSION ACTIVE - Les étudiants peuvent voter")
            else:
                print("\n❌ SESSION INACTIVE - Les étudiants ne peuvent pas voter")
                print("   → C'est probablement la cause de l'erreur!")
                
        else:
            print("❌ AUCUNE SESSION DE VOTE TROUVÉE")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def check_backend_connection():
    """Vérifier la connexion au backend"""
    print(f"\n🔌 VÉRIFICATION DE LA CONNEXION BACKEND")
    print("-" * 40)
    
    try:
        # Vérifier si le backend Flask est accessible
        import requests
        import socket
        
        # Vérifier l'IP locale
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"  IP locale: {local_ip}")
        
        # Essayer de se connecter au backend
        try:
            response = requests.get(f"http://{local_ip}:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend accessible")
            else:
                print(f"❌ Backend répond avec code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend non accessible: {e}")
            
    except ImportError:
        print("⚠️  Module 'requests' non installé")
    except Exception as e:
        print(f"❌ Erreur vérification backend: {e}")

def check_firebase_connection():
    """Vérifier la connexion Firebase"""
    print(f"\n🔥 VÉRIFICATION DE LA CONNEXION FIREBASE")
    print("-" * 40)
    
    try:
        # Tester la connexion Firebase
        test_doc = db.collection('test_connection').document('test').get()
        print("✅ Connexion Firebase OK")
        
        # Vérifier les collections principales
        collections = ['etudiants', 'candidates', 'votes', 'vote_sessions']
        for collection_name in collections:
            try:
                docs = list(db.collection(collection_name).limit(1).stream())
                print(f"  ✅ Collection '{collection_name}': {len(docs)} document(s)")
            except Exception as e:
                print(f"  ❌ Collection '{collection_name}': Erreur - {e}")
                
    except Exception as e:
        print(f"❌ Erreur connexion Firebase: {e}")

def check_student_login_process(matricule):
    """Simuler le processus de connexion d'un étudiant"""
    print(f"\n👤 SIMULATION DE CONNEXION ÉTUDIANT: {matricule}")
    print("-" * 50)
    
    try:
        # Étape 1: Vérifier si l'étudiant existe
        student_doc = db.collection('etudiants').document(matricule).get()
        if not student_doc.exists:
            print("❌ Étape 1: Étudiant non trouvé")
            return False
        print("✅ Étape 1: Étudiant trouvé")
        
        # Étape 2: Vérifier si la session est active
        session_doc = db.collection('vote_sessions').document('default_session').get()
        if not session_doc.exists:
            print("❌ Étape 2: Session de vote non trouvée")
            return False
            
        session_data = session_doc.to_dict()
        if not session_data.get('is_active', False):
            print("❌ Étape 2: Session de vote inactive")
            return False
        print("✅ Étape 2: Session de vote active")
        
        # Étape 3: Vérifier si l'étudiant a déjà voté
        votes = db.collection('votes').where('student_matricule', '==', matricule).where('is_valid', '==', True).stream()
        vote_list = list(votes)
        
        if vote_list:
            print("❌ Étape 3: Étudiant a déjà voté")
            return False
        print("✅ Étape 3: Étudiant n'a pas encore voté")
        
        print("✅ TOUTES LES ÉTAPES VALIDÉES - Connexion autorisée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur simulation: {e}")
        return False

def activate_vote_session():
    """Activer la session de vote"""
    print(f"\n🔓 ACTIVATION DE LA SESSION DE VOTE")
    print("-" * 40)
    
    try:
        # Activer la session
        db.collection('vote_sessions').document('default_session').update({
            'is_active': True,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        print("✅ Session de vote activée!")
        print("   Les étudiants peuvent maintenant se connecter et voter.")
        
    except Exception as e:
        print(f"❌ Erreur activation: {e}")

def main():
    matricule_test = "24-11661"
    
    print("🔍 DIAGNOSTIC COMPLET DE L'ERREUR DE CONNEXION")
    print("=" * 70)
    
    # Vérifier le statut de la session
    check_vote_session_status()
    
    # Vérifier les connexions
    check_firebase_connection()
    check_backend_connection()
    
    # Simuler le processus de connexion
    can_connect = check_student_login_process(matricule_test)
    
    print(f"\n" + "="*70)
    print("📋 DIAGNOSTIC FINAL:")
    print("-" * 30)
    
    if can_connect:
        print("✅ L'étudiant devrait pouvoir se connecter")
        print("   Le problème vient probablement du frontend ou du réseau")
    else:
        print("❌ L'étudiant ne peut pas se connecter")
        print("   Problème identifié dans le processus de validation")
    
    print(f"\n💡 SOLUTION RECOMMANDÉE:")
    print("-" * 30)
    print("1. Activer la session de vote si elle est inactive")
    print("2. Vérifier la connexion réseau")
    print("3. Redémarrer le backend Flask")
    print("4. Vérifier les logs du frontend")
    
    # Demander si on veut activer la session
    response = input(f"\nVoulez-vous activer la session de vote? (oui/non): ").lower().strip()
    if response in ['oui', 'o', 'yes', 'y']:
        activate_vote_session()

if __name__ == "__main__":
    main() 