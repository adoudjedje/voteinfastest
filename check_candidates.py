import sys
import os
sys.path.append('backend')

import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("backend/firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def check_candidates():
    """Vérifier les candidats dans la base de données"""
    try:
        candidats_ref = db.collection('candidats')
        candidats = list(candidats_ref.stream())
        
        print(f"📊 NOMBRE DE CANDIDATS: {len(candidats)}")
        print()
        
        if len(candidats) == 0:
            print("❌ AUCUN CANDIDAT TROUVÉ!")
            print("   Vous devez créer des candidats avant de pouvoir voter.")
            print("   Utilisez le script create_candidates.py pour en créer.")
        else:
            print("✅ CANDIDATS DISPONIBLES:")
            for i, candidat in enumerate(candidats, 1):
                data = candidat.to_dict()
                print(f"   {i}. {data.get('prenom', '')} {data.get('nom', '')} - {data.get('filiere', '')}")
        
        print()
        
        # Vérifier aussi les étudiants
        etudiants_ref = db.collection('etudiants')
        etudiants = list(etudiants_ref.stream())
        print(f"👥 NOMBRE D'ÉTUDIANTS: {len(etudiants)}")
        
        if len(etudiants) == 0:
            print("❌ AUCUN ÉTUDIANT TROUVÉ!")
            print("   Vous devez importer les étudiants avant de pouvoir voter.")
        else:
            print("✅ ÉTUDIANTS DISPONIBLES")
            print(f"   Exemple de matricule: {etudiants[0].id}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_candidates() 