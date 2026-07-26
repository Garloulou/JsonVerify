# JsonVerify

Outil de vérification de dialogues traduits au format JSON pour le projet de traduction française de Persona 2: Innocent Sin (PSP).

## Table des Matières

1. [À Propos](#à-propos)
2. [Installation](#installation)
3. [Utilisation](#utilisation)
4. [Calcul de Taille](#calcul-de-taille)
5. [Architecture](#architecture)
6. [Développement](#développement)
7. [Dépannage](#dépannage)
8. [Licence](#licence)

---

## À Propos

JsonVerify est un vérificateur automatisé de dialogues au format JSON. Le logiciel calcule la taille exacte des textes traduits selon un encodage spécifique et détecte les phrases dépassant les limites de taille autorisées.

Conçu pour fonctionner sur Windows, macOS et Linux. L'interface graphique offre un feedback en temps réel, support complet des accents français et génération automatique de rapports GitHub.

---

## Installation

### Windows

```bash
git clone https://github.com/Garloulou/JsonVerify.git
cd JsonVerify
start.bat
```

L'interface s'ouvre automatiquement sur http://localhost:5173

### macOS / Linux

```bash
git clone https://github.com/Garloulou/JsonVerify.git
cd JsonVerify
```

Terminal 1 (Backend) :
```bash
cd backend
pip install -r requirements.txt
python app.py
```

Terminal 2 (Frontend) :
```bash
cd frontend
npm install
npm run dev
```

Accès : http://localhost:5173

### Prérequis

- Python 3.8 ou supérieur
- Node.js 16 ou supérieur
- npm

---

## Utilisation

### Vérifier un fichier unique

1. Cliquez sur "Charger JSON"
2. Sélectionnez un fichier `.json`
3. Cliquez sur "Vérifier"
4. Les résultats s'affichent dans la console
5. Si des erreurs sont détectées, le bouton "Copier Issue" devient actif

### Vérifier un dossier

1. Cliquez sur "Sélectionner" dans la section Dossier
2. Choisissez un dossier contenant des fichiers JSON
3. Cliquez sur "Vérifier"
4. Tous les fichiers JSON sont traités séquentiellement
5. Les résultats agrégés s'affichent dans la console

### Comprendre les résultats

La console affiche chaque opération avec un timestamp :

```
[HH:MM:SS] Fichier chargé : dialogs.json
[HH:MM:SS] 42 entrées détectées
[HH:MM:SS] ERROR ID 15 : +8 bytes (4 chars en trop) | Max: ~30 chars
[HH:MM:SS] OK ID 23 : 45 bytes (22 chars)
```

Les statistiques indiquent :
- Dialogues : Nombre total d'entrées
- OK : Entrées conformes
- Erreurs : Entrées dépassant la limite
- Skippées : Entrées non traduites

---

## Calcul de Taille

### Règles d'Encodage

La taille est calculée en bytes selon ces règles précises :

**Caractères standards**
- Caractère standard = 2 bytes
- Accents français (é, è, ê, à, ù, ô, etc.) = remplacés par leurs équivalents encodés (3-4 bytes)

**Balises de Contrôle**
- [SP], [E1], [U+XXXX] = 2 bytes chacune
- [NULL] = 0 byte (ignorée)
- Balise mal fermée = -1 (crash détecté)

### Limite Effective

```
Taille maximale = data_size - 8 bytes
```

### Exemple

Fichier JSON :
```json
{
  "id": 42,
  "texte_fr": "Salut! Tu allez bien?",
  "data_size": 50
}
```

Calcul :
- Texte : "Salut! Tu allez bien?" (21 caractères)
- Taille : 21 × 2 = 42 bytes
- Limite : 50 - 8 = 42 bytes
- Résultat : Conforme

---

## Architecture

### Backend

Le backend expose une API REST via FastAPI sur le port 8000.

Structure :
```
backend/
├── app.py              # Serveur FastAPI
├── utils.py            # Calcul de taille personnalisé
└── requirements.txt    # Dépendances Python
```

Endpoints principaux :
- POST /api/load : Charger les données JSON
- POST /api/verify : Vérifier le fichier
- POST /api/process_directory : Traiter un dossier entier

### Frontend

L'interface est construite avec React et Vite.

Structure :
```
frontend/
├── src/
│   ├── App.jsx         # Composant principal
│   ├── index.css       # Styles Tailwind CSS
│   └── main.jsx        # Point d'entrée React
├── package.json
├── tailwind.config.js  # Configuration Tailwind
└── vite.config.js      # Configuration Vite
```

Stack technique :
- React 18
- Vite 4
- Tailwind CSS 3
- Framer Motion pour les animations
- Lucide React pour les icônes

---

## Développement

### Configuration initiale

```bash
git clone https://github.com/Garloulou/JsonVerify.git
cd JsonVerify

cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

### Lancer en développement

Windows :
```bash
start.bat
```

Manuellement :
```bash
# Terminal 1
cd backend
python app.py

# Terminal 2
cd frontend
npm run dev
```

### Build pour production

```bash
cd frontend
npm run build
```

Le dossier `dist/` contient les fichiers prêts au déploiement.

---

## Structure du Projet

```
JsonVerify/
├── backend/
│   ├── app.py
│   ├── utils.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── index.html
├── start.bat
├── README.md
└── LICENSE
```

---

## Dépannage

### Port déjà utilisé

Si le port 8000 ou 5173 est occupé :

Windows :
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

macOS / Linux :
```bash
lsof -i :8000
kill -9 <PID>
```

### Erreur de module Python

```bash
cd backend
pip install --upgrade -r requirements.txt
```

### npm install échoue

```bash
cd frontend
npm cache clean --force
npm install
```

---

## Licence

Ce projet est distribué sous la licence Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).

Conditions :
- Attribution : Vous devez mentionner le créateur original
- NonCommercial : Pas d'utilisation à des fins commerciales
- ShareAlike : Tout partage doit utiliser la même licence

Consultez le fichier LICENSE pour le texte complet.

---

## Crédits

Auteur principal : Garloulou

Contributeurs : Nolan

Inspiré par : P2 IS Tool et le projet Persona 2: Innocent Sin - Traduction Française

---

Pour signaler des problèmes ou proposer des améliorations, consultez les [Issues](https://github.com/Garloulou/JsonVerify/issues) du projet.
