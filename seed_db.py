"""
Database seeder script for École Presbytérale Saint Joseph de L'Asile
This script creates initial data for testing the application.
"""
from datetime import datetime, date, timedelta
from flask_bcrypt import Bcrypt
from app import app, db
from models import User, Classe, Eleve, Cours, Enseignement, Presence, Note, Paiement, Frais, Evenement, Annonce

bcrypt = Bcrypt()

def seed_database():
    """Seed the database with initial data"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if we already have users
        if User.query.count() > 0:
            print("Database already has data. Skipping seed.")
            return
        
        print("Seeding database...")
        
        # Create admin user
        admin_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
        admin = User(
            username="admin",
            email="admin@epsjl.ht",
            password_hash=admin_password,
            nom="Administrateur",
            prenom="Système",
            role="admin"
        )
        db.session.add(admin)
        
        # Create director user
        
        
        # Create classes
        classes = [
            Classe(nom="6ème A", niveau="6ème", annee_scolaire="2024-2025", capacite=30, salle="Salle 101"),
            Classe(nom="5ème A", niveau="5ème", annee_scolaire="2024-2025", capacite=30, salle="Salle 102"),
            Classe(nom="4ème A", niveau="4ème", annee_scolaire="2024-2025", capacite=30, salle="Salle 103"),
            Classe(nom="3ème A", niveau="3ème", annee_scolaire="2024-2025", capacite=30, salle="Salle 104"),
            Classe(nom="Seconde A", niveau="Seconde", annee_scolaire="2024-2025", capacite=25, salle="Salle 201"),
            Classe(nom="Première A", niveau="Première", annee_scolaire="2024-2025", capacite=25, salle="Salle 202"),
            Classe(nom="Terminale A", niveau="Terminale", annee_scolaire="2024-2025", capacite=25, salle="Salle 203")
        ]
        for classe in classes:
            db.session.add(classe)
        
        # Commit classes to get their IDs
        db.session.commit()


        # Create courses
        cours = [
            Cours(code="MATH", nom="Mathématiques", description="Cours de mathématiques", coefficient=2.0),
            Cours(code="FRA", nom="Français", description="Cours de français", coefficient=2.0),
            Cours(code="ANG", nom="Anglais", description="Cours d'anglais", coefficient=1.5),
            Cours(code="HIS", nom="Histoire", description="Cours d'histoire", coefficient=1.0),
            Cours(code="GEO", nom="Géographie", description="Cours de géographie", coefficient=1.0),
            Cours(code="PHY", nom="Physique", description="Cours de physique", coefficient=1.5),
            Cours(code="CHI", nom="Chimie", description="Cours de chimie", coefficient=1.5),
            Cours(code="BIO", nom="Biologie", description="Cours de biologie", coefficient=1.5),
            Cours(code="INF", nom="Informatique", description="Cours d'informatique", coefficient=1.0),
            Cours(code="EPS", nom="Éducation Physique", description="Cours d'éducation physique", coefficient=1.0)
        ]
        for c in cours:
            db.session.add(c)
        
        # Commit courses to get their IDs
        db.session.commit()
        
        
        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
