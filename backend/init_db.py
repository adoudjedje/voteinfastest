import firebase_admin
from firebase_admin import credentials, firestore
import os

# Configuration Firebase
# Remplacez le chemin par votre fichier de clé Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def init_database():
    """Initialiser la base de données avec des données d'exemple"""
    
    # Collection étudiants
    etudiants_ref = db.collection('etudiants')
    
    # Données d'exemple pour les étudiants
    etudiants_data = [
        {
            'matricule': '2024001',
            'nom': 'Kouadio',
            'prenom': 'Jean',
            'filiere': 'PGP'
        },
        {
            'matricule': '2024002',
            'nom': 'Traoré',
            'prenom': 'Awa',
            'filiere': 'PGP'
        },
        {
            'matricule': '2024003',
            'nom': 'Koné',
            'prenom': 'Moussa',
            'filiere': 'PGP'
        },
        {
            'matricule': '2024004',
            'nom': 'Ouattara',
            'prenom': 'Fatou',
            'filiere': 'PGP'
        },
        {
            'matricule': '2024005',
            'nom': 'Bamba',
            'prenom': 'Kouassi',
            'filiere': 'PGP'
        }
    ]
    
    # Ajouter les étudiants
    for etudiant in etudiants_data:
        etudiants_ref.document(etudiant['matricule']).set({
            'nom': etudiant['nom'],
            'prenom': etudiant['prenom'],
            'filiere': etudiant['filiere']
        })
        print(f"Étudiant ajouté: {etudiant['prenom']} {etudiant['nom']}")
    
    # Collection candidats
    candidats_ref = db.collection('candidats')
    
    # Données d'exemple pour les candidats
    candidats_data = [
        {
            'id': '1',
            'nom': 'Traoré',
            'prenom': 'Awa',
            'filiere': 'PGP'
        },
        {
            'id': '2',
            'nom': 'Koné',
            'prenom': 'Moussa',
            'filiere': 'PGP'
        },
        {
            'id': '3',
            'nom': 'Ouattara',
            'prenom': 'Fatou',
            'filiere': 'PGP'
        }
    ]
    
    # Ajouter les candidats
    for candidat in candidats_data:
        candidats_ref.document(candidat['id']).set({
            'nom': candidat['nom'],
            'prenom': candidat['prenom'],
            'filiere': candidat['filiere'],
            'votes': 0,
            'photo': f"https://ui-avatars.com/api/?name={candidat['prenom']}+{candidat['nom']}&background=28a745&color=fff&size=200&font-size=0.4&bold=true"
        })
        print(f"Candidat ajouté: {candidat['prenom']} {candidat['nom']}")
    
    candidats_ref.document('1').set({
        'nom': 'Traoré',
        'prenom': 'Awa',
        'filiere': 'PGP',
        'votes': 0
    })
    candidats_ref.document('2').set({
        'nom': 'Koné',
        'prenom': 'Moussa',
        'filiere': 'PGP',
        'votes': 0
    })
    candidats_ref.document('3').set({
        'nom': 'Ouattara',
        'prenom': 'Fatou',
        'filiere': 'PGP',
        'votes': 0
    })
    candidats_ref.document('4').set({
        'nom': 'Adou',
        'prenom': 'Meledje',
        'filiere': 'PGP',
        'votes': 0
    })

    print("\nBase de données initialisée avec succès!")
    print("\nMatricules de test:")
    for etudiant in etudiants_data:
        print(f"- {etudiant['matricule']} ({etudiant['prenom']} {etudiant['nom']})")

if __name__ == "__main__":
    init_database() 