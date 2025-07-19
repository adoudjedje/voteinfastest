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

def parse_all_students_fixed(text):
    """Parser tous les étudiants avec correction des formats"""
    all_students = []
    lines = text.split('\n')
    
    print("🔍 Parsing corrigé de tous les étudiants du PDF...")
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # Ignorer les lignes d'en-tête
        if 'LISTEDEFINITIVELICENCE' in line or 'NOMATRICULE' in line:
            continue
        
        # Pattern principal: numéro + matricule + PGPA + nom + téléphone
        # Gérer les cas où il n'y a pas d'espace entre numéro et matricule
        patterns = [
            # Pattern 1: numéro + espace + matricule + PGPA + nom + téléphone
            r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)\s+(\d{10,11}(?:/\d{10,11})?)$',
            # Pattern 2: numéro collé au matricule + PGPA + nom + téléphone
            r'^(\d{1,3})(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)\s+(\d{10,11}(?:/\d{10,11})?)$',
            # Pattern 3: numéro + matricule + PGPA + nom + téléphone (sans espace final)
            r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)(\d{10,11}(?:/\d{10,11})?)$',
            # Pattern 4: numéro collé + matricule + PGPA + nom + téléphone (sans espace final)
            r'^(\d{1,3})(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)(\d{10,11}(?:/\d{10,11})?)$',
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

def insert_missing_students(missing_students):
    """Insérer les étudiants manquants"""
    if not missing_students:
        print("✅ Tous les étudiants sont déjà dans la base de données!")
        return 0
    
    print(f"\n📝 Ajout de {len(missing_students)} étudiants manquants...")
    
    added_count = 0
    for i, student in enumerate(missing_students, 1):
        try:
            # Vérifier si l'étudiant existe déjà par matricule
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
            
            print(f"✅ {i}/{len(missing_students)} - N°{student['numero']} - {student['matricule']} - {student['nom']} {student['prenom']}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Erreur {student['matricule']}: {e}")
    
    print(f"🎉 {added_count} étudiants ajoutés avec succès!")
    return added_count

def display_statistics(pdf_students, existing_students, missing_students):
    """Afficher les statistiques"""
    print("\n" + "="*60)
    print("📊 STATISTIQUES COMPLÈTES")
    print("="*60)
    
    total_pdf = len(pdf_students)
    total_existing = len(existing_students)
    total_missing = len(missing_students)
    
    print(f"📄 Total dans le PDF: {total_pdf}")
    print(f"💾 Total en base: {total_existing}")
    print(f"❌ Total manquants: {total_missing}")
    print(f"📈 Progression: {total_existing}/{276} ({total_existing/276*100:.1f}%)")
    
    if missing_students:
        print(f"\n📋 Étudiants manquants ({len(missing_students)}):")
        print("-" * 60)
        for student in missing_students[:10]:
            print(f"  N°{student['numero']:3d} - {student['matricule']} - {student['nom']} {student['prenom']}")
        
        if len(missing_students) > 10:
            print(f"  ... et {len(missing_students) - 10} autres")

def main():
    print("🔍 IMPORT COMPLET CORRIGÉ DES ÉTUDIANTS")
    print("=" * 60)
    
    # Extraire le texte du PDF
    print("📄 Extraction du texte du PDF...")
    text = extract_text_from_pdf("../LISTE DEFINITIVE LICENCE 1 PGPA 2025_011511(1).pdf")
    
    if not text:
        print("❌ Impossible d'extraire le texte du PDF")
        return
    
    print("✅ Texte extrait avec succès")
    
    # Parser tous les étudiants du PDF avec correction
    pdf_students = parse_all_students_fixed(text)
    
    if not pdf_students:
        print("❌ Aucun étudiant trouvé dans le PDF")
        return
    
    print(f"✅ {len(pdf_students)} étudiants parsés du PDF")
    
    # Récupérer les étudiants existants
    existing_students = get_existing_students()
    
    # Trouver les étudiants manquants
    missing_students = []
    for student in pdf_students:
        if student['numero'] not in existing_students:
            missing_students.append(student)
    
    # Afficher les statistiques
    display_statistics(pdf_students, existing_students, missing_students)
    
    if missing_students:
        # Demander confirmation
        response = input(f"\nVoulez-vous ajouter ces {len(missing_students)} étudiants manquants? (oui/non): ").lower().strip()
        
        if response in ['oui', 'o', 'yes', 'y']:
            added_count = insert_missing_students(missing_students)
            
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
        print("✅ Tous les étudiants sont déjà dans la base de données!")

if __name__ == "__main__":
    main() 