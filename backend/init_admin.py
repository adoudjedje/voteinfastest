import firebase_admin
from firebase_admin import credentials, firestore
import hashlib

# Configuration Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Collection des administrateurs
admins_ref = db.collection('admins')

# Configuration des administrateurs par défaut
DEFAULT_ADMINS = [
    {
        'email': 'admin@infas.com',
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'name': 'Administrateur Principal'
    },
    {
        'email': 'supervisor@infas.com',
        'password': hashlib.sha256('supervisor123'.encode()).hexdigest(),
        'name': 'Superviseur'
    }
]

def init_admins():
    """Initialiser les administrateurs par défaut"""
    print("🔧 Initialisation des administrateurs...")
    
    for admin_data in DEFAULT_ADMINS:
        admin_doc = admins_ref.document(admin_data['email'])
        
        if not admin_doc.get().exists:
            admin_doc.set(admin_data)
            print(f"✅ Administrateur créé: {admin_data['email']} (mot de passe: {admin_data['email'].split('@')[0]}123)")
        else:
            print(f"ℹ️  Administrateur existe déjà: {admin_data['email']}")
    
    print("\n📋 Identifiants de connexion:")
    print("=" * 50)
    for admin in DEFAULT_ADMINS:
        email = admin['email']
        password = email.split('@')[0] + '123'
        print(f"Email: {email}")
        print(f"Mot de passe: {password}")
        print("-" * 30)
    
    print("\n🎯 Accès à l'administration:")
    print("1. Allez sur: http://localhost:3000/admin/login")
    print("2. Utilisez les identifiants ci-dessus")
    print("3. Créez une session de vote")
    print("4. Les étudiants pourront alors voter")

if __name__ == "__main__":
    init_admins() 