import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Collections Firestore
etudiants_ref = db.collection('etudiants')
candidats_ref = db.collection('candidats')

def get_all_students():
    """Récupérer tous les étudiants"""
    students = []
    etudiants_docs = etudiants_ref.stream()
    
    for doc in etudiants_docs:
        student_data = doc.to_dict()
        students.append({
            'id': doc.id,
            'matricule': student_data.get('matricule'),
            'nom': student_data.get('nom'),
            'prenom': student_data.get('prenom'),
            'filiere': student_data.get('filiere'),
            'numero': student_data.get('numero', '')
        })
    
    # Trier par numéro
    students.sort(key=lambda x: int(x['numero']) if x['numero'].isdigit() else 999)
    return students

def create_candidates():
    """Créer des candidats à partir des étudiants"""
    print("🎯 Création des candidats")
    print("=" * 50)
    
    # Récupérer tous les étudiants
    students = get_all_students()
    
    if not students:
        print("❌ Aucun étudiant trouvé dans la base de données")
        print("💡 Importez d'abord les étudiants avec: python import_all_students.py")
        return
    
    print(f"📊 {len(students)} étudiants trouvés")
    
    # Afficher la liste des étudiants (premiers 20)
    print("\n📋 Liste des étudiants disponibles (premiers 20):")
    print("-" * 60)
    for i, student in enumerate(students[:20], 1):
        print(f"{i:3d}. N°{student['numero']} - {student['matricule']} - {student['nom']} {student['prenom']} ({student['filiere']})")
    
    if len(students) > 20:
        print(f"... et {len(students) - 20} autres étudiants")
    
    # Demander quels étudiants seront candidats
    print(f"\n🎯 Sélectionnez les candidats (numéros séparés par des virgules)")
    print("Exemple: 1,3,5,7,10,15")
    print("Ou entrez 'auto' pour sélectionner automatiquement les 5 premiers")
    
    try:
        selection = input("Numéros des candidats (ou 'auto'): ").strip()
        
        if selection.lower() == 'auto':
            # Sélectionner automatiquement les 5 premiers
            selected_indices = list(range(5))
            print("✅ Sélection automatique des 5 premiers étudiants")
        else:
            selected_indices = [int(x.strip()) - 1 for x in selection.split(',')]
        
        # Vérifier que les indices sont valides
        for idx in selected_indices:
            if idx < 0 or idx >= len(students):
                print(f"❌ Index invalide: {idx + 1}")
                return
        
        # Créer les candidats
        candidates = []
        for idx in selected_indices:
            student = students[idx]
            candidates.append(student)
        
        print(f"\n✅ {len(candidates)} candidats sélectionnés:")
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. N°{candidate['numero']} - {candidate['nom']} {candidate['prenom']} ({candidate['matricule']})")
        
        # Demander confirmation
        response = input("\nVoulez-vous créer ces candidats? (oui/non): ").lower().strip()
        
        if response not in ['oui', 'o', 'yes', 'y']:
            print("❌ Opération annulée")
            return
        
        # Insérer les candidats dans Firestore
        print("\n📝 Création des candidats...")
        
        for i, candidate in enumerate(candidates, 1):
            try:
                # Créer un ID unique pour le candidat
                candidat_id = f"candidat_{candidate['matricule']}"
                
                # Générer une photo par défaut
                photo_url = f"https://ui-avatars.com/api/?name={candidate['prenom']}+{candidate['nom']}&background=2563eb&color=fff&size=120&font-size=0.4&bold=true"
                
                candidats_ref.document(candidat_id).set({
                    'id': candidat_id,
                    'matricule': candidate['matricule'],
                    'nom': candidate['nom'],
                    'prenom': candidate['prenom'],
                    'filiere': candidate['filiere'],
                    'photo': photo_url,
                    'votes': 0,
                    'numero': candidate['numero'],
                    'created_at': datetime.now()
                })
                
                print(f"✅ Candidat {i}/{len(candidates)} créé: {candidate['nom']} {candidate['prenom']}")
                
            except Exception as e:
                print(f"❌ Erreur lors de la création du candidat {candidate['nom']}: {e}")
        
        print(f"\n🎉 {len(candidates)} candidats créés avec succès!")
        print("\n📝 Prochaines étapes:")
        print("1. Connectez-vous en tant qu'admin: http://localhost:3000/admin/login")
        print("2. Créez une session de vote")
        print("3. Les étudiants pourront voter pour les candidats")
        
    except ValueError:
        print("❌ Format invalide. Utilisez des numéros séparés par des virgules.")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def list_candidates():
    """Lister les candidats existants"""
    print("📋 Candidats existants:")
    print("-" * 50)
    
    candidats = candidats_ref.stream()
    count = 0
    
    for candidat in candidats:
        count += 1
        data = candidat.to_dict()
        print(f"{count}. N°{data.get('numero', 'N/A')} - {data['nom']} {data['prenom']} ({data['matricule']}) - {data.get('votes', 0)} votes")
    
    if count == 0:
        print("Aucun candidat trouvé")
    else:
        print(f"\nTotal: {count} candidat(s)")

def list_students():
    """Lister tous les étudiants"""
    print("📋 Tous les étudiants:")
    print("-" * 50)
    
    students = get_all_students()
    for i, student in enumerate(students, 1):
        print(f"{i:3d}. N°{student['numero']} - {student['matricule']} - {student['nom']} {student['prenom']} ({student['filiere']})")
    
    print(f"\nTotal: {len(students)} étudiant(s)")

if __name__ == "__main__":
    print("🎯 Gestion des candidats")
    print("=" * 30)
    print("1. Créer de nouveaux candidats")
    print("2. Lister les candidats existants")
    print("3. Lister tous les étudiants")
    
    choice = input("\nVotre choix (1, 2 ou 3): ").strip()
    
    if choice == "1":
        create_candidates()
    elif choice == "2":
        list_candidates()
    elif choice == "3":
        list_students()
    else:
        print("❌ Choix invalide") 