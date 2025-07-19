import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def init_votes():
    """Initialiser la collection 'votes' avec des exemples de votes"""
    votes_ref = db.collection('votes')

    # Exemples de votes (matricule -> candidat_id)
    votes_data = [
        {
            'matricule': '2024001',
            'candidat_id': '1',
            'timestamp': datetime.now()
        },
        {
            'matricule': '2024002',
            'candidat_id': '2',
            'timestamp': datetime.now()
        },
        {
            'matricule': '2024003',
            'candidat_id': '3',
            'timestamp': datetime.now()
        }
    ]

    for vote in votes_data:
        votes_ref.document(vote['matricule']).set({
            'candidat_id': vote['candidat_id'],
            'matricule': vote['matricule'],
            'timestamp': vote['timestamp']
        })
        print(f"Vote ajouté: matricule {vote['matricule']} pour candidat {vote['candidat_id']}")

    print("\nVotes initialisés avec succès!")

if __name__ == "__main__":
    init_votes() 