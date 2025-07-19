import PyPDF2
import re

def extract_text_from_pdf(pdf_path):
    """Extraire le texte du PDF"""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def analyze_pdf_format(text):
    """Analyser le format du PDF"""
    print("🔍 ANALYSE DU FORMAT DU PDF")
    print("=" * 60)
    
    lines = text.split('\n')
    
    print(f"📄 Total de lignes: {len(lines)}")
    
    # Analyser les premières lignes pour comprendre le format
    print("\n📋 Premières lignes du PDF:")
    print("-" * 60)
    
    for i, line in enumerate(lines[:20], 1):
        if line.strip():
            print(f"Ligne {i:2d}: '{line[:100]}...'")
    
    # Chercher les lignes qui contiennent des numéros
    print("\n🔢 Lignes contenant des numéros:")
    print("-" * 60)
    
    numero_lines = []
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Chercher un numéro au début de la ligne
        numero_match = re.match(r'^(\d{1,3})\s+', line)
        if numero_match:
            numero = int(numero_match.group(1))
            if 1 <= numero <= 276:
                numero_lines.append((i, numero, line))
                print(f"Ligne {i:3d}: N°{numero:3d} - '{line[:80]}...'")
    
    print(f"\n📊 Total de lignes avec numéros: {len(numero_lines)}")
    
    # Analyser quelques exemples en détail
    if numero_lines:
        print("\n🔍 Analyse détaillée des premières lignes:")
        print("-" * 60)
        
        for i, (line_num, numero, line) in enumerate(numero_lines[:5]):
            print(f"\nExemple {i+1}:")
            print(f"  Ligne: {line_num}")
            print(f"  Numéro: {numero}")
            print(f"  Contenu: '{line}'")
            
            # Chercher les composants
            matricule_match = re.search(r'(\d{2}[P-]?\d{4,5})', line)
            pgpa_match = re.search(r'PGPA', line)
            telephone_match = re.search(r'(\d{10,11}(?:/\d{10,11})?)$', line)
            
            print(f"  Matricule trouvé: {matricule_match.group(1) if matricule_match else 'Non trouvé'}")
            print(f"  PGPA trouvé: {'Oui' if pgpa_match else 'Non'}")
            print(f"  Téléphone trouvé: {telephone_match.group(1) if telephone_match else 'Non trouvé'}")
    
    # Chercher les patterns spécifiques
    print("\n🔍 Recherche de patterns spécifiques:")
    print("-" * 60)
    
    patterns_to_test = [
        r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)\s+(\d{10,11}(?:/\d{10,11})?)$',
        r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})\s+PGPA\s+([A-Z\s]+?)\s+(\d{10,11}(?:/\d{10,11})?)$',
        r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z]+)\s+(\d{10,11}(?:/\d{10,11})?)$',
        r'^(\d{1,3})\s+(\d{2}[P-]?\d{4,5})PGPA([A-Z\s]+?)(\d{10,11}(?:/\d{10,11})?)$',
    ]
    
    for pattern_idx, pattern in enumerate(patterns_to_test, 1):
        matches = 0
        for line_num, numero, line in numero_lines:
            if re.match(pattern, line):
                matches += 1
        
        print(f"Pattern {pattern_idx}: {matches} correspondances")
    
    # Analyser les numéros manquants
    print("\n📊 Analyse des numéros:")
    print("-" * 60)
    
    found_numbers = set(numero for _, numero, _ in numero_lines)
    missing_numbers = set(range(1, 277)) - found_numbers
    
    print(f"Numéros trouvés: {len(found_numbers)}")
    print(f"Numéros manquants: {len(missing_numbers)}")
    
    if missing_numbers:
        print("Premiers numéros manquants:", sorted(list(missing_numbers))[:10])
    
    return numero_lines

def main():
    print("🔍 DEBUG DU FORMAT PDF")
    print("=" * 60)
    
    # Extraire le texte du PDF
    text = extract_text_from_pdf("../LISTE DEFINITIVE LICENCE 1 PGPA 2025_011511(1).pdf")
    
    if not text:
        print("❌ Impossible d'extraire le texte du PDF")
        return
    
    # Analyser le format
    numero_lines = analyze_pdf_format(text)
    
    print(f"\n✅ Analyse terminée. {len(numero_lines)} lignes avec numéros trouvées.")

if __name__ == "__main__":
    main() 