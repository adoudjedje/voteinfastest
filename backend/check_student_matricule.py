import firebase_admin
from firebase_admin import credentials, firestore

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def check_matricule(matricule):
    """Vérifier si un matricule existe dans la base de données"""
    print(f"🔍 VÉRIFICATION DU MATRICULE: {matricule}")
    print("=" * 50)
    
    try:
        # Chercher l'étudiant par matricule
        student_doc = db.collection('etudiants').document(matricule).get()
        
        if student_doc.exists:
            student_data = student_doc.to_dict()
            print("✅ MATRICULE TROUVÉ!")
            print(f"  Nom: {student_data.get('nom', 'N/A')}")
            print(f"  Prénom: {student_data.get('prenom', 'N/A')}")
            print(f"  Filière: {student_data.get('filiere', 'N/A')}")
            print(f"  Numéro: {student_data.get('numero', 'N/A')}")
            print(f"  Téléphone: {student_data.get('telephone', 'N/A')}")
            return True
        else:
            print("❌ MATRICULE NON TROUVÉ!")
            print(f"Le matricule '{matricule}' n'existe pas dans la base de données.")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

def search_similar_matricules(matricule):
    """Chercher des matricules similaires"""
    print(f"\n🔍 RECHERCHE DE MATRICULES SIMILAIRES")
    print("-" * 40)
    
    try:
        # Récupérer tous les étudiants
        students = list(db.collection('etudiants').stream())
        
        # Chercher des matricules similaires
        similar_matricules = []
        for student_doc in students:
            student_data = student_doc.to_dict()
            student_matricule = student_data.get('matricule', '')
            
            # Vérifier si le matricule contient la recherche
            if matricule in student_matricule or student_matricule in matricule:
                similar_matricules.append({
                    'matricule': student_matricule,
                    'nom': student_data.get('nom', ''),
                    'prenom': student_data.get('prenom', ''),
                    'numero': student_data.get('numero', '')
                })
        
        if similar_matricules:
            print(f"Matricules similaires trouvés ({len(similar_matricules)}):")
            for i, similar in enumerate(similar_matricules[:10], 1):
                print(f"  {i}. {similar['matricule']} - {similar['nom']} {similar['prenom']} (N°{similar['numero']})")
        else:
            print("Aucun matricule similaire trouvé.")
            
    except Exception as e:
        print(f"❌ Erreur recherche: {e}")

def check_vote_status(matricule):
    """Vérifier le statut de vote d'un étudiant"""
    print(f"\n🗳️  STATUT DE VOTE POUR {matricule}")
    print("-" * 40)
    
    try:
        # Chercher les votes de cet étudiant
        votes = db.collection('votes').where('student_matricule', '==', matricule).stream()
        vote_list = list(votes)
        
        if vote_list:
            print(f"Votes trouvés: {len(vote_list)}")
            for i, vote_doc in enumerate(vote_list, 1):
                vote_data = vote_doc.to_dict()
                print(f"  Vote {i}:")
                print(f"    Candidat: {vote_data.get('candidate_matricule', 'N/A')}")
                print(f"    Session: {vote_data.get('session_id', 'N/A')}")
                print(f"    Valide: {vote_data.get('is_valid', 'N/A')}")
                print(f"    Date: {vote_data.get('vote_timestamp', 'N/A')}")
        else:
            print("Aucun vote trouvé pour cet étudiant.")
            
    except Exception as e:
        print(f"❌ Erreur vérification vote: {e}")

def main():
    matricule_to_check = "24-11661"
    
    print("🔍 DIAGNOSTIC D'ERREUR DE CONNEXION")
    print("=" * 60)
    
    # Vérifier le matricule
    exists = check_matricule(matricule_to_check)
    
    if not exists:
        # Chercher des matricules similaires
        search_similar_matricules(matricule_to_check)
    
    # Vérifier le statut de vote
    check_vote_status(matricule_to_check)
    
    print(f"\n" + "="*60)
    print("📋 CAUSES POSSIBLES DE L'ERREUR:")
    print("-" * 40)
    print("1. ❌ Matricule inexistant dans la base de données")
    print("2. ❌ Erreur de saisie (chiffres/lettres inversés)")
    print("3. ❌ Problème de connexion à Firebase")
    print("4. ❌ Session de vote inactive")
    print("5. ❌ Étudiant déjà voté")
    
    print(f"\n💡 SOLUTIONS:")
    print("-" * 20)
    print("• Vérifier l'orthographe du matricule")
    print("• Consulter la liste des matricules valides")
    print("• Vérifier la connexion internet")
    print("• Contacter l'administrateur si le problème persiste")

if __name__ == "__main__":
    main() 