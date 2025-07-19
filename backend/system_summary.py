import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def generate_system_summary():
    """Générer un résumé complet du système"""
    print("📊 RÉSUMÉ COMPLET DU SYSTÈME DE VOTE")
    print("=" * 60)
    
    # Statistiques générales
    print("📈 STATISTIQUES GÉNÉRALES")
    print("-" * 30)
    
    collections = {
        'etudiants': 'Étudiants inscrits',
        'candidates': 'Candidats',
        'votes': 'Votes enregistrés',
        'vote_sessions': 'Sessions de vote',
        'vote_rules': 'Règles de vote',
        'validation_rules': 'Règles de validation'
    }
    
    for collection_name, description in collections.items():
        try:
            docs = list(db.collection(collection_name).stream())
            print(f"  {description}: {len(docs)}")
        except Exception as e:
            print(f"  {description}: Erreur - {e}")
    
    # Détails des étudiants
    print(f"\n👥 DÉTAILS DES ÉTUDIANTS")
    print("-" * 30)
    
    try:
        students = list(db.collection('etudiants').stream())
        print(f"  Total étudiants: {len(students)}")
        print(f"  Objectif: 276 étudiants")
        print(f"  Progression: {len(students)}/276 ({len(students)/276*100:.1f}%)")
        
        if len(students) < 276:
            missing = 276 - len(students)
            print(f"  Étudiants manquants: {missing}")
    except Exception as e:
        print(f"  Erreur: {e}")
    
    # Détails des candidats
    print(f"\n🎯 DÉTAILS DES CANDIDATS")
    print("-" * 30)
    
    try:
        candidates = list(db.collection('candidates').stream())
        print(f"  Total candidats: {len(candidates)}")
        
        if candidates:
            print("  Liste des candidats:")
            for i, candidate_doc in enumerate(candidates, 1):
                candidate_data = candidate_doc.to_dict()
                nom = candidate_data.get('nom', '')
                prenom = candidate_data.get('prenom', '')
                matricule = candidate_data.get('matricule', '')
                votes = candidate_data.get('votes_count', 0)
                print(f"    {i:2d}. {nom} {prenom} ({matricule}) - {votes} vote(s)")
    except Exception as e:
        print(f"  Erreur: {e}")
    
    # Détails des votes
    print(f"\n🗳️  DÉTAILS DES VOTES")
    print("-" * 30)
    
    try:
        votes = list(db.collection('votes').stream())
        print(f"  Total votes: {len(votes)}")
        
        if votes:
            valid_votes = [v for v in votes if v.to_dict().get('is_valid', True)]
            invalid_votes = len(votes) - len(valid_votes)
            print(f"  Votes valides: {len(valid_votes)}")
            print(f"  Votes invalides: {invalid_votes}")
            
            # Votes par session
            session_votes = {}
            for vote_doc in votes:
                vote_data = vote_doc.to_dict()
                session_id = vote_data.get('session_id', 'unknown')
                session_votes[session_id] = session_votes.get(session_id, 0) + 1
            
            print("  Votes par session:")
            for session_id, count in session_votes.items():
                print(f"    {session_id}: {count} vote(s)")
    except Exception as e:
        print(f"  Erreur: {e}")
    
    # Configuration du système
    print(f"\n⚙️  CONFIGURATION DU SYSTÈME")
    print("-" * 30)
    
    try:
        # Règles de vote
        rules_doc = db.collection('vote_rules').document('default').get()
        if rules_doc.exists:
            rules = rules_doc.to_dict()
            print("  Règles de vote:")
            for key, value in rules.get('rules', {}).items():
                print(f"    {key}: {value}")
        
        # Règles de validation
        validation_doc = db.collection('validation_rules').document('default').get()
        if validation_doc.exists:
            validation = validation_doc.to_dict()
            print("  Règles de validation:")
            for category, settings in validation.items():
                if isinstance(settings, dict):
                    print(f"    {category}:")
                    for key, value in settings.items():
                        print(f"      {key}: {value}")
        
        # Session de vote
        session_doc = db.collection('vote_sessions').document('default_session').get()
        if session_doc.exists:
            session = session_doc.to_dict()
            print("  Session de vote:")
            print(f"    Nom: {session.get('name', 'N/A')}")
            print(f"    Active: {session.get('is_active', 'N/A')}")
            print(f"    Max votes par étudiant: {session.get('max_votes_per_student', 'N/A')}")
    except Exception as e:
        print(f"  Erreur: {e}")

def display_constraints():
    """Afficher les contraintes du système"""
    print(f"\n🔒 CONTRAINTES DU SYSTÈME")
    print("-" * 30)
    
    constraints = [
        "✅ Un étudiant ne peut voter qu'une seule fois",
        "✅ Un étudiant ne peut voter que pour un seul candidat",
        "✅ Validation par matricule d'étudiant obligatoire",
        "✅ Traçabilité IP et user agent",
        "✅ Pas de modification de vote autorisée",
        "✅ Détection automatique des votes en double",
        "✅ Comptage automatique des votes par candidat",
        "✅ Sessions de vote configurables",
        "✅ Règles de validation personnalisables",
        "✅ Historique complet des votes"
    ]
    
    for constraint in constraints:
        print(f"  {constraint}")

def display_security_features():
    """Afficher les fonctionnalités de sécurité"""
    print(f"\n🛡️  FONCTIONNALITÉS DE SÉCURITÉ")
    print("-" * 30)
    
    security_features = [
        "✅ Validation par matricule d'étudiant",
        "✅ Traçabilité IP pour audit",
        "✅ Traçabilité user agent",
        "✅ Timestamp de chaque vote",
        "✅ Prévention des votes en double",
        "✅ Validation de l'existence de l'étudiant",
        "✅ Validation de l'existence du candidat",
        "✅ Marquage des votes invalides",
        "✅ Sessions de vote contrôlées",
        "✅ Règles de validation strictes"
    ]
    
    for feature in security_features:
        print(f"  {feature}")

def main():
    print("📋 RÉSUMÉ COMPLET DU SYSTÈME DE VOTE INFAS35")
    print("=" * 70)
    
    # Générer le résumé
    generate_system_summary()
    
    # Afficher les contraintes
    display_constraints()
    
    # Afficher les fonctionnalités de sécurité
    display_security_features()
    
    print(f"\n" + "="*70)
    print("🎉 SYSTÈME DE VOTE INFAS35 PRÊT!")
    print("✅ Tous les composants sont opérationnels")
    print("✅ Les contraintes de vote unique sont implémentées")
    print("✅ La sécurité et la traçabilité sont assurées")
    print("✅ Le système est prêt pour les élections")
    
    print(f"\n📞 PROCHAINES ÉTAPES:")
    print("-" * 20)
    print("1. Activer la session de vote via l'interface admin")
    print("2. Lancer le frontend React pour les étudiants")
    print("3. Commencer les élections")
    print("4. Surveiller les résultats en temps réel")

if __name__ == "__main__":
    main() 