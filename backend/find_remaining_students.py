import firebase_admin
from firebase_admin import credentials, firestore
import PyPDF2
import re
from datetime import datetime

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def extract_text_from_pdf(pdf_path):
    """Extraire le texte du PDF"""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_existing_students():
    """Récupérer les étudiants existants"""
    existing = set()
    etudiants = db.collection('etudiants').stream()
    for etudiant in etudiants:
        data = etudiant.to_dict()
        existing.add(int(data.get('numero', 0)))
    return existing

def find_all_students_in_pdf(text):
    """Trouver tous les étudiants dans le PDF avec patterns avancés"""
    all_students = []
    lines = text.split('\n')
    
    print("🔍 Recherche avancée de tous les étudiants...")
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # Ignorer les lignes d'en-tête
        if 'LISTEDEFINITIVELICENCE' in line or 'NOMATRICULE' in line:
            continue
        
        # Patterns avancés pour capturer tous les formats possibles
        patterns = [
            # Pattern 1: numéro + espace + matricule + PGPA + nom + téléphone
            r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)\s+(\d{10,11}(?:/\d{10,11})?)$',
            # Pattern 2: numéro collé au matricule + PGPA + nom + téléphone
            r'^(\d{1,3})(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)\s+(\d{10,11}(?:/\d{10,11})?)$',
            # Pattern 3: numéro + matricule + PGPA + nom + téléphone (sans espace final)
            r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)(\d{10,11}(?:/\d{10,11})?)$',
            # Pattern 4: numéro collé + matricule + PGPA + nom + téléphone (sans espace final)
            r'^(\d{1,3})(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)(\d{10,11}(?:/\d{10,11})?)$',
            # Pattern 5: numéro + matricule + PGPA + nom + téléphone (format alternatif)
            r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z]+)\s+(\d{10,11}(?:/\d{10,11})?)$',
            # Pattern 6: numéro + matricule + PGPA + nom + téléphone (format compact)
            r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z]+)(\d{10,11}(?:/\d{10,11})?)$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                numero = int(match.group(1))
                matricule = match.group(2)
                nom_complet = match.group(3).strip()
                telephone = match.group(4)
                
                # Vérifier que le numéro est valide
                if numero < 1 or numero > 276:
                    continue
                
                # Séparer nom et prénom
                name_parts = nom_complet.split()
                if len(name_parts) >= 2:
                    prenom = name_parts[-1]
                    nom = ' '.join(name_parts[:-1])
                else:
                    nom = ""
                    prenom = name_parts[0]
                
                all_students.append({
                    'numero': numero,
                    'matricule': matricule,
                    'nom': nom,
                    'prenom': prenom,
                    'filiere': 'PGPA',
                    'telephone': telephone,
                    'ligne_originale': line,
                    'ligne_num': line_num
                })
                break
    
    return all_students

def analyze_missing_numbers(existing_numbers):
    """Analyser les numéros manquants"""
    all_numbers = set(range(1, 277))
    missing_numbers = all_numbers - existing_numbers
    
    print(f"\n📊 ANALYSE DES NUMÉROS MANQUANTS")
    print("=" * 50)
    print(f"Numéros existants: {len(existing_numbers)}")
    print(f"Numéros manquants: {len(missing_numbers)}")
    
    if missing_numbers:
        missing_list = sorted(list(missing_numbers))
        print(f"Numéros manquants: {missing_list}")
        
        # Grouper par plages
        ranges = []
        start = missing_list[0]
        end = start
        
        for num in missing_list[1:]:
            if num == end + 1:
                end = num
            else:
                ranges.append((start, end))
                start = end = num
        
        ranges.append((start, end))
        
        print("\n📋 Plages de numéros manquants:")
        for start, end in ranges:
            if start == end:
                print(f"  N°{start}")
            else:
                print(f"  N°{start} à N°{end} ({end - start + 1} étudiants)")
    
    return missing_numbers

