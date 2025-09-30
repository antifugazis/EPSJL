# Section Archives - Documentation

## Vue d'ensemble

La section **Archives** permet de stocker et gérer des documents de tous formats (DOCX, PDF, PPT, MP3, MP4, etc.) de manière organisée et sécurisée.

## Fonctionnalités principales

### 1. Gestion des dossiers

#### Création d'un dossier
- **Nom du dossier** : Nom descriptif pour identifier le dossier
- **Photo de couverture** : Image miniature affichée sur la carte du dossier
- **Date de création** : Automatiquement enregistrée
- **Nombre de fichiers** : Spécifiez combien de fichiers vous souhaitez ajouter
- **Informations supplémentaires** : Notes ou description du dossier

#### Options de sauvegarde
- **Emplacement** : 
  - Serveur (en ligne) - recommandé
  - Local (appareil uniquement)
- **Confidentialité** :
  - Public : Accessible à tous les utilisateurs autorisés
  - Confidentiel : Protégé par code PIN (minimum 4 caractères)

### 2. Gestion des fichiers

Pour chaque fichier dans un dossier, vous pouvez spécifier :
- **Nom du document** : Nom descriptif du fichier
- **Photo de couverture** : Miniature personnalisée (optionnel)
- **Date d'ajout** : Automatiquement enregistrée
- **Fichier** : Le document à uploader (tous formats acceptés)
- **Note additionnelle** : Informations supplémentaires sur le fichier

#### Formats acceptés
- **Documents** : PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, CSV, ODT, ODS, ODP
- **Images** : JPG, JPEG, PNG, GIF, BMP, SVG, WEBP
- **Audio** : MP3, WAV
- **Vidéo** : MP4, AVI, MOV, WMV, FLV
- **Archives** : ZIP, RAR, 7Z, TAR, GZ

### 3. Système de filtres

Les filtres permettent de naviguer facilement dans vos archives :

- **Tous** : Affiche tous les dossiers
- **Ajoutés récemment** : Dossiers créés il y a moins d'un mois
- **Modifiés récemment** : Dossiers modifiés il y a moins d'un mois
- **Confidentiel** : Uniquement les dossiers protégés par PIN

Le nombre d'éléments correspondants est affiché entre parenthèses pour chaque filtre.

### 4. Accès aux dossiers confidentiels

Les dossiers marqués comme confidentiels nécessitent un code PIN pour y accéder :
1. Cliquez sur le dossier confidentiel
2. Entrez le code PIN à 4 chiffres minimum
3. Une fois déverrouillé, vous avez accès pendant 1 heure

### 5. Corbeille

Les fichiers supprimés sont conservés pendant **30 jours** dans la corbeille :

#### Actions disponibles
- **Restaurer** : Récupérer un dossier supprimé
- **Supprimer définitivement** : Suppression permanente (admin/directeur uniquement)

#### Nettoyage automatique
Les dossiers dans la corbeille depuis plus de 30 jours sont automatiquement supprimés de façon permanente.

### 6. Export des données

Vous pouvez exporter la liste des dossiers dans plusieurs formats :

- **PDF** : Document formaté avec tableau
- **Excel** : Fichier .xlsx avec données structurées
- **DOCX** : Document Word avec tableau

L'export respecte le filtre actuellement sélectionné.

## Actions disponibles

### Sur la page principale
- **Voir** : Consulter les détails et fichiers d'un dossier
- **Modifier** : Mettre à jour les informations du dossier
- **Supprimer** : Déplacer vers la corbeille

### Dans les détails d'un dossier
- **Télécharger** : Télécharger un fichier individuel
- **Modifier le dossier** : Changer les paramètres
- **Supprimer le dossier** : Mettre à la corbeille

### Dans la corbeille
- **Restaurer** : Remettre le dossier dans les archives
- **Supprimer définitivement** : Suppression permanente (irréversible)

## Messages de confirmation

Toutes les actions importantes affichent des messages de confirmation :
- Nom du dossier concerné
- Action réalisée (création, modification, suppression, restauration)

## Permissions

### Utilisateurs standards
- Créer des dossiers
- Voir les dossiers non-confidentiels
- Accéder aux dossiers confidentiels avec le bon PIN
- Modifier leurs propres dossiers

### Administrateurs et Directeurs
- Toutes les permissions des utilisateurs standards
- Supprimer définitivement des dossiers de la corbeille
- Accès à tous les dossiers (avec PIN pour les confidentiels)

## Bonnes pratiques

1. **Organisation** : Utilisez des noms de dossiers descriptifs
2. **Sécurité** : Utilisez des codes PIN forts pour les dossiers confidentiels
3. **Photos de couverture** : Ajoutez des miniatures pour une meilleure identification visuelle
4. **Notes** : Documentez vos fichiers avec des notes additionnelles
5. **Nettoyage** : Vérifiez régulièrement la corbeille avant suppression définitive

## Accès à la section

La section Archives est accessible via :
- Menu principal (utilisateurs connectés) → Profil → Archives
- Menu mobile → Gestion → Archives
- URL directe : `/archives`

## Support technique

Pour toute question ou problème :
- Contactez l'administrateur système
- Consultez la documentation technique dans `/modules/archives.py`
