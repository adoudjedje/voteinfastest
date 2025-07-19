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

def get_existing_students():
    """Récupérer les étudiants existants"""
    existing = set()
    etudiants = etudiants_ref.stream()
    for etudiant in etudiants:
        data = etudiant.to_dict()
        existing.add(int(data.get('numero', 0)))
    return existing

def manual_extract_missing_students(text):
    """Extraction manuelle des étudiants manquants basée sur l'analyse"""
    students = []
    existing_numbers = get_existing_students()
    
    print(f"📊 Étudiants existants: {len(existing_numbers)}")
    print(f"🔍 Extraction manuelle des étudiants manquants...")
    
    lines = text.split('\n')
    
    # Traitement spécifique pour les cas identifiés
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Cas 1: Ligne avec numéro 2 manquant
        if line.startswith('2 24P-0387PGPAABLI'):
            try:
                # Extraire les données manuellement
                parts = line.split()
                numero = "2"
                matricule_full = "24P-0387PGPAABLI"
                telephone = parts[-1]  # Dernier élément
                
                # Extraire le nom/prénom
                start_pos = line.find(matricule_full) + len(matricule_full)
                end_pos = line.find(telephone)
                nom_prenom = line[start_pos:end_pos].strip()
                
                matricule_simple = "24P-0387"
                nom = "ABLI"
                prenom = "BOLOINGRIDROSELINE"
                
                students.append({
                    'matricule': matricule_simple,
                    'nom': nom,
                    'prenom': prenom,
                    'filiere': 'PGPA',
                    'telephone': telephone,
                    'matricule_complet': matricule_full,
                    'numero': numero,
                    'nom_complet': nom_prenom
                })
                
                print(f"✅ Étudiant manquant trouvé: N°{numero} - {nom} {prenom}")
                
            except Exception as e:
                print(f"❌ Erreur ligne {line_num}: {e}")
        
        # Cas 2: Chercher d'autres patterns spécifiques
        # Pattern pour les numéros manquants avec matricule PGPA
        pgpa_pattern = r'(\d{1,3})\s+(\d{2}[P-]?\d{4,5}PGPA[A-Z]+)'
        matches = re.findall(pgpa_pattern, line)
        
        for match in matches:
            try:
                numero_part, matricule_full = match
                numero = int(numero_part)
                
                if numero in existing_numbers or numero <= 0 or numero > 276:
                    continue
                
                # Extraire le téléphone
                telephone_match = re.search(r'(\d{10,11}(?:/\d{10,11})?)$', line)
                if not telephone_match:
                    continue
                
                telephone = telephone_match.group(1)
                
                # Extraire le nom/prénom
                start_pos = line.find(matricule_full) + len(matricule_full)
                end_pos = line.find(telephone)
                
                if start_pos >= end_pos:
                    continue
                
                nom_prenom = line[start_pos:end_pos].strip()
                
                # Extraire le matricule simple
                if 'PGPA' in matricule_full:
                    matricule_simple = matricule_full.split('PGPA')[0]
                else:
                    matricule_simple = matricule_full
                
                # Séparer nom et prénom
                nom_prenom_clean = nom_prenom.strip()
                
                if ' ' not in nom_prenom_clean:
                    nom = ""
                    prenom = nom_prenom_clean
                else:
                    name_parts = nom_prenom_clean.split()
                    if len(name_parts) >= 2:
                        prenom = name_parts[-1]
                        nom = ' '.join(name_parts[:-1])
                    else:
                        nom = ""
                        prenom = name_parts[0]
                
                students.append({
                    'matricule': matricule_simple,
                    'nom': nom.strip(),
                    'prenom': prenom.strip(),
                    'filiere': 'PGPA',
                    'telephone': telephone,
                    'matricule_complet': matricule_full,
                    'numero': str(numero),
                    'nom_complet': nom_prenom_clean
                })
                
                print(f"✅ Étudiant manquant trouvé: N°{numero} - {nom} {prenom}")
                
            except Exception as e:
                continue
    
    return students

def insert_missing_students(students):
    """Insérer les étudiants manquants"""
    if not students:
        print("❌ Aucun étudiant manquant trouvé")
        return
    
    print(f"\n📝 Insertion de {len(students)} étudiants manquants...")
    
    for i, student in enumerate(students, 1):
        try:
            # Vérifier si l'étudiant existe déjà
            existing = etudiants_ref.document(student['matricule']).get()
            if existing.exists:
                print(f"⚠️  Étudiant {student['matricule']} existe déjà")
                continue
            
            # Créer le document
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
            
            print(f"✅ {i}/{len(students)} - N°{student['numero']} - {student['nom']} {student['prenom']}")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de {student['matricule']}: {e}")
    
    print(f"\n🎉 {len(students)} étudiants manquants ajoutés avec succès!")

def main():
    """Fonction principale"""
    print("🔍 Extraction manuelle des étudiants manquants")
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
    
    # Parser les étudiants manquants
    missing_students = manual_extract_missing_students(text)
    
    if not missing_students:
        print("❌ Aucun étudiant manquant trouvé")
        return
    
    print(f"\n📊 {len(missing_students)} étudiants manquants identifiés")
    
    # Afficher un aperçu
    print("\n📋 Aperçu des étudiants manquants:")
    print("-" * 60)
    for i, student in enumerate(missing_students[:10], 1):
        print(f"{i:2d}. N°{student['numero']} - {student['matricule']} - {student['nom']} {student['prenom']} ({student['filiere']})")
        print(f"     Téléphone: {student.get('telephone', 'N/A')}")
    
    if len(missing_students) > 10:
        print(f"... et {len(missing_students) - 10} autres étudiants")
    
    # Demander confirmation
    response = input(f"\nVoulez-vous ajouter ces {len(missing_students)} étudiants? (oui/non): ").lower().strip()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return
    
    # Insérer les étudiants manquants
    insert_missing_students(missing_students)
    
    # Vérifier le total final
    total_etudiants = len(list(etudiants_ref.stream()))
    print(f"\n📊 Total final: {total_etudiants} étudiants dans la base de données")
    print(f"🎯 Objectif: 276 étudiants")
    print(f"📈 Progression: {total_etudiants}/276 ({total_etudiants/276*100:.1f}%)")

if __name__ == "__main__":
    main() 