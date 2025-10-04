# Système d'Administration EPSJL

## Vue d'ensemble

Un système d'administration moderne et complet pour gérer le site web de l'École Presbytérale Saint Joseph de L'Asile.

## Fonctionnalités

### 🔐 Authentification
- **Page de connexion sécurisée** (`/admin/login`)
- Authentification uniquement (pas d'inscription publique)
- Redirection automatique vers le dashboard après connexion
- Design moderne avec animations GSAP

### 📊 Dashboard Principal (`/admin/dashboard`)
- Vue d'ensemble des statistiques clés
- Cartes interactives pour :
  - Messages de contact
  - Inscriptions
  - Annonces actives
  - Élèves actifs
- Derniers messages et inscriptions
- Accès rapides aux actions fréquentes

### 📝 Section Formulaires (`/admin/formulaires`)
- **Gestion des messages de contact**
  - Affichage de tous les formulaires depuis `contact.html`
  - Filtres : Tous / Non lus / Non traités / Traités
  - Marquage lu/non lu
  - Marquage traité/non traité
  - Notes administratives
  - Suppression de messages
  - Réponse directe par email

### 📢 Section Contenu (`/admin/contenu`)
- **Gestion des Annonces**
  - Création, modification, suppression
  - Marquage public/privé
  - Marquage important
  - Date d'expiration automatique
  - Filtrage et recherche

- **Gestion des Actualités**
  - Création, modification, suppression
  - Système de priorité (0-100)
  - Activation/désactivation
  - Affichage dans le bandeau défilant

### 🎓 Section Admission et Inscription (`/admin/admissions`)
- **Gestion des demandes d'inscription**
  - Vue détaillée de chaque demande
  - Changement de statut :
    - En attente
    - Approuvée
    - Rejetée
    - Complétée
  - Informations complètes de l'élève et des parents
  - Notes administratives
  - Contact direct (email/téléphone)
  - Statistiques par statut

### 💰 Section Paiements (`/admin/paiements`)
- **Consultation des paiements**
  - Historique complet
  - Filtres par méthode (espèces, chèque, virement)
  - Statistiques financières
  - Détails par élève et type de frais

## Design et UX

### 🎨 Interface Moderne
- **Design élégant** avec Tailwind CSS
- **Animations fluides** avec GSAP
- **Interface responsive** pour tous les appareils
- **Cartes interactives** avec effets hover
- **Gradients modernes** pour les boutons et cartes

### 🎭 Animations GSAP
- Animations d'entrée pour tous les éléments
- Transitions fluides entre les pages
- Effets de survol interactifs
- Animations de chargement

### 🧭 Navigation Intuitive
- **Sidebar moderne** avec icônes
- **Indicateur de page active**
- **Accès rapide** aux sections principales
- **Profil utilisateur** en bas de sidebar
- **Bouton de déconnexion** facilement accessible

## Structure des Fichiers

```
modules/
  └── admin.py                    # Routes et logique backend

templates/admin/
  ├── base_admin.html             # Template de base avec sidebar
  ├── login.html                  # Page de connexion
  ├── dashboard.html              # Dashboard principal
  ├── formulaires.html            # Liste des formulaires
  ├── view_contact.html           # Détails d'un message
  ├── contenu.html                # Gestion du contenu
  ├── nouvelle_annonce.html       # Créer une annonce
  ├── modifier_annonce.html       # Modifier une annonce
  ├── nouvelle_actualite.html     # Créer une actualité
  ├── modifier_actualite.html     # Modifier une actualité
  ├── admissions.html             # Liste des inscriptions
  ├── view_admission.html         # Détails d'une inscription
  └── paiements.html              # Liste des paiements
```

## Routes Principales

### Authentification
- `GET/POST /admin/login` - Connexion
- `GET /admin/logout` - Déconnexion

### Dashboard
- `GET /admin/dashboard` - Dashboard principal

### Formulaires
- `GET /admin/formulaires` - Liste des formulaires
- `GET /admin/formulaires/contact/<id>` - Détails d'un contact
- `POST /admin/formulaires/contact/<id>/status` - Mettre à jour le statut
- `POST /admin/formulaires/contact/<id>/notes` - Enregistrer les notes
- `DELETE /admin/formulaires/contact/<id>` - Supprimer un contact

### Contenu
- `GET /admin/contenu` - Liste du contenu
- `GET/POST /admin/contenu/annonce/nouvelle` - Créer une annonce
- `GET/POST /admin/contenu/annonce/<id>/modifier` - Modifier une annonce
- `DELETE /admin/contenu/annonce/<id>` - Supprimer une annonce
- `GET/POST /admin/contenu/actualite/nouvelle` - Créer une actualité
- `GET/POST /admin/contenu/actualite/<id>/modifier` - Modifier une actualité
- `DELETE /admin/contenu/actualite/<id>` - Supprimer une actualité

### Admissions
- `GET /admin/admissions` - Liste des inscriptions
- `GET /admin/admissions/<id>` - Détails d'une inscription
- `POST /admin/admissions/<id>/statut` - Mettre à jour le statut
- `DELETE /admin/admissions/<id>` - Supprimer une inscription

### Paiements
- `GET /admin/paiements` - Liste des paiements

## Sécurité

- ✅ Authentification requise pour toutes les routes
- ✅ Vérification du rôle admin avec décorateur `@admin_required`
- ✅ Protection CSRF avec Flask
- ✅ Validation des données côté serveur
- ✅ Gestion sécurisée des sessions

## Utilisation

### Accès au système
1. Naviguer vers `/admin/login`
2. Se connecter avec un compte admin
3. Redirection automatique vers le dashboard

### Gestion des messages de contact
1. Aller dans **Formulaires** > **Messages de contact**
2. Filtrer par statut si nécessaire
3. Cliquer sur "Voir" pour les détails
4. Marquer comme lu/traité
5. Ajouter des notes administratives
6. Répondre directement par email

### Gestion du contenu
1. Aller dans **Contenu**
2. Choisir **Annonces** ou **Actualités**
3. Créer, modifier ou supprimer du contenu
4. Configurer la visibilité et les priorités

### Gestion des admissions
1. Aller dans **Admissions**
2. Filtrer par statut
3. Consulter les détails de chaque demande
4. Changer le statut selon le traitement
5. Ajouter des notes pour le suivi

## Technologies Utilisées

- **Backend**: Flask (Python)
- **Frontend**: HTML5, Tailwind CSS
- **Animations**: GSAP 3.12.2
- **Base de données**: SQLAlchemy
- **Authentification**: Flask-Login

## Améliorations Futures Possibles

- [ ] Export des données en CSV/Excel
- [ ] Système de notifications en temps réel
- [ ] Statistiques avancées avec graphiques
- [ ] Recherche globale
- [ ] Historique des modifications
- [ ] Gestion des permissions par rôle
- [ ] API REST pour intégrations externes

## Support

Pour toute question ou problème, contactez l'administrateur système.
