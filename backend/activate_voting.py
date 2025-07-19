import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def activate_voting():
    """Activer la session de vote"""
    try:
        # Activer la session
        db.collection('vote_sessions').document('default_session').update({
            'is_active': True,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        print("✅ SESSION DE VOTE ACTIVÉE!")
        print("   Les étudiants peuvent maintenant se connecter et voter.")
        print("   L'erreur 'Erreur de connexion' devrait disparaître.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    activate_voting() 