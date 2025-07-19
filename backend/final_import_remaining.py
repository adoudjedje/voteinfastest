import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_existing_students():
    """Récupérer les étudiants existants"""
    existing = set()
    etudiants = db.collection('etudiants').stream()
    for etudiant in etudiants:
        data = etudiant.to_dict()
        existing.add(int(data.get('numero', 0)))
    return existing

def add_remaining_students():
    """Ajouter les étudiants restants manuellement"""
    
    # Liste des étudiants manquants basée sur l'analyse du PDF
    missing_students = [
        # Étudiants identifiés dans l'analyse précédente
        {"numero": 12, "matricule": "24P-2834", "nom": "AGOU", "prenom": "AKPISIMEONCREPIN", "telephone": "0142058572"},
        {"numero": 18, "matricule": "24P-1822", "nom": "AKASSA", "prenom": "KOUSSOMARIEESTELLE", "telephone": "0759233883"},
        {"numero": 20, "matricule": "24P-1119", "nom": "AKPA", "prenom": "MICKAEL", "telephone": "0709473421"},
        {"numero": 21, "matricule": "24P-2964", "nom": "AMA", "prenom": "TANOHELODIE", "telephone": "0709551217"},
        {"numero": 22, "matricule": "24P-1538", "nom": "AMANI", "prenom": "BROUINNOCENTE", "telephone": "0759709631"},
        {"numero": 23, "matricule": "24-11674", "nom": "AMANVI", "prenom": "ALLOMOUCHRISTINE", "telephone": "0777285206"},
        {"numero": 29, "matricule": "24P-1554", "nom": "APPIA", "prenom": "JULES", "telephone": "0779127795"},
        {"numero": 39, "matricule": "24P-0282", "nom": "ATTO", "prenom": "APIEGWLADYS", "telephone": "0141585220"},
        {"numero": 43, "matricule": "24-11673", "nom": "ATTO", "prenom": "APIEGWLADYS", "telephone": "0576226165"},
        {"numero": 47, "matricule": "24-11692", "nom": "BEDE", "prenom": "KOMETWILFRIED", "telephone": "070951123"},
        {"numero": 48, "matricule": "24P-1493", "nom": "BEDJI", "prenom": "EVODIECLEMENCE", "telephone": "0505002393"},
        {"numero": 50, "matricule": "24P-1981", "nom": "BOA", "prenom": "TANONRUTHPATRICIA", "telephone": "0701994816"},
        {"numero": 51, "matricule": "24P-2325", "nom": "BODJI", "prenom": "BAFFOLEESAIEARISTIDE", "telephone": "0797490109"},
        {"numero": 52, "matricule": "24P-1977", "nom": "BOFFO", "prenom": "GRACEELVIRA", "telephone": "0749333862"},
        {"numero": 60, "matricule": "24P-1952", "nom": "BROU", "prenom": "YAOYANNALEX", "telephone": "0759445183"},
        {"numero": 66, "matricule": "24-11773", "nom": "BROU", "prenom": "YAOYANNALEX", "telephone": "0759445183"},
        {"numero": 72, "matricule": "24P-2769", "nom": "DAPPA", "prenom": "KOBENANJEANPAUL", "telephone": "0779322105"},
        {"numero": 73, "matricule": "24P-1254", "nom": "DEGNY", "prenom": "YACEFLAVIEELGARPARICE", "telephone": "0777041432"},
        {"numero": 74, "matricule": "24P-0420", "nom": "DEGUI", "prenom": "MARTHEGERTRUDE", "telephone": "0779851963"},
        {"numero": 80, "matricule": "24P-1694", "nom": "DIOMANDE", "prenom": "INZA", "telephone": "0708301477"},
        {"numero": 86, "matricule": "24P-2522", "nom": "DOBE", "prenom": "STEPHANEBEMA", "telephone": "0789378100"},
        {"numero": 87, "matricule": "24P-0543", "nom": "DON", "prenom": "BOSCOGINETTELINDA", "telephone": "0777084295"},
        {"numero": 89, "matricule": "24-11722", "nom": "DOUEU", "prenom": "EMMANUEL", "telephone": "0704252004"},
        {"numero": 93, "matricule": "24P-1997", "nom": "DOUON", "prenom": "NUNKAMEPRINCEULRICH", "telephone": "0585999855"},
        {"numero": 99, "matricule": "24P-3244", "nom": "ESSUI", "prenom": "N'DAHAFFOUEFABIENNE", "telephone": "0708580962"},
        {"numero": 113, "matricule": "24-11744", "nom": "GREBIO", "prenom": "GRÂCEEMMANUELLA", "telephone": "0769617083"},
        {"numero": 115, "matricule": "24P-0295", "nom": "GUEHI", "prenom": "STEPHANIEAUDE", "telephone": "0747774992"},
        {"numero": 123, "matricule": "24P-2083", "nom": "KANHUE", "prenom": "MOMANANGELEÉPOUSELEUH", "telephone": "0504120522"},
        {"numero": 128, "matricule": "24P-1794", "nom": "KASSI", "prenom": "ADJOBAPAULINECLAVERIE", "telephone": "0767040259"},
        {"numero": 131, "matricule": "24-11759", "nom": "KIMOU", "prenom": "ACHYJOELFABRICE", "telephone": "0767664845"},
        {"numero": 137, "matricule": "24P-11216", "nom": "KOFFI", "prenom": "BOSSOANDREAEUPHRASIE", "telephone": "0707690544"},
        {"numero": 144, "matricule": "24P-0842", "nom": "KONAN", "prenom": "KOUAKOUESTELLE", "telephone": "0709910736"},
        {"numero": 152, "matricule": "24P-0541", "nom": "KOTCHI", "prenom": "APOAIMEE", "telephone": "0748999928"},
        {"numero": 156, "matricule": "23P-2650", "nom": "KOUADIO", "prenom": "NIAMIENRICARDO", "telephone": "0708100524"},
        {"numero": 158, "matricule": "24P-3227", "nom": "KOUADIO", "prenom": "FO", "telephone": "0749054219"},
        {"numero": 161, "matricule": "24P-0874", "nom": "KOUADIO", "prenom": "NIAMKEYMARIEADELLENOEL", "telephone": "0787028917"},
        {"numero": 162, "matricule": "24P-2814", "nom": "KOUAHO", "prenom": "KENZREYAYEKPAPRISCA", "telephone": "0759065902"},
        {"numero": 163, "matricule": "24P-1375", "nom": "KOUAKOU", "prenom": "KOUASSIKEVIN", "telephone": "0788236960"},
        {"numero": 164, "matricule": "24P-2607", "nom": "KOUAKOU", "prenom": "YAOROMUALDULRICH", "telephone": "0789853051"},
        {"numero": 194, "matricule": "24P-0299", "nom": "MANIMA", "prenom": "GISÈLEANDRÉA", "telephone": "0759458614"},
        {"numero": 203, "matricule": "24P-1991", "nom": "N'GUESSAN", "prenom": "AHOUSOLANGE", "telephone": "0506317008"},
        {"numero": 212, "matricule": "24P-0318", "nom": "N'GUESSAN", "prenom": "KOUAMEHERMANN", "telephone": "0757789778"},
        {"numero": 214, "matricule": "24P-2202", "nom": "NIONGUI", "prenom": "JOCELYNE", "telephone": "0707822971"},
        {"numero": 219, "matricule": "24P-2835", "nom": "OUATTARA", "prenom": "AICHA", "telephone": "0704057141"},
        {"numero": 220, "matricule": "24P-2076", "nom": "OUATTARA", "prenom": "ADAMA", "telephone": "0544623155"},
        {"numero": 221, "matricule": "23P-2074", "nom": "OUATTARA", "prenom": "IBRAHIM", "telephone": "0767621783"},
        {"numero": 231, "matricule": "24P-2787", "nom": "SERI", "prenom": "GNANZEGBOJEAN-DIEUDONNE", "telephone": "0141888407"},
        {"numero": 249, "matricule": "24-11859", "nom": "TOURE", "prenom": "BASSITAFIDELE", "telephone": "0768555478"},
        {"numero": 251, "matricule": "24P-0321", "nom": "TRAORÉ", "prenom": "MAMINA", "telephone": "0757101545"},
        {"numero": 261, "matricule": "24P-0767", "nom": "YAO", "prenom": "KAKOUSAMSONARISTIDE", "telephone": "0748510797"},
        {"numero": 264, "matricule": "24P-0766", "nom": "YAO", "prenom": "YAWAHENRIETTE", "telephone": "0748872660"},
        {"numero": 267, "matricule": "24-11874", "nom": "YAPO", "prenom": "NANDJUIYOANARIEL", "telephone": "0797127502"},
    ]
    
    existing_numbers = get_existing_students()
    
    # Filtrer les étudiants qui ne sont pas encore dans la base
    to_add = []
    for student in missing_students:
        if student['numero'] not in existing_numbers:
            to_add.append(student)
    
    print(f"📊 Étudiants existants: {len(existing_numbers)}")
    print(f"📋 Étudiants à ajouter: {len(to_add)}")
    
    if not to_add:
        print("✅ Tous les étudiants sont déjà dans la base de données!")
        return
    
    print(f"\n📝 Ajout de {len(to_add)} étudiants...")
    
    added_count = 0
    for i, student in enumerate(to_add, 1):
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
                'filiere': 'PGPA',
                'telephone': student['telephone'],
                'numero': str(student['numero']),
                'created_at': datetime.now()
            })
            
            print(f"✅ {i}/{len(to_add)} - N°{student['numero']} - {student['matricule']} - {student['nom']} {student['prenom']}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Erreur {student['matricule']}: {e}")
    
    print(f"🎉 {added_count} étudiants ajoutés avec succès!")
    return added_count

def main():
    print("🔍 IMPORT FINAL DES ÉTUDIANTS RESTANTS")
    print("=" * 60)
    
    # Ajouter les étudiants restants
    added_count = add_remaining_students()
    
    # Vérifier le total final
    final_total = len(list(db.collection('etudiants').stream()))
    print(f"\n📊 Total final: {final_total}/276 étudiants ({final_total/276*100:.1f}%)")
    
    if final_total == 276:
        print("🎉 Tous les étudiants ont été importés avec succès!")
    else:
        print(f"⚠️  Il manque encore {276 - final_total} étudiants")
        
        # Afficher les numéros manquants
        existing_numbers = get_existing_students()
        all_numbers = set(range(1, 277))
        missing_numbers = all_numbers - existing_numbers
        
        if missing_numbers:
            print(f"Numéros manquants: {sorted(list(missing_numbers))}")

if __name__ == "__main__":
    main() 