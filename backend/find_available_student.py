import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def find_available_students():
    """Trouver des étudiants qui n'ont pas encore voté"""
    print("🔍 RECHERCHE D'ÉTUDIANTS DISPONIBLES POUR TEST")
    print("=" * 60)
    
    try:
        # Récupérer tous les étudiants
        students = list(db.collection('etudiants').stream())
        
        # Récupérer tous les votes valides
        valid_votes = db.collection('votes').where('is_valid', '==', True).stream()
        voted_matricules = [vote.to_dict()['student_matricule'] for vote in valid_votes]
        
        # Trouver les étudiants qui n'ont pas voté
        available_students = []
        for student_doc in students:
            student_data = student_doc.to_dict()
            matricule = student_data.get('matricule', '')
            
            if matricule not in voted_matricules:
                available_students.append({
                    'matricule': matricule,
                    'nom': student_data.get('nom', ''),
                    'prenom': student_data.get('prenom', ''),
                    'numero': student_data.get('numero', ''),
                    'telephone': student_data.get('telephone', '')
                })
        
        print(f"📊 STATISTIQUES:")
        print(f"   Total étudiants: {len(students)}")
        print(f"   Étudiants ayant voté: {len(voted_matricules)}")
        print(f"   Étudiants disponibles: {len(available_students)}")
        print(f"   Taux de participation: {(len(voted_matricules)/len(students))*100:.1f}%")
        
        print(f"\n🎯 ÉTUDIANTS DISPONIBLES POUR TEST (premiers 10):")
        print("-" * 50)
        
        for i, student in enumerate(available_students[:10], 1):
            print(f"{i:2d}. {student['matricule']} - {student['nom']} {student['prenom']} (N°{student['numero']})")
            print(f"     Tél: {student['telephone']}")
        
        if len(available_students) > 10:
            print(f"     ... et {len(available_students) - 10} autres étudiants")
        
        print(f"\n💡 RECOMMANDATIONS POUR TEST:")
        print("-" * 40)
        print("• Utilisez un des matricules ci-dessus pour tester")
        print("• Ces étudiants n'ont pas encore voté")
        print("• Ils devraient pouvoir se connecter sans erreur")
        
        return available_students
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def main():
    available_students = find_available_students()
    
    if available_students:
        print(f"\n" + "="*60)
        print("✅ DIAGNOSTIC TERMINÉ")
        print("   Utilisez un des matricules disponibles pour tester!")

if __name__ == "__main__":
    main() 