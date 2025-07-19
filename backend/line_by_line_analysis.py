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
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_existing_students():
    existing = set()
    etudiants = db.collection('etudiants').stream()
    for etudiant in etudiants:
        data = etudiant.to_dict()
        existing.add(int(data.get('numero', 0)))
    return existing

def analyze_line_by_line(text):
    students = []
    existing_numbers = get_existing_students()
    
    print(f"📊 Étudiants existants: {len(existing_numbers)}")
    print("🔍 Analyse ligne par ligne...")
    
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # Chercher un numéro au début de la ligne
        numero_match = re.match(r'^(\d{1,3})\s+', line)
        if not numero_match:
            continue
        
        numero = int(numero_match.group(1))
        
        # Vérifier si ce numéro est manquant
        if numero in existing_numbers or numero > 276:
            continue
        
        print(f"Ligne {line_num}: Numéro {numero} manquant - '{line[:80]}...'")
        
        # Essayer d'extraire les informations
        try:
            # Chercher le matricule (format: 24P-XXXX ou 24-XXXX)
            matricule_match = re.search(r'(\d{2}[P-]?\d{4,5})', line)
            if not matricule_match:
                continue
            
            matricule = matricule_match.group(1)
            
            # Chercher PGPA
            if 'PGPA' not in line:
                continue
            
            # Chercher le téléphone (dernier groupe de chiffres)
            telephone_match = re.search(r'(\d{10,11}(?:/\d{10,11})?)$', line)
            if not telephone_match:
                continue
            
            telephone = telephone_match.group(1)
            
            # Extraire le nom entre le matricule et le téléphone
            start_pos = line.find(matricule) + len(matricule)
            end_pos = line.find(telephone)
            
            if start_pos >= end_pos:
                continue
            
            nom_part = line[start_pos:end_pos].strip()
            
            # Nettoyer le nom (enlever PGPA et autres éléments)
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
            
            students.append({
                'numero': str(numero),
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
    
    return students

def insert_students(students):
    if not students:
        print("❌ Aucun étudiant à ajouter")
        return
    
    print(f"\n📝 Ajout de {len(students)} étudiants...")
    
    added_count = 0
    for i, student in enumerate(students, 1):
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
                'numero': student['numero'],
                'created_at': datetime.now()
            })
            
            print(f"✅ {i}/{len(students)} - N°{student['numero']} - {student['nom']} {student['prenom']}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Erreur {student['matricule']}: {e}")
    
    print(f"🎉 {added_count} étudiants ajoutés!")

def main():
    print("🔍 Analyse ligne par ligne pour les étudiants manquants")
    print("=" * 60)
    
    # Extraire texte du PDF
    text = extract_text_from_pdf("../LISTE DEFINITIVE LICENCE 1 PGPA 2025_011511(1).pdf")
    
    # Analyser ligne par ligne
    missing_students = analyze_line_by_line(text)
    
    if missing_students:
        print(f"\n📋 {len(missing_students)} étudiants manquants identifiés")
        
        # Demander confirmation
        response = input(f"\nVoulez-vous ajouter ces {len(missing_students)} étudiants? (oui/non): ").lower().strip()
        
        if response in ['oui', 'o', 'yes', 'y']:
            insert_students(missing_students)
            
            # Vérifier total final
            total = len(list(db.collection('etudiants').stream()))
            print(f"\n📊 Total final: {total}/276 étudiants ({total/276*100:.1f}%)")
        else:
            print("❌ Opération annulée")
    else:
        print("❌ Aucun étudiant manquant trouvé")

if __name__ == "__main__":
    main() 