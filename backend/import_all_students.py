import firebase_admin
from firebase_admin import credentials, firestore
import PyPDF2
import re
from datetime import datetime

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Collections Firestore
etudiants_ref = db.collection('etudiants')
candidats_ref = db.collection('candidats')
votes_ref = db.collection('votes')
sessions_ref = db.collection('sessions')

def extract_text_from_pdf(pdf_path):
    """Extraire le texte du PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Erreur lors de la lecture du PDF: {e}")
        return None

def parse_student_data(text):
    """Parser les données des étudiants depuis le texte extrait"""
    students = []
    
    lines = text.split('\n')
    
    for line in lines:
        # Nettoyer la ligne
        line = line.strip()
        if not line:
            continue
        
        # Chercher les patterns de matricule avec PGPA
        pgpa_pattern = r'(\d{1,3})?(\d{2}[P-]?\d{4,5}PGPA[A-Z]+)'
        matches = re.findall(pgpa_pattern, line)
        
        for match in matches:
            try:
                numero_part, matricule_full = match
                
                # Si le numéro est vide, essayer de l'extraire du début de la ligne
                if not numero_part:
                    # Chercher un numéro au début de la ligne
                    numero_match = re.match(r'(\d{1,3})', line)
                    if numero_match:
                        numero_part = numero_match.group(1)
                    else:
                        continue
                
                numero = numero_part
                
                # Vérifier si le numéro est valide (1-276)
                if not numero.isdigit() or int(numero) <= 0 or int(numero) > 276:
                    continue
                
                # Extraire le téléphone (dernier groupe de chiffres)
                telephone_match = re.search(r'(\d{10,11}(?:/\d{10,11})?)$', line)
                if not telephone_match:
                    continue
                
                telephone = telephone_match.group(1)
                
                # Extraire le nom/prénom entre le matricule et le téléphone
                start_pos = line.find(matricule_full) + len(matricule_full)
                end_pos = line.find(telephone)
                
                if start_pos >= end_pos:
                    continue
                
                nom_prenom = line[start_pos:end_pos].strip()
                
                # Extraire le matricule simple (avant PGPA)
                if 'PGPA' in matricule_full:
                    matricule_simple = matricule_full.split('PGPA')[0]
                else:
                    matricule_simple = matricule_full
                
                # Séparer nom et prénom intelligemment
                nom_prenom_clean = nom_prenom.strip()
                
                # Si c'est un seul mot, c'est le prénom
                if ' ' not in nom_prenom_clean:
                    nom = ""
                    prenom = nom_prenom_clean
                else:
                    # Essayer de séparer intelligemment
                    name_parts = nom_prenom_clean.split()
                    if len(name_parts) >= 2:
                        # Le dernier mot est généralement le prénom
                        prenom = name_parts[-1]
                        nom = ' '.join(name_parts[:-1])
                    else:
                        # Un seul mot, c'est le prénom
                        nom = ""
                        prenom = name_parts[0]
                
                students.append({
                    'matricule': matricule_simple,
                    'nom': nom.strip(),
                    'prenom': prenom.strip(),
                    'filiere': 'PGPA',
                    'telephone': telephone,
                    'matricule_complet': matricule_full,
                    'numero': numero,
                    'nom_complet': nom_prenom_clean
                })
                
                # Ne traiter que le premier match par ligne
                break
                
            except Exception as e:
                print(f"⚠️  Erreur parsing ligne '{line}': {e}")
                continue
    
    return students

def clear_database():
    """Supprimer toutes les données existantes"""
    print("🗑️  Suppression complète de la base de données...")
    
    # Supprimer tous les étudiants
    etudiants = etudiants_ref.stream()
    count_etudiants = 0
    for etudiant in etudiants:
        etudiant.reference.delete()
        count_etudiants += 1
    print(f"✅ {count_etudiants} étudiants supprimés")
    
    # Supprimer tous les candidats
    candidats = candidats_ref.stream()
    count_candidats = 0
    for candidat in candidats:
        candidat.reference.delete()
        count_candidats += 1
    print(f"✅ {count_candidats} candidats supprimés")
    
    # Supprimer tous les votes
    votes = votes_ref.stream()
    count_votes = 0
    for vote in votes:
        vote.reference.delete()
        count_votes += 1
    print(f"✅ {count_votes} votes supprimés")
    
    # Supprimer toutes les sessions
    sessions = sessions_ref.stream()
    count_sessions = 0
    for session in sessions:
        session.reference.delete()
        count_sessions += 1
    print(f"✅ {count_sessions} sessions supprimées")
    
    print("✅ Base de données complètement vidée")

def insert_students(students):
    """Insérer les étudiants dans Firestore"""
    print(f"📝 Insertion de {len(students)} étudiants...")
    
    for i, student in enumerate(students, 1):
        try:
            # Créer le document avec le matricule comme ID
            etudiants_ref.document(student['matricule']).set({
                'matricule': student['matricule'],
                'nom': student['nom'],
                'prenom': student['prenom'],
                'filiere': student['filiere'],
                'telephone': student.get('telephone', ''),
                'matricule_complet': student.get('matricule_complet', ''),
                'numero': student.get('numero', ''),
                'nom_complet': student.get('nom_complet', ''),
                'created_at': datetime.now()
            })
            
            if i % 20 == 0:  # Afficher le progrès tous les 20 étudiants
                print(f"   {i}/{len(students)} étudiants insérés...")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de {student['matricule']}: {e}")
    
    print(f"✅ {len(students)} étudiants insérés avec succès")

def main():
    """Fonction principale"""
    print("🎓 Import complet des étudiants depuis le PDF")
    print("=" * 60)
    
    # Chemin vers le PDF
    pdf_path = "../LISTE DEFINITIVE LICENCE 1 PGPA 2025_011511(1).pdf"
    
    # Extraire le texte du PDF
    print("📄 Extraction du texte du PDF...")
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print("❌ Impossible d'extraire le texte du PDF")
        return
    
    print("✅ Texte extrait avec succès")
    
    # Parser les données des étudiants
    print("🔍 Analyse des données des étudiants...")
    students = parse_student_data(text)
    
    if not students:
        print("❌ Aucun étudiant trouvé dans le PDF")
        return
    
    print(f"✅ {len(students)} étudiants trouvés")
    
    # Vérifier que nous avons bien tous les étudiants (1-276)
    numeros_trouves = [int(s['numero']) for s in students]
    numeros_manquants = [i for i in range(1, 277) if i not in numeros_trouves]
    
    if numeros_manquants:
        print(f"⚠️  Attention: {len(numeros_manquants)} étudiants manquants")
        print(f"   Numéros manquants: {numeros_manquants[:10]}{'...' if len(numeros_manquants) > 10 else ''}")
    
    # Afficher un aperçu des données
    print("\n📋 Aperçu des données:")
    print("-" * 60)
    for i, student in enumerate(students[:10], 1):
        print(f"{i:2d}. N°{student.get('numero', 'N/A')} - {student['matricule']} - {student['nom']} {student['prenom']} ({student['filiere']})")
        print(f"     Téléphone: {student.get('telephone', 'N/A')}")
    
    if len(students) > 10:
        print(f"... et {len(students) - 10} autres étudiants")
    
    # Demander confirmation
    print(f"\n⚠️  ATTENTION: Cette opération va supprimer TOUTES les données existantes!")
    print(f"📊 {len(students)} étudiants seront importés")
    response = input("Voulez-vous continuer? (oui/non): ").lower().strip()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return
    
    # Supprimer les données existantes
    clear_database()
    
    # Insérer les nouveaux étudiants
    insert_students(students)
    
    print("\n🎉 Import terminé avec succès!")
    print(f"📊 {len(students)} étudiants importés dans la base de données")
    print(f"🎯 Filière: PGPA")
    print("\n📝 Prochaines étapes:")
    print("1. Créez des candidats avec: python create_candidates.py")
    print("2. Connectez-vous en tant qu'admin: http://localhost:3000/admin/login")
    print("3. Créez une session de vote")

if __name__ == "__main__":
    main() 