# 🚀 ClipGenius AI - Guide de Lancement Local (100% GRATUIT)

## ✅ Modifications Effectuées

Le projet a été adapté pour fonctionner **100% gratuitement en local** :

1. ✅ **OpenAI remplacé** → Analyse heuristique gratuite pour le scoring viral
2. ✅ **AWS S3 remplacé** → Stockage local sur votre disque
3. ✅ **Stripe remplacé** → Système de codes d'activation
4. ✅ **Email configuré** → Resend avec votre clé API

## 📋 Prérequis

Installez ces logiciels :

1. **Python 3.11+** : https://www.python.org/downloads/
2. **Node.js 18+** : https://nodejs.org/
3. **PostgreSQL** : https://www.postgresql.org/download/
4. **Redis** : https://github.com/microsoftarchive/redis/releases (Windows)
5. **FFmpeg** : https://ffmpeg.org/download.html

## 🎯 Installation Pas à Pas

### Étape 1 : Configurer PostgreSQL

```powershell
# Créer la base de données
psql -U postgres
CREATE DATABASE clipgenius;
CREATE USER clipgenius WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE clipgenius TO clipgenius;
\q
```

### Étape 2 : Lancer Redis

```powershell
# Téléchargez et extrayez Redis pour Windows
# Puis lancez:
redis-server
```

### Étape 3 : Configurer le Backend

```powershell
cd "c:\Users\chado\Documents\AI Clip Maker\clipgenius\backend"

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
copy .env.example .env

# Éditer .env avec votre clé Resend
notepad .env
```

**Dans le fichier `.env`, modifiez :**
```
RESEND_API_KEY=re_XKcC4ddL_M1VyQk82tPZABWnQoQMj7HnJ
```

### Étape 4 : Initialiser la Base de Données

```powershell
# Dans backend/ avec venv activé
python -c "from models import init_db; init_db()"
```

### Étape 5 : Lancer le Backend

**Terminal 1 - API Backend:**
```powershell
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```powershell
cd backend
venv\Scripts\activate
celery -A workers.celery_config worker --loglevel=info --pool=solo
```

### Étape 6 : Lancer le Frontend

**Terminal 3 - Frontend:**
```powershell
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

## 🌐 Accès à l'Application

Une fois tout lancé :

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 🎟️ Codes d'Activation

Le système utilise des codes d'activation au lieu de Stripe. **5 codes sont déjà générés** dans :

`backend/activation_codes.json`

**Codes disponibles :**
1. `FREE-TRIAL-2024-A1B2`
2. `PREMIUM-ACCESS-C3D4`
3. `CLIPGENIUS-E5F6`
4. `ACTIVATE-NOW-G7H8`
5. `UNLOCK-POWER-I9J0`

**Pour utiliser un code :**
1. Créez un compte sur http://localhost:3000
2. Connectez-vous
3. Allez sur http://localhost:3000/dashboard/activate
4. Entrez un des codes ci-dessus
5. Votre compte devient PRO avec 100 crédits pour 30 jours !

## 📁 Structure des Dossiers de Stockage

Les vidéos sont stockées localement dans :

```
backend/
  storage/
    uploads/    # Vidéos uploadées
    clips/      # Clips générés
    temp/       # Fichiers temporaires
```

Ces dossiers sont créés automatiquement au premier upload.

## 🐛 Dépannage

### Problème : PostgreSQL ne se connecte pas
```powershell
# Vérifiez que PostgreSQL est lancé
net start postgresql-x64-15
```

### Problème : Redis ne démarre pas
```powershell
# Relancez Redis
redis-server
```

###  Problème : Erreur d'import FFmpeg
```powershell
# Vérifiez que FFmpeg est dans le PATH
ffmpeg -version
```

### Problème : Celery ne démarre pas sur Windows
```powershell
# Utilisez --pool=solo
celery -A workers.celery_config worker --loglevel=info --pool=solo
```

## 🎬 Premier Test

1. Connectez-vous sur http://localhost:3000
2. Activez votre compte avec un code
3. Allez sur "Upload"
4. Uploadez une vidéo (MP4, MOV...)
5. Attendez le traitement (quelques minutes)
6. Récupérez vos clips avec scoring viral !

## 💡 Fonctionnalités GRATUITES

✅ **Analyse Virale** - Scoring heuristique intelligent (sans API)
✅ **Transcription** - Whisper open-source
✅ **Détection Visage** - DeepFace gratuit
✅ **Sous-titres** - Génération automatique avec emojis
✅ **Recadrage 9:16** - Auto-reframing intelligent
✅ **Stockage Local** - Pas de frais S3
✅ **Codes d'activation** - Pas de Stripe nécessaire

## 📧 Emails

Les emails sont envoyés via Resend avec votre clé :
- Email de bienvenue à l'inscription
- Notification quand les clips sont prêts

## 🔧 Personnalisation

### Générer Plus de Codes

Vous pouvez ajouter des codes dans `backend/activation_codes.json` :

```json
{
  "code": "VOTRE-CODE-1234",
  "duration_days": 30,
  "used": false,
  "created_at": "2024-01-01T00:00:00",
  "used_by": null,
  "used_at": null
}
```

### Modifier la Durée des Codes

Changez `duration_days` pour la durée souhaitée (en jours).

## 📊 Monitoring

Pour surveiller les tâches Celery, vous pouvez installer Flower :

```powershell
pip install flower
celery -A workers.celery_config flower
```

Accès : http://localhost:5555

## 🎉 Félicitations !

Votre application ClipGenius AI est maintenant 100% gratuite et opérationnelle en local ! 🚀

**Aucun coût :**
- ❌ Pas d'OpenAI
- ❌ Pas d'AWS
- ❌ Pas de Stripe
- ✅ Tout en local et gratuit !
