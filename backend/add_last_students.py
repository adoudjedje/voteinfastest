import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def add_last_students():
    """Ajouter les derniers étudiants manquants"""
    
    # Les 4 derniers étudiants manquants
    last_students = [
        {"numero": 23, "matricule": "24-11674", "nom": "AMANVI", "prenom": "ALLOMOUCHRISTINE", "telephone": "0777285206"},
        {"numero": 66, "matricule": "24-11773", "nom": "BROU", "prenom": "YAOYANNALEX", "telephone": "0759445183"},
        {"numero": 67, "matricule": "24-11774", "nom": "CREBIO", "prenom": "GRACEEMMANUELLA", "telephone": "0769617083"},
        {"numero": 249, "matricule": "24-11859", "nom": "TOURE", "prenom": "BASSITAFIDELE", "telephone": "0768555478"},
    ]
    
    print("🔍 Ajout des 4 derniers étudiants manquants")
    print("=" * 50)
    
    added_count = 0
    for i, student in enumerate(last_students, 1):
        try:
            # Vérifier si l'étudiant existe déjà par matricule
            existing = db.collection('etudiants').document(student['matricule']).get()
            if existing.exists:
                print(f"⚠️  {student['matricule']} existe déjà")
                continue
            
            # Ajouter l'étudiant
            db.collection('etudiants').document(student['matricule']).set({
                'matricule': student['matricule'],
                'nom': student['nom'],
                'prenom': student['prenom'],
                'filiere': 'PGPA',
                'telephone': student['telephone'],
                'numero': str(student['numero']),
                'created_at': datetime.now()
            })
            
            print(f"✅ {i}/4 - N°{student['numero']} - {student['matricule']} - {student['nom']} {student['prenom']}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Erreur {student['matricule']}: {e}")
    
    print(f"🎉 {added_count} étudiants ajoutés!")
    return added_count

def main():
    # Ajouter les derniers étudiants
    added_count = add_last_students()
    
    # Vérifier le total final
    final_total = len(list(db.collection('etudiants').stream()))
    print(f"\n📊 Total final: {final_total}/276 étudiants ({final_total/276*100:.1f}%)")
    
    if final_total == 276:
        print("🎉 Tous les 276 étudiants ont été importés avec succès!")
        print("✅ Import terminé avec succès!")
    else:
        print(f"⚠️  Il manque encore {276 - final_total} étudiants")

if __name__ == "__main__":
    main() 