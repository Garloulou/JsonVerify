# Guide d'Installation - JsonVerify

## Configuration Initiale

### 1️⃣ Prérequis

Vérifiez que vous avez installé :

- **Python 3.8+** → [Télécharger](https://www.python.org/downloads/)
- **Node.js 16+** → [Télécharger](https://nodejs.org/)

**Sur Windows**, assurez-vous que Python et npm sont ajoutés au PATH.

### 2️⃣ Cloner le Dépôt

```bash
git clone https://github.com/Garloulou/JsonVerify.git
cd JsonVerify
```

### 3️⃣ Installation Automatique (Windows)

Double-cliquez sur **`start.bat`** et attendez que les deux fenêtres s'ouvrent.

### 4️⃣ Installation Manuelle (macOS / Linux)

**Terminal 1 - Backend :**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

Vous verrez : `Uvicorn running on http://127.0.0.1:8000`

**Terminal 2 - Frontend :**
```bash
cd frontend
npm install
npm run dev
```

Vous verrez : `Local: http://localhost:5173`

---

## Vérification

Ouvrez votre navigateur et allez sur **http://localhost:5173**

Vous devriez voir l'interface JsonVerify avec :
- Statut "Prêt"
- Boutons bleus et gradient cyan
- Console vide

Si oui → Installation réussie !

---

## Troubleshooting

### Python n'est pas reconnu

**Symptôme :** `'python' is not recognized as an internal or external command`

**Solution :**
1. Allez sur https://www.python.org/downloads/
2. Téléchargez et installez Python
3. Cochez : "Add Python to PATH"
4. Redémarrez votre ordinateur

### Node.js n'est pas reconnu

**Symptôme :** `'node' is not recognized as an internal or external command`

**Solution :**
1. Allez sur https://nodejs.org/
2. Téléchargez et installez Node.js LTS
3. Redémarrez votre ordinateur

### Port 8000 / 5173 déjà utilisé

**Symptôme :** `Address already in use`

**Solution Windows :**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Solution macOS / Linux :**
```bash
lsof -i :8000
kill -9 <PID>
```

### npm install échoue

**Symptôme :** Erreurs pendant `npm install`

**Solution :**
```bash
cd frontend
npm cache clean --force
rm -rf node_modules
npm install
```

### Erreur FastAPI

**Symptôme :** ModuleNotFoundError: No module named 'fastapi'

**Solution :**
```bash
cd backend
pip install --upgrade -r requirements.txt
```

---

## Première Utilisation

1. Ouvrez http://localhost:5173
2. Cliquez sur **"Charger JSON"**
3. Sélectionnez un fichier `.json`
4. Cliquez sur **"Vérifier"**
5. Vérifiez les résultats dans la console

---

## Déploiement (Production)

### Build Frontend

```bash
cd frontend
npm run build
```

Output : `frontend/dist/`

### Serveur Backend

Utilisez un serveur ASGI en production :

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

---

## Variables d'Environnement

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Port du backend
PORT=8000

# Mode debug
DEBUG=False

# CORS origins
CORS_ORIGINS=http://localhost:5173,https://votre-domaine.com
```

---

## Support

- **Issues** : https://github.com/Garloulou/JsonVerify/issues
- **Discussions** : https://github.com/Garloulou/JsonVerify/discussions

---

## Prochaines Étapes

- Lis le [README.md](README.md) pour l'utilisation complète
- Consulte la [Architecture](#) pour les détails techniques
- Rejoins la communauté P2IS sur Discord