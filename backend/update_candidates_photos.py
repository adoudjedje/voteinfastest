import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def update_candidates_photos():
    """Ajouter des photos aux candidats existants"""
    candidats_ref = db.collection('candidats')
    
    print("Mise à jour des photos des candidats...")
    
    candidats_docs = candidats_ref.stream()
    for doc in candidats_docs:
        candidat_data = doc.to_dict()
        candidat_id = doc.id
        
        # Vérifier si le champ photo existe
        if 'photo' not in candidat_data:
            photo_url = f"../src/assets/{candidat_data.get('prenom', '')}+{candidat_data.get('nom', '')}&background=28a745&color=fff&size=200&font-size=0.4&bold=true"
            
            candidats_ref.document(candidat_id).update({
                'photo': photo_url,
                'votes': candidat_data.get('votes', 0)
            })
            
            print(f"Photo ajoutée pour candidat {candidat_id}: {candidat_data.get('prenom')} {candidat_data.get('nom')}")
        else:
            print(f"Candidat {candidat_id}: {candidat_data.get('prenom')} {candidat_data.get('nom')} - Photo déjà présente")
    
    print("\nMise à jour terminée!")

if __name__ == "__main__":
    update_candidates_photos() 