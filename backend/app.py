from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime, timedelta
import hashlib
import jwt
import time

app = Flask(__name__)
CORS(app)

# Configuration Firebase
# Remplacez le chemin par votre fichier de clé Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Collections Firestore
etudiants_ref = db.collection('etudiants')
candidats_ref = db.collection('candidats')
votes_ref = db.collection('votes')
sessions_ref = db.collection('sessions')
admins_ref = db.collection('admins')

# Configuration JWT (à changer en production)
JWT_SECRET = "infas_vote_secret_key_2024"

# Configuration des administrateurs par défaut
DEFAULT_ADMINS = [
    {
        'email': 'admin@infas.com',
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'name': 'Administrateur Principal'
    }
]

def init_default_admins():
    """Initialiser les administrateurs par défaut"""
    for admin_data in DEFAULT_ADMINS:
        admin_doc = admins_ref.document(admin_data['email'])
        if not admin_doc.get().exists:
            admin_doc.set(admin_data)
            print(f"✅ Administrateur créé: {admin_data['email']}")

def verify_admin_token(token):
    """Vérifier le token administrateur"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except:
        return None

def get_current_session():
    """Obtenir la session de vote actuelle"""
    try:
        sessions = sessions_ref.where('isActive', '==', True).limit(1).stream()
        for session in sessions:
            return session.to_dict()
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de la session: {e}")
        return None

def is_vote_session_active():
    """Vérifier si une session de vote est active"""
    session = get_current_session()
    if not session:
        return False
    
    now = datetime.now()
    start_time = session['startTime'].replace(tzinfo=None) if hasattr(session['startTime'], 'tzinfo') else session['startTime']
    end_time = session['endTime'].replace(tzinfo=None) if hasattr(session['endTime'], 'tzinfo') else session['endTime']
    
    return start_time <= now <= end_time

def increment_candidate_votes(candidat_id):
    """Fonction pour incrémenter les votes d'un candidat"""
    try:
        candidat_ref = candidats_ref.document(candidat_id)
        candidat_snapshot = candidat_ref.get()
        
        if not candidat_snapshot.exists:
            print(f"ERREUR: Candidat {candidat_id} non trouvé")
            return False
        
        candidat_data = candidat_snapshot.to_dict()
        current_votes = candidat_data.get('votes', 0)
        new_votes = current_votes + 1
        
        # Mettre à jour le champ votes
        candidat_ref.update({'votes': new_votes})
        
        print(f"✅ Vote incrémenté pour candidat {candidat_id}: {current_votes} → {new_votes}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'incrémentation: {str(e)}")
        return False

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Connexion administrateur"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        # Vérifier les identifiants administrateur
        admin_doc = admins_ref.document(email).get()
        
        if not admin_doc.exists:
            return jsonify({'error': 'Identifiants invalides'}), 401
        
        admin_data = admin_doc.to_dict()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if admin_data['password'] != hashed_password:
            return jsonify({'error': 'Identifiants invalides'}), 401
        
        # Générer un token JWT
        token = jwt.encode({
            'email': email,
            'name': admin_data['name'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'email': email,
            'name': admin_data['name'],
            'token': token
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/session/status', methods=['GET'])
def get_session_status():
    """Obtenir le statut de la session de vote"""
    try:
        # Vérifier l'authentification admin
        auth_header = request.headers.get('Admin-Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentification requise'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_admin_token(token)
        if not payload:
            return jsonify({'error': 'Token invalide'}), 401
        
        # Obtenir la session actuelle
        session = get_current_session()
        
        if not session:
            return jsonify({
                'isActive': False,
                'totalVotes': 0,
                'totalStudents': 0
            })
        
        # Compter les votes et étudiants
        total_votes = len(list(votes_ref.stream()))
        total_students = len(list(etudiants_ref.stream()))
        
        return jsonify({
            'isActive': session['isActive'],
            'startTime': session['startTime'].isoformat() if hasattr(session['startTime'], 'isoformat') else str(session['startTime']),
            'endTime': session['endTime'].isoformat() if hasattr(session['endTime'], 'isoformat') else str(session['endTime']),
            'duration': session['duration'],
            'totalVotes': total_votes,
            'totalStudents': total_students
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/session/create', methods=['POST'])
def create_session():
    """Créer une nouvelle session de vote"""
    try:
        # Vérifier l'authentification admin
        auth_header = request.headers.get('Admin-Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentification requise'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_admin_token(token)
        if not payload:
            return jsonify({'error': 'Token invalide'}), 401
        
        data = request.get_json()
        start_time = datetime.fromisoformat(data['startTime'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['endTime'].replace('Z', '+00:00'))
        duration = data['duration']
        
        # Désactiver toutes les sessions existantes
        existing_sessions = sessions_ref.where('isActive', '==', True).stream()
        for session in existing_sessions:
            session.reference.update({'isActive': False})
        
        # Créer la nouvelle session
        session_data = {
            'startTime': start_time,
            'endTime': end_time,
            'duration': duration,
            'isActive': True,
            'createdBy': payload['email'],
            'createdAt': datetime.now()
        }
        
        sessions_ref.add(session_data)
        
        return jsonify({'message': 'Session créée avec succès'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/session/stop', methods=['POST'])
def stop_session():
    """Arrêter la session de vote active"""
    try:
        # Vérifier l'authentification admin
        auth_header = request.headers.get('Admin-Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentification requise'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_admin_token(token)
        if not payload:
            return jsonify({'error': 'Token invalide'}), 401
        
        # Arrêter toutes les sessions actives
        active_sessions = sessions_ref.where('isActive', '==', True).stream()
        for session in active_sessions:
            session.reference.update({'isActive': False})
        
        return jsonify({'message': 'Session arrêtée avec succès'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/status', methods=['GET'])
def public_session_status():
    """Statut public de la session de vote"""
    try:
        session = get_current_session()
        
        if not session:
            return jsonify({
                'isActive': False,
                'message': 'Aucune session de vote active'
            })
        
        now = datetime.now()
        start_time = session['startTime'].replace(tzinfo=None) if hasattr(session['startTime'], 'tzinfo') else session['startTime']
        end_time = session['endTime'].replace(tzinfo=None) if hasattr(session['endTime'], 'tzinfo') else session['endTime']
        
        is_active = start_time <= now <= end_time
        
        return jsonify({
            'isActive': is_active,
            'startTime': start_time.isoformat() if hasattr(start_time, 'isoformat') else str(start_time),
            'endTime': end_time.isoformat() if hasattr(end_time, 'isoformat') else str(end_time),
            'message': 'Session de vote active' if is_active else 'Session de vote fermée'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Vérifier le matricule et connecter l'étudiant"""
    try:
        # Vérifier si une session de vote est active
        if not is_vote_session_active():
            return jsonify({'error': 'Aucune session de vote active'}), 403
        
        data = request.get_json()
        matricule = data.get('matricule')
        
        if not matricule:
            return jsonify({'error': 'Matricule requis'}), 400
        
        # Vérifier si l'étudiant existe
        etudiant_doc = etudiants_ref.document(matricule).get()
        
        if not etudiant_doc.exists:
            return jsonify({'error': 'Matricule invalide'}), 401
        
        etudiant_data = etudiant_doc.to_dict()
        
        return jsonify({
            'matricule': matricule,
            'nom': etudiant_data.get('nom'),
            'prenom': etudiant_data.get('prenom'),
            'filiere': etudiant_data.get('filiere')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidats', methods=['GET'])
def get_candidats():
    """Récupérer la liste des candidats"""
    try:
        # Vérifier si une session de vote est active
        if not is_vote_session_active():
            return jsonify({'error': 'Aucune session de vote active'}), 403
        
        candidats = []
        candidats_docs = candidats_ref.stream()
        
        for doc in candidats_docs:
            candidat_data = doc.to_dict()
            candidats.append({
                'id': doc.id,
                'nom': candidat_data.get('nom'),
                'prenom': candidat_data.get('prenom'),
                'filiere': candidat_data.get('filiere'),
                'photo': candidat_data.get('photo', '')
            })
        
        return jsonify(candidats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vote', methods=['POST'])
def vote():
    """Enregistrer un vote"""
    try:
        # Vérifier si une session de vote est active
        if not is_vote_session_active():
            return jsonify({'error': 'Session de vote fermée'}), 403
        
        data = request.get_json()
        candidat_id = data.get('candidat_id')
        
        # Récupérer le matricule depuis l'en-tête Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentification requise'}), 401
        
        matricule = auth_header.split(' ')[1]
        
        if not candidat_id:
            return jsonify({'error': 'ID du candidat requis'}), 400
        
        # Vérifier si l'étudiant a déjà voté
        vote_doc = votes_ref.document(matricule).get()
        if vote_doc.exists:
            return jsonify({'error': 'Vous avez déjà voté'}), 400
        
        # Vérifier si le candidat existe
        candidat_doc = candidats_ref.document(candidat_id).get()
        if not candidat_doc.exists:
            return jsonify({'error': 'Candidat invalide'}), 400
        
        print(f"🗳️ Vote en cours: Étudiant {matricule} vote pour candidat {candidat_id}")
        
        # Incrémenter les votes du candidat
        if not increment_candidate_votes(candidat_id):
            return jsonify({'error': 'Erreur lors de l\'incrémentation des votes'}), 500

        # Enregistrer le vote
        vote_data = {
            'candidat_id': candidat_id,
            'matricule': matricule,
            'timestamp': datetime.now()
        }
        
        votes_ref.document(matricule).set(vote_data)
        print(f"✅ Vote enregistré pour {matricule} → candidat {candidat_id}")
        
        return jsonify({'message': 'Vote enregistré avec succès'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vote/status', methods=['GET'])
def check_vote_status():
    """Vérifier le statut de vote d'un étudiant"""
    try:
        # Récupérer le matricule depuis l'en-tête Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentification requise'}), 401
        
        matricule = auth_header.split(' ')[1]
        
        # Vérifier si l'étudiant a voté
        vote_doc = votes_ref.document(matricule).get()
        
        if vote_doc.exists:
            vote_data = vote_doc.to_dict()
            candidat_id = vote_data.get('candidat_id')
            
            # Récupérer les informations du candidat voté
            candidat_doc = candidats_ref.document(candidat_id).get()
            candidat_data = candidat_doc.to_dict()
            
            return jsonify({
                'has_voted': True,
                'voted_candidate': {
                    'id': candidat_id,
                    'nom': candidat_data.get('nom'),
                    'prenom': candidat_data.get('prenom'),
                    'filiere': candidat_data.get('filiere')
                }
            })
        else:
            return jsonify({'has_voted': False})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/resultats', methods=['GET'])
def get_resultats():
    """Récupérer les résultats des votes"""
    try:
        # Récupérer tous les candidats avec leur nombre de votes
        candidats = []
        candidats_docs = candidats_ref.stream()
        total_votes = 0
        
        for doc in candidats_docs:
            candidat_data = doc.to_dict()
            votes_count = candidat_data.get('votes', 0)
            total_votes += votes_count
            
            candidats.append({
                'id': doc.id,
                'nom': candidat_data.get('nom'),
                'prenom': candidat_data.get('prenom'),
                'filiere': candidat_data.get('filiere'),
                'votes': votes_count,
                'photo': candidat_data.get('photo', '')
            })
        
        # Calculer les pourcentages
        resultats = []
        for candidat in candidats:
            pourcentage = (candidat['votes'] / total_votes * 100) if total_votes > 0 else 0
            resultats.append({
                'id': candidat['id'],
                'nom': candidat['nom'],
                'prenom': candidat['prenom'],
                'filiere': candidat['filiere'],
                'votes': candidat['votes'],
                'pourcentage': round(pourcentage, 2),
                'photo': candidat['photo']
            })
        
        # Trier par nombre de votes décroissant
        resultats.sort(key=lambda x: x['votes'], reverse=True)
        
        return jsonify(resultats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/candidates', methods=['GET'])
def debug_candidates():
    """Route de débogage pour voir l'état des candidats"""
    try:
        candidats = []
        candidats_docs = candidats_ref.stream()
        
        for doc in candidats_docs:
            candidat_data = doc.to_dict()
            candidats.append({
                'id': doc.id,
                'nom': candidat_data.get('nom'),
                'prenom': candidat_data.get('prenom'),
                'votes': candidat_data.get('votes', 0)
            })
        
        return jsonify({
            'message': 'État des candidats',
            'candidats': candidats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de l'état du serveur"""
    return jsonify({'status': 'OK', 'message': 'Serveur opérationnel'})

if __name__ == '__main__':
    # Initialiser les administrateurs par défaut
    init_default_admins()
    app.run(debug=True, host='0.0.0.0', port=5000)