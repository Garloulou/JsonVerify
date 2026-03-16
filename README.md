# 🔍 JsonVerify

Outil de vérification de taille de dialogues traduits au format JSON, conçu pour détecter les entrées trop longues avant intégration en jeu.

---

## ✨ Fonctionnalités

- 📄 Vérification d'un fichier JSON unique
- 📁 Vérification en lot d'un dossier entier
- ⚖️ Calcul de la taille en bytes selon un encodage custom (accents, balises de contrôle)
- 📝 Génération automatique de rapports de log et d'issues GitHub
- 🖥️ Interface graphique avec barre de progression et compteurs en temps réel

---

## 📦 Prérequis

- 🐍 Python 3.8 ou supérieur
- ✅ Aucune dépendance externe (librairie standard uniquement)

---

## 🚀 Lancement

```bash
python JsonVerify.py
```

---

## 🖱️ Utilisation

### 📄 Fichier unique

1. Cliquer sur **Charger JSON** et sélectionner un fichier `.json`
2. Cliquer sur **Verifier**
3. La console affiche uniquement les erreurs détectées
4. Si des erreurs sont présentes, le bouton **Copier Issue GitHub** devient actif

### 📁 Mode dossier

1. Cliquer sur **Verifier un dossier entier** et sélectionner un dossier
2. Tous les fichiers `.json` du dossier sont traités en séquence
3. Les résultats sont sauvegardés dans un sous-dossier `VERIFICATION_OUTPUT/`

---

## 📊 Résultats en mode dossier

Pour chaque fichier contenant des traductions, un sous-dossier est créé dans `VERIFICATION_OUTPUT/` :

```
VERIFICATION_OUTPUT/
└── nom_du_fichier/
    ├── logs_nom_du_fichier.txt     # 📋 Log complet (OK + erreurs)
    └── github_nom_du_fichier.txt  # 🐙 Rapport GitHub (seulement si erreurs)
```

---

## ⚙️ Calcul de la taille

La taille est calculée en bytes selon les règles suivantes :

- Chaque caractère standard compte pour **2 bytes**
- Les caractères accentués français (`é`, `è`, `ê`, etc.) sont remplacés par leurs équivalents encodés avant comptage
- Les balises de contrôle (`[SP]`, `[E1]`, `[NULL]`, `[U+XXXX]`, etc.) comptent pour **2 bytes** chacune
- La balise `[NULL]` est ignorée (0 byte)
- Une balise non reconnue est comptée caractère par caractère (2 bytes par caractère)

> 📐 La limite effective est : `data_size - 8`

---

## 💬 Messages console

| Message | Couleur | Signification |
|---|---|---|
| `TROP LONG ID x : y/z bytes` | 🔴 Rouge | Le dialogue dépasse la limite autorisée |
| `CRASH ID x : -1/z bytes` | 🔴 Rouge foncé | Balise `[` non fermée détectée dans le texte |
| `Tout est traduit et a la bonne taille !` | 🟢 Vert | Aucune erreur trouvée |

---

## 🐙 Format du rapport GitHub

Le bouton **Copier Issue GitHub** génère un texte prêt à coller dans une issue GitHub :

```
### 📂 Script affecte
* `nom_du_fichier.json`

### ⚠️ ID des phrases affectees
Les IDs suivants presentent des longueurs excessives :
> `12`, `47`, `103`

---
### 🛠️ Solution possible
* **Action :** Rendre les phrases plus courtes.
```
