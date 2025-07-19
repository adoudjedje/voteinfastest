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

def find_all_missing_students(text):
    students = []
    existing_numbers = get_existing_students()
    
    print(f"📊 Étudiants existants: {len(existing_numbers)}")
    
    # Pattern pour capturer: numéro + matricule + PGPA + nom + téléphone
    pattern = r'(\d{1,3})\s+(\d{2}[P-]?\d{4,5}PGPA[A-Z\s]+?)\s+(\d{10,11}(?:/\d{10,11})?)$'
    
    matches = re.finditer(pattern, text, re.MULTILINE)
    
    for match in matches:
        numero = int(match.group(1))
        matricule_complet = match.group(2)
        telephone = match.group(3)
        
        if numero in existing_numbers:
            continue
            
        # Extraire matricule simple
        matricule_simple = matricule_complet.split('PGPA')[0]
        
        # Extraire nom/prénom
        nom_part = matricule_complet.split('PGPA')[1].strip()
        
        if ' ' in nom_part:
            name_parts = nom_part.split()
            prenom = name_parts[-1]
            nom = ' '.join(name_parts[:-1])
        else:
            nom = ""
            prenom = nom_part
        
        students.append({
            'numero': str(numero),
            'matricule': matricule_simple,
            'nom': nom,
            'prenom': prenom,
            'filiere': 'PGPA',
            'telephone': telephone,
            'matricule_complet': matricule_complet
        })
    
    return students

def insert_students(students):
    if not students:
        print("❌ Aucun étudiant à ajouter")
        return
    
    print(f"📝 Ajout de {len(students)} étudiants...")
    
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
            
        except Exception as e:
            print(f"❌ Erreur {student['matricule']}: {e}")
    
    print(f"🎉 {len(students)} étudiants ajoutés!")

def main():
    print("🔍 Ajout des 58 étudiants manquants")
    print("=" * 50)
    
    # Extraire texte du PDF
    text = extract_text_from_pdf("../LISTE DEFINITIVE LICENCE 1 PGPA 2025_011511(1).pdf")
    
    # Trouver étudiants manquants
    missing_students = find_all_missing_students(text)
    
    if missing_students:
        print(f"\n📋 {len(missing_students)} étudiants manquants trouvés:")
        for student in missing_students[:5]:
            print(f"  N°{student['numero']} - {student['matricule']} - {student['nom']} {student['prenom']}")
        
        if len(missing_students) > 5:
            print(f"  ... et {len(missing_students) - 5} autres")
        
        # Ajouter les étudiants
        insert_students(missing_students)
        
        # Vérifier total final
        total = len(list(db.collection('etudiants').stream()))
        print(f"\n📊 Total final: {total}/276 étudiants ({total/276*100:.1f}%)")
    else:
        print("❌ Aucun étudiant manquant trouvé")

if __name__ == "__main__":
    main() 