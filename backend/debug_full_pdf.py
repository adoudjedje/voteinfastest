import PyPDF2
import re

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

def debug_full_pdf():
    """Debug complet du PDF"""
    pdf_path = "../LISTE DEFINITIVE LICENCE 1 PGPA 2025_011511(1).pdf"
    
    print("🔍 Debug complet du PDF")
    print("=" * 60)
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return
    
    lines = text.split('\n')
    
    print(f"📄 Total de lignes extraites: {len(lines)}")
    print(f"📄 Longueur totale du texte: {len(text)} caractères")
    
    print("\n📋 Premières 30 lignes:")
    print("-" * 60)
    for i, line in enumerate(lines[:30], 1):
        if line.strip():
            print(f"{i:2d}. '{line}'")
    
    print("\n🔍 Recherche des lignes avec des numéros (1-276):")
    print("-" * 60)
    
    found_numbers = []
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) >= 4:
            try:
                numero = parts[0]
                if numero.isdigit() and int(numero) > 0 and int(numero) <= 276:
                    found_numbers.append(int(numero))
                    print(f"Ligne {i:3d}: {line}")
            except:
                continue
    
    print(f"\n📊 Statistiques:")
    print(f"   Numéros trouvés: {len(found_numbers)}")
    print(f"   Numéros manquants: {276 - len(found_numbers)}")
    
    if found_numbers:
        found_numbers.sort()
        print(f"   Premiers numéros trouvés: {found_numbers[:10]}")
        print(f"   Derniers numéros trouvés: {found_numbers[-10:]}")
        
        # Trouver les gaps
        missing = []
        for i in range(1, 277):
            if i not in found_numbers:
                missing.append(i)
        
        if missing:
            print(f"   Numéros manquants: {missing[:20]}{'...' if len(missing) > 20 else ''}")
    
    print("\n🔍 Analyse des patterns problématiques:")
    print("-" * 60)
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Chercher des lignes qui ressemblent à des étudiants mais ne sont pas parsées
        if any(char.isdigit() for char in line) and len(line.split()) >= 3:
            parts = line.split()
            if not parts[0].isdigit() or int(parts[0]) > 276:
                print(f"Ligne {i:3d} (pattern suspect): '{line}'")

if __name__ == "__main__":
    debug_full_pdf() 