def search_for_specific_numbers(text, missing_numbers):
    """Rechercher des étudiants avec des numéros spécifiques"""
    print(f"\n🔍 Recherche des étudiants avec numéros spécifiques...")
    
    found_students = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # Chercher des numéros spécifiques dans la ligne
        for numero in missing_numbers:
            # Chercher le numéro au début de la ligne
            if re.match(f'^{numero}\\s+', line) or re.match(f'^{numero}\\d', line):
                print(f"Ligne {line_num}: Numéro {numero} trouvé - '{line[:80]}...'")
                
                # Essayer d'extraire les informations
                try:
                    # Chercher le matricule
                    matricule_match = re.search(r'(\d{2}[P-]?\d{4,5})', line)
                    if not matricule_match:
                        continue
                    
                    matricule = matricule_match.group(1)
                    
                    # Chercher PGPA
                    if 'PGPA' not in line:
                        continue
                    
                    # Chercher le téléphone
                    telephone_match = re.search(r'(\d{10,11}(?:/\d{10,11})?)$', line)
                    if not telephone_match:
                        continue
                    
                    telephone = telephone_match.group(1)
                    
                    # Extraire le nom
                    start_pos = line.find(matricule) + len(matricule)
                    end_pos = line.find(telephone)
                    
                    if start_pos >= end_pos:
                        continue
                    
                    nom_part = line[start_pos:end_pos].strip()
                    nom_part = re.sub(r'PGPA[A-Z\s]*', '', nom_part).strip()
                    
                    if not nom_part:
                        continue
                    
                    # Séparer nom et prénom
                    name_parts = nom_part.split()
                    if len(name_parts) >= 2:
                        prenom = name_parts[-1]
                        nom = ' '.join(name_parts[:-1])
                    else:
                        nom = ""
                        prenom = name_parts[0]
                    
                    found_students.append({
                        'numero': numero,
                        'matricule': matricule,
                        'nom': nom,
                        'prenom': prenom,
                        'filiere': 'PGPA',
                        'telephone': telephone,
                        'ligne_originale': line
                    })
                    
                    print(f"  ✅ Extrait: N°{numero} - {matricule} - {nom} {prenom}")
                    
                except Exception as e:
                    print(f"  ❌ Erreur extraction: {e}")
                    continue
    
    return found_students

def insert_found_students(found_students):
    """Insérer les étudiants trouvés"""
    if not found_students:
        print("❌ Aucun étudiant à ajouter")
        return 0
    
    print(f"\n📝 Ajout de {len(found_students)} étudiants trouvés...")
    
    added_count = 0
    for i, student in enumerate(found_students, 1):
        try:
            # Vérifier si existe déjà
            existing = db.collection('etudiants').document(student['matricule']).get()
            if existing.exists:
                print(f"⚠️  {student['matricule']} existe déjà")
                continue
            
            # Ajouter l'étudiant
            db.collection('etudiants').document(student['matricule']).set({
                'matricule': student['matricule'],
                'nom': student['nom'],
                'prenom': student['prenom'],
                'filiere': student['filiere'],
                'telephone': student['telephone'],
                'numero': str(student['numero']),
                'created_at': datetime.now()
            })
            
            print(f"✅ {i}/{len(found_students)} - N°{student['numero']} - {student['matricule']} - {student['nom']} {student['prenom']}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Erreur {student['matricule']}: {e}")
    
    print(f"🎉 {added_count} étudiants ajoutés!")
    return added_count

def main():
    print("🔍 RECHERCHE DES ÉTUDIANTS MANQUANTS RESTANTS")
    print("=" * 60)
    
    # Extraire le texte du PDF
    text = extract_text_from_pdf("../LISTE DEFINITIVE LICENCE 1 PGPA 2025_011511(1).pdf")
    
    if not text:
        print("❌ Impossible d'extraire le texte du PDF")
        return
    
    # Récupérer les étudiants existants
    existing_students = get_existing_students()
    
    # Analyser les numéros manquants
    missing_numbers = analyze_missing_numbers(existing_students)
    
    if not missing_numbers:
        print("✅ Tous les étudiants sont présents!")
        return
    
    # Rechercher les étudiants avec les numéros manquants
    found_students = search_for_specific_numbers(text, missing_numbers)
    
    if found_students:
        print(f"\n📋 {len(found_students)} étudiants trouvés avec numéros manquants")
        
        # Demander confirmation
        response = input(f"\nVoulez-vous ajouter ces {len(found_students)} étudiants? (oui/non): ").lower().strip()
        
        if response in ['oui', 'o', 'yes', 'y']:
            added_count = insert_found_students(found_students)
            
            # Vérifier le total final
            final_total = len(list(db.collection('etudiants').stream()))
            print(f"\n📊 Total final: {final_total}/276 étudiants ({final_total/276*100:.1f}%)")
            
            if final_total == 276:
                print("🎉 Tous les étudiants ont été importés avec succès!")
            else:
                print(f"⚠️  Il manque encore {276 - final_total} étudiants")
        else:
            print("❌ Opération annulée")
    else:
        print("❌ Aucun étudiant manquant trouvé dans le PDF")

if __name__ == "__main__":
    main() 