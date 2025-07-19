import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_all_students():
    """Récupérer tous les étudiants"""
    students = []
    etudiants = db.collection('etudiants').stream()
    for etudiant in etudiants:
        data = etudiant.to_dict()
        students.append(data)
    return students

def verify_import():
    """Vérifier l'import complet"""
    print("🔍 VÉRIFICATION FINALE DE L'IMPORT")
    print("=" * 60)
    
    # Récupérer tous les étudiants
    students = get_all_students()
    
    print(f"📊 Total d'étudiants en base: {len(students)}")
    print(f"🎯 Objectif: 276 étudiants")
    print(f"📈 Progression: {len(students)}/276 ({len(students)/276*100:.1f}%)")
    
    if len(students) == 276:
        print("\n🎉 SUCCÈS: Tous les 276 étudiants ont été importés!")
        print("✅ Import terminé avec succès!")
    else:
        print(f"\n⚠️  Il manque encore {276 - len(students)} étudiants")
        
        # Analyser les numéros manquants
        existing_numbers = set()
        for student in students:
            numero = int(student.get('numero', 0))
            if numero > 0:
                existing_numbers.add(numero)
        
        all_numbers = set(range(1, 277))
        missing_numbers = all_numbers - existing_numbers
        
        if missing_numbers:
            print(f"Numéros manquants: {sorted(list(missing_numbers))}")
    
    # Afficher quelques statistiques
    print(f"\n📋 STATISTIQUES:")
    print("-" * 30)
    
    # Compter par filière
    filieres = {}
    for student in students:
        filiere = student.get('filiere', 'Inconnue')
        filieres[filiere] = filieres.get(filiere, 0) + 1
    
    for filiere, count in filieres.items():
        print(f"  {filiere}: {count} étudiants")
    
    # Afficher quelques exemples d'étudiants
    print(f"\n📋 Exemples d'étudiants importés:")
    print("-" * 50)
    
    for i, student in enumerate(students[:10], 1):
        numero = student.get('numero', 'N/A')
        matricule = student.get('matricule', 'N/A')
        nom = student.get('nom', 'N/A')
        prenom = student.get('prenom', 'N/A')
        print(f"  {i:2d}. N°{numero} - {matricule} - {nom} {prenom}")
    
    if len(students) > 10:
        print(f"  ... et {len(students) - 10} autres étudiants")
    
    return len(students)

def main():
    total_students = verify_import()
    
    print(f"\n{'='*60}")
    if total_students == 276:
        print("🎉 MISSION ACCOMPLIE!")
        print("✅ Tous les 276 étudiants de la liste PGPA ont été importés avec succès!")
        print("✅ La base de données est maintenant complète et prête pour le système de vote!")
    else:
        print(f"⚠️  Import partiel: {total_students}/276 étudiants")
        print("📝 Il reste quelques étudiants à ajouter manuellement si nécessaire.")

if __name__ == "__main__":
    main() 