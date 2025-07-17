# École Presbytérale Saint Joseph de L'Asile - Système de Gestion Scolaire

Un système de gestion scolaire complet pour l'École Presbytérale Saint Joseph de L'Asile, permettant de gérer les élèves, les cours, les présences, les notes, les finances et plus encore.

## Fonctionnalités

### Gestion des Élèves
- Inscription des élèves
- Gestion des profils élèves
- Recherche et filtrage des élèves
- Suivi des informations personnelles et académiques

### Gestion des Cours
- Création et assignation des cours
- Attribution des enseignants
- Suivi des inscriptions aux cours

### Suivi des Présences
- Enregistrement quotidien des présences par cours
- Rapports de présence avec statistiques
- Statuts multiples (présent, absent, retard, excusé)

### Gestion des Notes
- Saisie des notes par cours, trimestre et type d'évaluation
- Bulletins scolaires avec moyennes et classements
- Suivi des performances sur plusieurs périodes d'évaluation

### Gestion Financière
- Configuration des frais par classe et année scolaire
- Suivi des paiements avec différentes méthodes
- Rapports financiers et relevés de solde des élèves

### Authentification des Utilisateurs
- Contrôle d'accès basé sur les rôles (admin, directeur, enseignant, parent)
- Système sécurisé de connexion et d'inscription
- Gestion des profils utilisateurs

### Calendrier et Événements
- Planification des événements scolaires
- Visualisation du calendrier mensuel
- Gestion des différents types d'événements

### Communication
- Annonces et actualités
- Gestion des documents
- Partage d'informations avec la communauté scolaire

## Prérequis

- Python 3.7+
- MySQL 5.7+ ou MariaDB 10.3+
- pip (gestionnaire de paquets Python)

## Installation

1. Cloner le dépôt :
   ```
   git clone https://github.com/votre-nom/epsjl-gestion.git
   cd epsjl-gestion
   ```

2. Créer un environnement virtuel :
   ```
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```

4. Configurer la base de données :
   - Créer une base de données MySQL
   - Exécuter le script SQL fourni dans `database/schema.sql`
   - Configurer les variables d'environnement ou modifier `config.py`

5. Lancer l'application :
   ```
   python app.py
   ```

6. Accéder à l'application dans votre navigateur :
   ```
   http://localhost:5000
   ```

## Structure du Projet

```
EPSJL/
├── app.py                   # Application principale
├── config.py                # Configuration
├── requirements.txt         # Dépendances
├── static/                  # Fichiers statiques (CSS, JS, Images)
├── templates/               # Templates Jinja2
│   ├── base.html            # Template de base
│   ├── accueil.html         # Page d'accueil
│   ├── auth/                # Templates d'authentification
│   ├── eleves/              # Templates de gestion des élèves
│   ├── cours/               # Templates de gestion des cours
│   ├── finances/            # Templates de gestion financière
│   └── admin/               # Templates d'administration
└── modules/                 # Modules de l'application
    ├── __init__.py
    ├── auth.py              # Fonctions d'authentification
    ├── eleves.py            # Gestion des élèves
    ├── cours.py             # Gestion des cours
    ├── presence.py          # Suivi des présences
    ├── notes.py             # Gestion des notes
    ├── finances.py          # Gestion financière
    ├── rapports.py          # Rapports et analyses
    ├── calendrier.py        # Calendrier et événements
    └── communication.py     # Outils de communication
```

## Utilisateurs par défaut

Un utilisateur administrateur est créé par défaut :
- Nom d'utilisateur : `admin`
- Mot de passe : `admin123`

**Important** : Changez ce mot de passe immédiatement après la première connexion.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des pull requests ou à ouvrir des issues pour améliorer le système.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
