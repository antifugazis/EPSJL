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
        directeur_password = bcrypt.generate_password_hash("directeur123").decode('utf-8')
        directeur = User(
            username="directeur",
            email="directeur@epsjl.ht",
            password_hash=directeur_password,
            nom="Dupont",
            prenom="Jean",
            role="directeur"
        )
        db.session.add(directeur)
        
        # Create teacher users
        professeur_password = bcrypt.generate_password_hash("prof123").decode('utf-8')
        professeurs = [
            User(
                username="prof_math",
                email="math@epsjl.ht",
                password_hash=professeur_password,
                nom="Mathieu",
                prenom="Pierre",
                role="professeur"
            ),
            User(
                username="prof_fr",
                email="francais@epsjl.ht",
                password_hash=professeur_password,
                nom="François",
                prenom="Marie",
                role="professeur"
            ),
            User(
                username="prof_sci",
                email="science@epsjl.ht",
                password_hash=professeur_password,
                nom="Laval",
                prenom="Claude",
                role="professeur"
            )
        ]
        for prof in professeurs:
            db.session.add(prof)
        
        # Create parent user
        parent_password = bcrypt.generate_password_hash("parent123").decode('utf-8')
        parent = User(
            username="parent",
            email="parent@example.com",
            password_hash=parent_password,
            nom="Parent",
            prenom="Test",
            role="parent"
        )
        db.session.add(parent)
        
        # Commit users to get their IDs
        db.session.commit()
        
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

        # Create fee types (Frais)
        frais_list = [
            Frais(type="frais de scolarité", description="Frais annuels de scolarité", montant=5000.0, annee_scolaire="2024-2025", classe_id=classes[0].id),
            Frais(type="uniforme", description="Frais pour uniforme scolaire", montant=1000.0, annee_scolaire="2024-2025", classe_id=classes[0].id),
        ]
        for f in frais_list:
            db.session.add(f)
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
        
        # Create students
        eleves = []
        for i in range(1, 31):
            classe_id = classes[0].id if i <= 15 else classes[1].id
            eleve = Eleve(
                matricule=f"E{2024}{i:04d}",
                nom=f"Nom{i}",
                prenom=f"Prenom{i}",
                date_naissance=date(2010, 1, 1) - timedelta(days=i*30),
                lieu_naissance="L'Asile",
                sexe="M" if i % 2 == 0 else "F",
                adresse=f"Adresse {i}, L'Asile",
                telephone=f"509-{i:08d}",
                email=f"eleve{i}@example.com",
                classe_id=classe_id,
                parent_id=parent.id if i <= 5 else None,
                date_inscription=date(2024, 8, 15),
                actif=True
            )
            eleves.append(eleve)
            db.session.add(eleve)
        
        # Commit students to get their IDs
        db.session.commit()
        
        # Create teacher assignments
        enseignements = [
            Enseignement(cours_id=cours[0].id, classe_id=classes[0].id, professeur_id=professeurs[0].id, annee_scolaire="2024-2025"),
            Enseignement(cours_id=cours[1].id, classe_id=classes[0].id, professeur_id=professeurs[1].id, annee_scolaire="2024-2025"),
            Enseignement(cours_id=cours[2].id, classe_id=classes[0].id, professeur_id=professeurs[2].id, annee_scolaire="2024-2025"),
            Enseignement(cours_id=cours[0].id, classe_id=classes[1].id, professeur_id=professeurs[0].id, annee_scolaire="2024-2025"),
            Enseignement(cours_id=cours[1].id, classe_id=classes[1].id, professeur_id=professeurs[1].id, annee_scolaire="2024-2025"),
            Enseignement(cours_id=cours[2].id, classe_id=classes[1].id, professeur_id=professeurs[2].id, annee_scolaire="2024-2025")
        ]
        for e in enseignements:
            db.session.add(e)
        
        # Create attendance records
        for eleve in eleves[:10]:  # Just for the first 10 students
            for i in range(5):  # For the past 5 days
                jour = date.today() - timedelta(days=i)
                if jour.weekday() < 5:  # Only for weekdays
                    presence = Presence(
                        eleve_id=eleve.id,
                        cours_id=enseignements[0].cours_id,  # Assign the first course for demonstration
                        date=jour,
                        statut="présent" if i % 5 != 0 else "absent",
                        notes="Absence non justifiée" if i % 5 == 0 else None
                    )
                    db.session.add(presence)
        
        # Create grades
        for eleve in eleves[:10]:  # Just for the first 10 students
            for c in cours[:3]:  # For the first 3 courses
                for i in range(1, 3):  # Two grades per course
                    note = Note(
                        eleve_id=eleve.id,
                        cours_id=c.id,
                        valeur=float(60 + (eleve.id % 40)),  # Random grade between 60 and 100
                        sur=100.0,
                        type="devoir" if i == 1 else "examen",
                        trimestre=1,
                        date=date.today() - timedelta(days=i*7),
                        commentaire="Bon travail" if eleve.id % 40 > 20 else "Peut mieux faire"
                    )
                    db.session.add(note)
        
        # Create payments
        for eleve in eleves[:5]:  # Just for the first 5 students
            paiement = Paiement(
                eleve_id=eleve.id,
                montant=5000.0,
                frais_id=frais_list[0].id,  # assign to "frais de scolarité"
                methode="espèces",
                reference=f"PAIE-{eleve.matricule}-{date.today().strftime('%Y%m%d')}",
                date=date.today() - timedelta(days=10),
                recu_par=admin.id,
                commentaire="Premier versement"
            )
            db.session.add(paiement)
        
        # Create events
        evenements = [
            Evenement(
                titre="Réunion des parents",
                description="Réunion d'information pour les parents d'élèves",
                date=date.today() + timedelta(days=10),
                heure_debut=datetime.strptime("18:00", "%H:%M").time(),
                heure_fin=datetime.strptime("20:00", "%H:%M").time(),
                lieu="Salle polyvalente",
                type="réunion",
                cree_par=directeur.id
            ),
            Evenement(
                titre="Journée sportive",
                description="Compétitions sportives entre classes",
                date=date.today() + timedelta(days=20),
                heure_debut=datetime.strptime("09:00", "%H:%M").time(),
                heure_fin=datetime.strptime("16:00", "%H:%M").time(),
                lieu="Terrain de sport",
                type="activité",
                cree_par=directeur.id
            ),
            Evenement(
                titre="Examens trimestriels",
                description="Période d'examens du premier trimestre",
                date=date.today() + timedelta(days=30),
                heure_debut=datetime.strptime("08:00", "%H:%M").time(),
                heure_fin=datetime.strptime("12:00", "%H:%M").time(),
                lieu="Toutes les salles",
                type="examen",
                cree_par=directeur.id
            )
        ]
        for evt in evenements:
            db.session.add(evt)
        
        # Create announcements
        annonces = [
            Annonce(
                titre="Bienvenue à l'année scolaire 2024-2025",
                contenu="Nous sommes heureux de vous accueillir pour cette nouvelle année scolaire. Nous vous souhaitons une excellente année pleine de réussite.",
                date_creation=datetime.now(),
                date_expiration=date.today() + timedelta(days=30),
                public=True,
                important=False
            ),
            Annonce(
                titre="Nouveaux horaires de la bibliothèque",
                contenu="La bibliothèque sera désormais ouverte de 8h à 17h du lundi au vendredi, et de 9h à 12h le samedi.",
                date_creation=datetime.now(),
                date_expiration=date.today() + timedelta(days=60),
                public=True,
                important=False
            ),
            Annonce(
                titre="Recrutement club de robotique",
                contenu="Le club de robotique recrute de nouveaux membres. Les élèves intéressés peuvent s'inscrire auprès du professeur d'informatique.",
                date_creation=datetime.now(),
                date_expiration=date.today() + timedelta(days=15),
                public=True,
                important=False
            )
        ]
        for annonce in annonces:
            db.session.add(annonce)
        
        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
