from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='parent')
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Eleve model
class Eleve(db.Model):
    __tablename__ = 'eleves'
    
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    lieu_naissance = db.Column(db.String(100), nullable=False)
    sexe = db.Column(db.String(1), nullable=False)
    adresse = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo = db.Column(db.String(255))
    date_inscription = db.Column(db.Date, default=datetime.now)
    actif = db.Column(db.Boolean, default=True)
    
    # Relationships
    classe = db.relationship('Classe', backref=db.backref('eleves', lazy=True))
    parent = db.relationship('User', backref=db.backref('enfants', lazy=True))
    
    def __repr__(self):
        return f'<Eleve {self.matricule}: {self.nom} {self.prenom}>'

# Classe model
class Classe(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    niveau = db.Column(db.String(20), nullable=False)
    annee_scolaire = db.Column(db.String(9), nullable=False)
    capacite = db.Column(db.Integer, default=30)
    salle = db.Column(db.String(20))
    
    def __repr__(self):
        return f'<Classe {self.nom}>'

# Cours model
class Cours(db.Model):
    __tablename__ = 'cours'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    coefficient = db.Column(db.Float, default=1.0)
    
    # Relationships
    enseignements = db.relationship('Enseignement', backref='cours', lazy=True)
    
    def __repr__(self):
        return f'<Cours {self.code}: {self.nom}>'

# Enseignement model (association between Cours, Classe, and Professeur)
class Enseignement(db.Model):
    __tablename__ = 'enseignements'
    
    id = db.Column(db.Integer, primary_key=True)
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    professeur_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    annee_scolaire = db.Column(db.String(9), nullable=False)
    
    # Relationships
    classe = db.relationship('Classe', backref=db.backref('enseignements', lazy=True))
    professeur = db.relationship('User', backref=db.backref('enseignements', lazy=True))
    
    def __repr__(self):
        return f'<Enseignement {self.cours.code} - {self.classe.nom}>'

# Presence model
class Presence(db.Model):
    __tablename__ = 'presences'
    
    id = db.Column(db.Integer, primary_key=True)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id'), nullable=False)
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(10), nullable=False)  # present, absent, retard, excuse
    notes = db.Column(db.Text)
    
    # Relationships
    eleve = db.relationship('Eleve', backref=db.backref('presences', lazy=True))
    cours = db.relationship('Cours', backref=db.backref('presences', lazy=True))
    
    def __repr__(self):
        return f'<Presence {self.eleve.matricule} - {self.date} - {self.statut}>'

# Note model
class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id'), nullable=False)
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id'), nullable=False)
    valeur = db.Column(db.Float, nullable=False)
    sur = db.Column(db.Float, default=100.0)
    type = db.Column(db.String(20), nullable=False)  # devoir, examen, projet
    trimestre = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    commentaire = db.Column(db.Text)
    
    # Relationships
    eleve = db.relationship('Eleve', backref=db.backref('notes', lazy=True))
    cours = db.relationship('Cours', backref=db.backref('notes', lazy=True))
    
    def __repr__(self):
        return f'<Note {self.eleve.matricule} - {self.cours.code} - {self.valeur}/{self.sur}>'

# Paiement model
class Paiement(db.Model):
    __tablename__ = 'paiements'
    
    id = db.Column(db.Integer, primary_key=True)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    frais_id = db.Column(db.Integer, db.ForeignKey('frais.id'), nullable=False)
    methode = db.Column(db.String(20), nullable=False)  # espèces, chèque, virement
    reference = db.Column(db.String(50))
    date = db.Column(db.Date, nullable=False)
    recu_par = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    commentaire = db.Column(db.Text)
    
    # Relationships
    eleve = db.relationship('Eleve', backref=db.backref('paiements', lazy=True))
    recepteur = db.relationship('User', backref=db.backref('paiements_recus', lazy=True))
    frais = db.relationship('Frais', backref=db.backref('paiements', lazy=True))
    
    def __repr__(self):
        return f'<Paiement {self.eleve.matricule} - {self.montant} - {self.frais.type if self.frais else "N/A"}>'

