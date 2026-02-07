# GitHub Viewer (Terminal Windows)

GitHub Viewer est un outil **100% terminal pour Windows** permettant de lier un dossier local à un dépôt GitHub et de **surveiller les changements**. Il simplifie la gestion des mises à jour entre ton projet local et ton repo distant.

---

## Fonctionnalités

- Lier un dossier local à un dépôt GitHub (public ou privé).  
- Surveiller le dépôt et le dossier local pour détecter les changements.  
- Proposer automatiquement de mettre à jour le dossier local ou le repo distant.  
- Choisir la branche à utiliser pour les mises à jour.  
- Gérer les dépôts privés via **token GitHub**, stocké de manière sécurisée.  
- Intégration complète avec l'environnement (variables d'environnement).  
- 100% terminal, aucune interface graphique nécessaire.  
- Compatible uniquement avec Windows (pour le moment).  

> 🔮 Dans les futures versions :  
> - Possibilité de lier plusieurs dossiers à un même dépôt.  
> - Configuration avancée par projet.

---

## Installation

1. Clonez ou téléchargez le projet dans un dossier local.  
2. Ouvrez un terminal PowerShell dans le dossier du projet.  
3. Assurez-vous d’avoir Python installé (recommandé Python 3.10+).  
4. Créez un environnement virtuel (optionnel mais recommandé) :

```powershell

python -m venv env
.\env\Scripts\activate
Installez les dépendances (si nécessaire) :

pip install -r requirements.txt
Utilisation
Lancez le script principal :

python src/main.py
Suivez les instructions du terminal :

Choisissez le dossier local à lier.

Indiquez le dépôt GitHub (URL).

Si le dépôt est privé, entrez votre token GitHub.

Choisissez la branche à suivre.

Le script surveillera automatiquement les changements dans le dossier local et sur le repo distant, et proposera de mettre à jour selon votre choix.

Structure du projet
V1.0.0/
├─ assets/           # Fichiers ressources (icônes, images, etc.)
├─ dist/             # Build/Nuitka (ignoré par Git)
├─ env/              # Environnement virtuel (ignoré par Git)
├─ src/              # Scripts Python
│  ├─ main.py        # Script principal
│  ├─ config.py      # Configuration
│  └─ ...            # Modules additionnels
├─ .gitignore        # Fichiers/dossiers ignorés
├─ build.bat         # Script de build Windows
├─ requirements.bat  # Script pour installer les dépendances
└─ README.md         # Documentation
Contribution
Pour le moment, ce projet est en version initiale. Les contributions sont les bienvenues :

Suggestions de nouvelles fonctionnalités.

Optimisation de la surveillance des changements.

Support multi-dossier et multi-projet.
