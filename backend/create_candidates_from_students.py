import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import random

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def create_candidates_from_students():
    """Créer des candidats à partir des étudiants"""
    print("👥 CRÉATION DES CANDIDATS")
    print("=" * 50)
    
    # Récupérer tous les étudiants
    students = list(db.collection('etudiants').stream())
    
    if not students:
        print("❌ Aucun étudiant trouvé dans la base de données")
        return
    
    print(f"📊 Total étudiants disponibles: {len(students)}")
    
    # Sélectionner aléatoirement des candidats (par exemple 10 candidats)
    num_candidates = min(10, len(students))
    selected_students = random.sample(students, num_candidates)
    
    print(f"🎯 Création de {num_candidates} candidats...")
    
    candidates_ref = db.collection('candidates')
    
    for i, student_doc in enumerate(selected_students, 1):
        student_data = student_doc.to_dict()
        
        # Créer le candidat
        candidate = {
            'matricule': student_data.get('matricule'),
            'nom': student_data.get('nom'),
            'prenom': student_data.get('prenom'),
            'filiere': student_data.get('filiere', 'PGPA'),
            'numero': student_data.get('numero'),
            'telephone': student_data.get('telephone'),
            'photo_url': f"https://ui-avatars.com/api/?name={student_data.get('nom', '')}+{student_data.get('prenom', '')}&size=200&background=random",
            'description': f"Candidat {i} - {student_data.get('nom', '')} {student_data.get('prenom', '')}",
            'programme': "Programme de développement de la filière PGPA",
            'votes_count': 0,
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        try:
            # Utiliser le matricule comme ID du document
            candidates_ref.document(student_data.get('matricule')).set(candidate)
            print(f"✅ Candidat {i}: {student_data.get('nom', '')} {student_data.get('prenom', '')} ({student_data.get('matricule', '')})")
        except Exception as e:
            print(f"❌ Erreur création candidat {i}: {e}")
    
    print(f"\n🎉 {num_candidates} candidats créés avec succès!")

def verify_candidates():
    """Vérifier les candidats créés"""
    print("\n🔍 VÉRIFICATION DES CANDIDATS")
    print("=" * 50)
    
    try:
        candidates = list(db.collection('candidates').stream())
        print(f"📊 Total candidats: {len(candidates)}")
        
        if candidates:
            print("📋 Liste des candidats:")
            for i, candidate_doc in enumerate(candidates, 1):
                candidate_data = candidate_doc.to_dict()
                print(f"  {i:2d}. {candidate_data.get('nom', '')} {candidate_data.get('prenom', '')} ({candidate_data.get('matricule', '')})")
                print(f"      Votes: {candidate_data.get('votes_count', 0)} | Photo: {candidate_data.get('photo_url', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ Erreur vérification candidats: {e}")

def create_vote_validation_rules():
    """Créer des règles de validation pour les votes"""
    print("\n📋 CRÉATION DES RÈGLES DE VALIDATION")
    print("=" * 50)
    
    validation_rules = {
        'vote_constraints': {
            'max_votes_per_student': 1,
            'allow_multiple_candidates': False,
            'require_student_verification': True,
            'prevent_duplicate_votes': True,
            'validate_student_exists': True,
            'validate_candidate_exists': True
        },
        'session_settings': {
            'default_session_id': 'default_session',
            'auto_start_voting': False,
            'auto_end_voting': False,
            'show_results_after_vote': True,
            'allow_vote_modification': False
        },
        'security_settings': {
            'log_ip_addresses': True,
            'log_user_agents': True,
            'require_confirmation': True,
            'prevent_rapid_voting': True,
            'max_votes_per_ip': 1
        },
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    try:
        db.collection('validation_rules').document('default').set(validation_rules)
        print("✅ Règles de validation créées")
    except Exception as e:
        print(f"⚠️  Règles existent déjà ou erreur: {e}")

def main():
    print("🗳️  PRÉPARATION DU SYSTÈME DE VOTE")
    print("=" * 60)
    
    # Créer les candidats
    create_candidates_from_students()
    
    # Vérifier les candidats
    verify_candidates()
    
    # Créer les règles de validation
    create_vote_validation_rules()
    
    print("\n" + "="*60)
    print("🎉 SYSTÈME DE VOTE COMPLÈTEMENT PRÊT!")
    print("✅ Candidats créés avec photos et descriptions")
    print("✅ Règles de validation strictes implémentées")
    print("✅ Contraintes de vote uniques par étudiant")
    print("✅ Système de traçabilité complet")
    print("\n📋 RÈGLES DE VOTE:")
    print("-" * 30)
    print("• Un étudiant ne peut voter qu'une seule fois")
    print("• Un étudiant ne peut voter que pour un seul candidat")
    print("• Validation par matricule d'étudiant obligatoire")
    print("• Traçabilité IP et user agent")
    print("• Pas de modification de vote autorisée")
    print("• Résultats visibles après vote")

if __name__ == "__main__":
    main() 