# Evenement model
class Evenement(db.Model):
    __tablename__ = 'evenements'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time)
    heure_fin = db.Column(db.Time)
    lieu = db.Column(db.String(100))
    type = db.Column(db.String(50))  # réunion, fête, examen, etc.
    cree_par = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    createur = db.relationship('User', backref=db.backref('evenements', lazy=True))
    
    def __repr__(self):
        return f'<Evenement {self.titre} - {self.date}>'

# Annonce model
class Annonce(db.Model):
    __tablename__ = 'annonces'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.now)
    date_expiration = db.Column(db.Date)
    public = db.Column(db.Boolean, default=True)
    important = db.Column(db.Boolean, default=False)
    

    
    def __repr__(self):
        return f'<Annonce {self.titre}>'

# Document model
class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    fichier = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50))  # bulletin, certificat, etc.
    date_creation = db.Column(db.DateTime, default=datetime.now)
    cree_par = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleves.id'))
    
    # Relationships
    createur = db.relationship('User', backref=db.backref('documents', lazy=True))
    eleve = db.relationship('Eleve', backref=db.backref('documents', lazy=True))
    
    def __repr__(self):
        return f'<Document {self.titre}>'

# Frais model (school fees)
class Frais(db.Model):
    __tablename__ = 'frais'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # frais de scolarité, uniforme, etc.
    description = db.Column(db.Text)
    montant = db.Column(db.Float, nullable=False)
    annee_scolaire = db.Column(db.String(9), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    date_echeance = db.Column(db.Date)
    
    # Relationships
    classe = db.relationship('Classe', backref=db.backref('frais', lazy=True))
    
    def __repr__(self):
        return f'<Frais {self.type} - {self.montant} HTG>'

# Inscription model (pour les demandes d'inscription en ligne)
class Inscription(db.Model):
    __tablename__ = 'inscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    # Informations de l'élève
    prenom_eleve = db.Column(db.String(100), nullable=False)
    nom_eleve = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    lieu_naissance = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(20), nullable=False)
    niveau_demande = db.Column(db.String(50), nullable=False)
    ancienne_classe = db.Column(db.String(100), nullable=True)
    promotion = db.Column(db.String(20), nullable=True)
    
    # Informations parent/tuteur 1
    parent1_nom = db.Column(db.String(100), nullable=False)
    parent1_lien = db.Column(db.String(50), nullable=False)
    parent1_telephone = db.Column(db.String(20), nullable=False)
    parent1_email = db.Column(db.String(120), nullable=False)
    
    # Informations parent/tuteur 2 (optionnel)
    parent2_nom = db.Column(db.String(100))
    parent2_lien = db.Column(db.String(50))
    parent2_telephone = db.Column(db.String(20))
    parent2_email = db.Column(db.String(120))
    
    # Informations complémentaires
    adresse = db.Column(db.String(255), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    pays = db.Column(db.String(100), nullable=False, default='Haïti')
    langues_parlees = db.Column(db.String(255))  # Liste des langues séparées par des virgules
    commentaires = db.Column(db.Text)
    
    # Documents (chemins des fichiers)
    acte_naissance = db.Column(db.String(255))
    bulletins_notes = db.Column(db.String(500))  # Chemins multiples séparés par des points-virgules
    photo_identite = db.Column(db.String(255))
    recu_paiement = db.Column(db.String(255))  # Reçu de paiement des frais d'inscription
    
    # Statut de la demande
    statut = db.Column(db.String(20), default='en_attente')  # en_attente, approuvee, rejetee, completee
    date_soumission = db.Column(db.DateTime, default=datetime.now)
    date_traitement = db.Column(db.DateTime)
    notes_admin = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Inscription {self.prenom_eleve} {self.nom_eleve} - {self.niveau_demande}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'eleve': f'{self.prenom_eleve} {self.nom_eleve}',
            'date_naissance': self.date_naissance.strftime('%Y-%m-%d') if self.date_naissance else None,
            'niveau_demande': self.niveau_demande,
            'parent1': self.parent1_nom,
            'parent1_telephone': self.parent1_telephone,
            'statut': self.statut,
            'date_soumission': self.date_soumission.strftime('%Y-%m-%d %H:%M') if self.date_soumission else None
        }

