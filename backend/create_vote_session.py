import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def create_active_voting_session():
    """Créer et activer une session de vote"""
    try:
        # Désactiver toutes les sessions existantes
        sessions_ref = db.collection('sessions')
        existing_sessions = sessions_ref.where('isActive', '==', True).stream()
        for session in existing_sessions:
            session.reference.update({'isActive': False})
            print(f"Session {session.id} désactivée")
        
        # Créer une nouvelle session active
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=24)  # Session de 24 heures
        
        session_data = {
            'isActive': True,
            'startTime': start_time,
            'endTime': end_time,
            'duration': 24,  # en heures
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Ajouter la session à Firestore
        sessions_ref.add(session_data)
        
        print("✅ SESSION DE VOTE CRÉÉE ET ACTIVÉE!")
        print(f"   Début: {start_time.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Fin: {end_time.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Durée: 24 heures")
        print("   Les étudiants peuvent maintenant se connecter et voter.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_active_voting_session() 