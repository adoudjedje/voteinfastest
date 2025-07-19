# Application de Vote INFAS 35e Promotion PGP

Application web complète pour le système de vote des étudiants de l'INFAS 35e promotion PGP.

## 🚀 Fonctionnalités

- **Authentification par matricule** : Les étudiants se connectent avec leur matricule
- **Vote unique** : Chaque étudiant ne peut voter qu'une seule fois
- **Liste des candidats** : Affichage de tous les candidats avec leurs informations
- **Résultats en temps réel** : Diagramme en bande avec mise à jour automatique
- **Interface moderne** : Design responsive et intuitif

## 🛠️ Technologies utilisées

### Frontend
- **React JS** (.jsx) - Framework JavaScript
- **React Router** - Navigation entre les pages
- **Recharts** - Graphiques pour les résultats
- **Axios** - Appels API
- **CSS3** - Styles et animations

### Backend
- **Flask** - Framework Python
- **Flask-CORS** - Gestion des requêtes cross-origin
- **Firebase Admin SDK** - Connexion à Firebase

### Base de données
- **Firebase Firestore** - Base de données NoSQL

## 📁 Structure du projet

```
infas-vote-app/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   └── Results.jsx
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   ├── App.css
│   ├── index.js
│   └── index.css
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── init_db.py
├── package.json
└── README.md
```

## 🚀 Installation et configuration

### 1. Configuration Firebase

1. Créez un projet Firebase sur [console.firebase.google.com](https://console.firebase.google.com)
2. Activez Firestore Database
3. Créez un compte de service :
   - Allez dans Paramètres du projet > Comptes de service
   - Cliquez sur "Générer une nouvelle clé privée"
   - Téléchargez le fichier JSON
4. Placez le fichier JSON dans le dossier `backend/` et renommez-le `firebase-key.json`

### 2. Installation du Frontend

```bash
# Installer les dépendances
npm install

# Démarrer l'application en mode développement
npm start
```

L'application sera accessible sur `http://localhost:3000`

### 3. Installation du Backend

```bash
# Aller dans le dossier backend
cd backend

# Créer un environnement virtuel Python
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur macOS/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données avec des données d'exemple
python init_db.py

# Démarrer le serveur Flask
python app.py
```

Le serveur API sera accessible sur `http://localhost:5000`

## 📊 Structure de la base de données

### Collection `etudiants`
```json
{
  "matricule": "2024001",
  "nom": "Kouadio",
  "prenom": "Jean",
  "filiere": "PGP"
}
```

### Collection `candidats`
```json
{
  "id": "1",
  "nom": "Traoré",
  "prenom": "Awa",
  "filiere": "PGP"
}
```

### Collection `votes`
```json
{
  "matricule": "2024001",
  "candidat_id": "1",
  "timestamp": "2024-06-01T12:00:00Z"
}
```

## 🔧 API Endpoints

### Authentification
- `POST /api/login` - Connexion avec matricule

### Candidats
- `GET /api/candidats` - Liste des candidats

### Votes
- `POST /api/vote` - Enregistrer un vote
- `GET /api/vote/status` - Vérifier le statut de vote
- `GET /api/resultats` - Résultats des votes

### Santé
- `GET /api/health` - Vérification de l'état du serveur

## 🧪 Données de test

Après avoir exécuté `init_db.py`, vous pouvez utiliser ces matricules pour tester :

- **2024001** - Jean Kouadio
- **2024002** - Awa Traoré
- **2024003** - Moussa Koné
- **2024004** - Fatou Ouattara
- **2024005** - Kouassi Bamba

## 🎯 Utilisation

1. **Connexion** : L'étudiant entre son matricule
2. **Dashboard** : Affichage de la liste des candidats
3. **Vote** : L'étudiant sélectionne un candidat et vote
4. **Résultats** : Visualisation des résultats en temps réel

## 🔒 Sécurité

- Authentification par matricule
- Vote unique par étudiant
- Validation côté serveur
- Protection des routes

## 🚀 Déploiement

### Frontend (Production)
```bash
npm run build
```

### Backend (Production)
```bash
# Utiliser Gunicorn pour la production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📝 Notes importantes

- Assurez-vous que Firebase est correctement configuré
- Le backend doit être démarré avant le frontend
- Les résultats se mettent à jour automatiquement toutes les 30 secondes
- Chaque étudiant ne peut voter qu'une seule fois

## 🤝 Contribution

Pour contribuer au projet :

1. Fork le repository
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📞 Support

Pour toute question ou problème, contactez l'équipe de développement.

---

**INFAS 35e Promotion PGP** - Système de vote étudiant 