# Contact model (pour les messages du formulaire de contact)
class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    sujet = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.now)
    lu = db.Column(db.Boolean, default=False)
    traite = db.Column(db.Boolean, default=False)
    notes_admin = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Contact {self.nom} - {self.sujet}>'

# News model (pour le bandeau d'actualités)
class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # Higher number = higher priority
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<News {self.id}: {self.content[:30]}...>'

# Article model (pour les actualités complètes avec images)
class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    description_courte = db.Column(db.String(500))
    contenu = db.Column(db.Text, nullable=False)
    image_couverture = db.Column(db.String(255))
    categorie = db.Column(db.String(50))  # vie-scolaire, annonces, culture, celebrations
    date_evenement = db.Column(db.Date)
    auteur_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.now)
    date_modification = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    vues = db.Column(db.Integer, default=0)
    
    # Relationships
    auteur = db.relationship('User', backref=db.backref('articles', lazy=True))
    
    def __repr__(self):
        return f'<Article {self.titre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titre': self.titre,
            'slug': self.slug,
            'description_courte': self.description_courte,
            'contenu': self.contenu,
            'image_couverture': self.image_couverture,
            'categorie': self.categorie,
            'date_evenement': self.date_evenement.strftime('%Y-%m-%d') if self.date_evenement else None,
            'auteur': f"{self.auteur.prenom} {self.auteur.nom}" if self.auteur else None,
            'actif': self.actif,
            'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M') if self.date_creation else None,
            'vues': self.vues
        }

# Resultat Admission model (pour les demandes d'admission/examen)
class ResultatAdmission(db.Model):
    __tablename__ = 'resultats_admission'
    
    id = db.Column(db.Integer, primary_key=True)
    type_examen = db.Column(db.String(50), nullable=False)  # Examen 9AF, Bac, Admission
    nom_complet = db.Column(db.String(200), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    contact = db.Column(db.String(200), nullable=False)  # WhatsApp ou Email
    statut = db.Column(db.String(20), default='en_attente')  # en_attente, approuve, rejete
    date_soumission = db.Column(db.DateTime, default=datetime.now)
    publie = db.Column(db.Boolean, default=False)
    notes_admin = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ResultatAdmission {self.nom_complet} - {self.type_examen}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'type_examen': self.type_examen,
            'nom_complet': self.nom_complet,
            'date_naissance': self.date_naissance.strftime('%Y-%m-%d') if self.date_naissance else None,
            'contact': self.contact,
            'statut': self.statut,
            'date_soumission': self.date_soumission.strftime('%Y-%m-%d %H:%M') if self.date_soumission else None,
            'publie': self.publie
        }



