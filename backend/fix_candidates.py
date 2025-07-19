import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def fix_candidates():
    """Vérifier et corriger les candidats existants"""
    candidats_ref = db.collection('candidats')
    
    print("Vérification des candidats existants...")
    
    candidats_docs = candidats_ref.stream()
    for doc in candidats_docs:
        candidat_data = doc.to_dict()
        candidat_id = doc.id
        
        # Vérifier si le champ votes existe
        if 'votes' not in candidat_data:
            print(f"Ajout du champ votes=0 pour candidat {candidat_id}")
            candidats_ref.document(candidat_id).update({'votes': 0})
        else:
            print(f"Candidat {candidat_id}: {candidat_data.get('nom')} {candidat_data.get('prenom')} - Votes: {candidat_data.get('votes', 0)}")
    
    print("\nVérification terminée!")

if __name__ == "__main__":
    fix_candidates() 