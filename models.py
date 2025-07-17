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
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    date_inscription = db.Column(db.Date, default=datetime.utcnow)
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
    date = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(10), nullable=False)  # présent, absent, retard
    justifie = db.Column(db.Boolean, default=False)
    commentaire = db.Column(db.Text)
    
    # Relationships
    eleve = db.relationship('Eleve', backref=db.backref('presences', lazy=True))
    
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
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_expiration = db.Column(db.Date)
    cree_par = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    public = db.Column(db.Boolean, default=True)
    
    # Relationships
    createur = db.relationship('User', backref=db.backref('annonces', lazy=True))
    
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
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
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
        return f'<Frais {self.type} - {self.montant}>'