# Archive Dossier model (pour la gestion des dossiers d'archives)
class ArchiveDossier(db.Model):
    __tablename__ = 'archive_dossiers'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    photo_couverture = db.Column(db.String(255))
    date_creation = db.Column(db.DateTime, default=datetime.now)
    nombre_fichiers = db.Column(db.Integer, default=0)
    informations_supplementaires = db.Column(db.Text)
    sauvegarde_serveur = db.Column(db.Boolean, default=True)  # True = serveur, False = local
    confidentiel = db.Column(db.Boolean, default=False)
    code_pin = db.Column(db.String(255))  # Hashé si confidentiel
    cree_par = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_modification = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    supprime = db.Column(db.Boolean, default=False)
    date_suppression = db.Column(db.DateTime)
    
    # Relationships
    createur = db.relationship('User', backref=db.backref('archive_dossiers', lazy=True))
    fichiers = db.relationship('ArchiveFichier', backref='dossier', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ArchiveDossier {self.nom}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'photo_couverture': self.photo_couverture,
            'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M') if self.date_creation else None,
            'nombre_fichiers': self.nombre_fichiers,
            'informations_supplementaires': self.informations_supplementaires,
            'sauvegarde_serveur': self.sauvegarde_serveur,
            'confidentiel': self.confidentiel,
            'date_modification': self.date_modification.strftime('%Y-%m-%d %H:%M') if self.date_modification else None,
            'createur': self.createur.username if self.createur else None
        }

# Archive Fichier model (pour les fichiers dans les dossiers)
class ArchiveFichier(db.Model):
    __tablename__ = 'archive_fichiers'
    
    id = db.Column(db.Integer, primary_key=True)
    dossier_id = db.Column(db.Integer, db.ForeignKey('archive_dossiers.id'), nullable=False)
    nom_document = db.Column(db.String(200), nullable=False)
    photo_couverture = db.Column(db.String(255))
    date_ajout = db.Column(db.DateTime, default=datetime.now)
    fichier_path = db.Column(db.String(500), nullable=False)  # Chemin du fichier
    fichier_type = db.Column(db.String(50))  # Extension du fichier (pdf, docx, mp3, etc.)
    fichier_taille = db.Column(db.Integer)  # Taille en bytes
    note_additionnelle = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ArchiveFichier {self.nom_document}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'dossier_id': self.dossier_id,
            'nom_document': self.nom_document,
            'photo_couverture': self.photo_couverture,
            'date_ajout': self.date_ajout.strftime('%Y-%m-%d %H:%M') if self.date_ajout else None,
            'fichier_path': self.fichier_path,
            'fichier_type': self.fichier_type,
            'fichier_taille': self.fichier_taille,
            'note_additionnelle': self.note_additionnelle
        }

# Newsletter model (pour les inscriptions à la newsletter)
class Newsletter(db.Model):
    __tablename__ = 'newsletters'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.now)
    actif = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Newsletter {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'date_inscription': self.date_inscription.strftime('%Y-%m-%d %H:%M') if self.date_inscription else None,
            'actif': self.actif
        }

# Doleance model (pour les doléances/plaintes)
class Doleance(db.Model):
    __tablename__ = 'doleances'
    
    id = db.Column(db.Integer, primary_key=True)
    nom_complet_eleve = db.Column(db.String(200), nullable=False)
    classe = db.Column(db.String(50), nullable=False)
    telephone1 = db.Column(db.String(20), nullable=False)
    telephone2 = db.Column(db.String(20))
    email = db.Column(db.String(120))
    photo_recu = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=False)
    statut = db.Column(db.String(20), default='en_attente')  # en_attente, en_cours, resolu, rejete
    date_soumission = db.Column(db.DateTime, default=datetime.now)
    date_traitement = db.Column(db.DateTime)
    reponse_admin = db.Column(db.Text)
    traite_par = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationship
    admin = db.relationship('User', backref=db.backref('doleances_traitees', lazy=True))
    
    def __repr__(self):
        return f'<Doleance {self.id}: {self.nom_complet_eleve}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom_complet_eleve': self.nom_complet_eleve,
            'classe': self.classe,
            'telephone1': self.telephone1,
            'telephone2': self.telephone2,
            'email': self.email,
            'photo_recu': self.photo_recu,
            'description': self.description,
            'statut': self.statut,
            'date_soumission': self.date_soumission.strftime('%Y-%m-%d %H:%M') if self.date_soumission else None,
            'date_traitement': self.date_traitement.strftime('%Y-%m-%d %H:%M') if self.date_traitement else None,
            'reponse_admin': self.reponse_admin
        }
