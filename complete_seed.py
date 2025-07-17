#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Database Seeder for École Presbytérale Saint Joseph de L'Asile

This script combines functionality from:
- seed_db.py (users, basic data)
- populate_database.py (classes and subjects)
- populate_enseignements.py (linking classes and subjects)

It ensures a complete database setup with proper relationships between all entities.
"""
from datetime import datetime, date, timedelta
import random
import sys
import os
from flask_bcrypt import Bcrypt

# Add the parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (User, Classe, Eleve, Cours, Enseignement, Presence, 
                   Note, Paiement, Frais, Evenement, Annonce)

bcrypt = Bcrypt()

# List of all classes
CLASSES = [
    "1ère année fondamentale (1ère AF)",
    "2ème année fondamentale (2ème AF)",
    "3ème année fondamentale (3ème AF)",
    "4ème année fondamentale (4ème AF)",
    "5ème année fondamentale (5ème AF)",
    "6ème année fondamentale (6ème AF)",
    "7ème année fondamentale (7ème AF)",
    "8ème année fondamentale (8ème AF)",
    "9ème année fondamentale (9ème AF)",
    "Secondaire 1 (NS1)",
    "Secondaire 2 (NS2)",
    "Rhéto / Première (NS3)",
    "Philosophie / Terminale (NS4)"
]

# List of all subjects
SUBJECTS = [
    "Créole haïtien",
    "Français",
    "Mathématiques",
    "Sciences de la nature / Sciences expérimentales",
    "Sciences sociales",
    "Histoire d'Haïti",
    "Géographie",
    "Éducation civique",
    "Formation morale et civique",
    "Philosophie",
    "Anglais",
    "Espagnol",
    "Latin",
    "Physique",
    "Chimie",
    "Sciences de la vie et de la terre (SVT)",
    "Informatique",
    "Lecture / Dictée / Expression écrite",
    "Dessin",
    "Musique",
    "Arts plastiques",
    "Éducation artistique",
    "Éducation physique et sportive",
    "Religion / Catéchèse / Culture religieuse",
    "Technologie",
    "Technologie industrielle",
    "Électricité",
    "Électronique",
    "Mécanique",
    "Dessin technique",
    "Agriculture",
    "Comptabilité",
    "Économie",
    "Gestion",
    "Marketing",
    "Secrétariat / Bureautique",
    "Dactylographie",
    "Cuisine / Hôtellerie",
    "Couture / Coupe & couture",
    "Théâtre",
    "Danse",
    "Journalisme scolaire",
    "Éducation à l'environnement",
    "Éducation à la citoyenneté",
    "Projet personnel / Tutorat / Orientation scolaire",
    "Préparation aux examens / Études dirigées",
    "Statistiques",
    "Probabilités",
    "Géométrie descriptive",
    "Logique mathématique",
    "Culture générale",
    "Pratique professionnelle"
]

def seed_database():
    """Comprehensive database seeding function"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if we already have users
        if User.query.count() > 0:
            print("Database already has data.")
            choice = input("Do you want to continue seeding? This will add missing data but won't delete existing data. (y/n): ")
            if choice.lower() != 'y':
                print("Seeding aborted.")
                return
        
        print("Starting comprehensive database seeding...")
        
        # PART 1: SEED USERS
        print("\n--- SEEDING USERS ---")
        admin = seed_users()
        
        # PART 2: SEED CLASSES
        print("\n--- SEEDING CLASSES ---")
        class_objects = seed_classes()
        
        # PART 3: SEED SUBJECTS
        print("\n--- SEEDING SUBJECTS ---")
        subject_objects = seed_subjects()
        
        # PART 4: SEED ENSEIGNEMENTS (link classes and subjects)
        print("\n--- SEEDING ENSEIGNEMENTS ---")
        seed_enseignements(class_objects, subject_objects, admin)
        
        # PART 5: SEED SAMPLE STUDENTS
        print("\n--- SEEDING SAMPLE STUDENTS ---")
        students = seed_students(class_objects)
        
        # PART 6: SEED ADDITIONAL DATA (fees, payments, events, etc.)
        print("\n--- SEEDING ADDITIONAL DATA ---")
        seed_additional_data(admin, students)
        
        print("\nDatabase seeding completed successfully!")

def seed_users():
    """Create users if they don't exist"""
    # Create admin user
    admin = User.query.filter_by(username="admin").first()
    if not admin:
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
        print("Added admin user")
    
    # Create director user
    directeur = User.query.filter_by(username="directeur").first()
    if not directeur:
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
        print("Added director user")
    
    # Create teacher users
    prof_count = User.query.filter_by(role="professeur").count()
    if prof_count < 3:
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
            if not User.query.filter_by(username=prof.username).first():
                db.session.add(prof)
        print(f"Added {len(professeurs)} teacher users")
    
    # Create parent user
    parent = User.query.filter_by(username="parent").first()
    if not parent:
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
        print("Added parent user")
    
    # Commit users to get their IDs
    db.session.commit()
    return admin

def seed_classes():
    """Create all classes if they don't exist"""
    # Current academic year
    current_year = datetime.now().year
    academic_year = f"{current_year-1}-{current_year}" if datetime.now().month < 9 else f"{current_year}-{current_year+1}"
    
    class_objects = []
    classes_added = 0
    
    for class_name in CLASSES:
        # Extract niveau from class name (e.g., "2ème AF", "NS1")
        if "fondamentale" in class_name:
            niveau = class_name.split("(")[1].strip(")")
        else:
            niveau = class_name.split("(")[1].strip(")")
        
        # Check if class already exists
        existing_class = Classe.query.filter_by(nom=class_name).first()
        if not existing_class:
            new_class = Classe(
                nom=class_name,
                niveau=niveau,
                annee_scolaire=academic_year,
                capacite=30,
                salle=f"Salle {100 + classes_added}"
            )
            db.session.add(new_class)
            classes_added += 1
            class_objects.append(new_class)
        else:
            class_objects.append(existing_class)
    
    # Commit to get IDs
    db.session.commit()
    print(f"Added {classes_added} new classes")
    
    return class_objects

def seed_subjects():
    """Create all subjects if they don't exist"""
    # Get existing course codes
    existing_codes = [c.code for c in Cours.query.all()]
    print(f"Found {len(existing_codes)} existing course codes")
    
    subject_objects = []
    subjects_added = 0
    
    # Process each subject individually with separate commits
    for idx, subject_name in enumerate(SUBJECTS):
        try:
            # Check if subject already exists by name
            existing_subject = Cours.query.filter_by(nom=subject_name).first()
            if existing_subject:
                subject_objects.append(existing_subject)
                continue
                
            # Create a code from the first letters of each word
            base_code = ''.join(word[0].upper() for word in subject_name.split() if word[0].isalpha())
            if len(base_code) < 2:
                base_code = subject_name[:3].upper()
            
            # Ensure code is unique by adding a suffix if needed
            code = base_code
            suffix = 1
            while code in existing_codes:
                code = f"{base_code}{suffix}"
                suffix += 1
            
            # Add the new code to our tracking list
            existing_codes.append(code)
            
            new_subject = Cours(
                code=code,
                nom=subject_name,
                description=f"Cours de {subject_name}",
                coefficient=1.0
            )
            db.session.add(new_subject)
            
            # Commit after each subject to avoid batch integrity errors
            db.session.commit()
            subjects_added += 1
            subject_objects.append(new_subject)
            
        except Exception as e:
            print(f"Error adding subject {subject_name}: {str(e)}")
            db.session.rollback()
    
    print(f"Added {subjects_added} new subjects")
    return subject_objects

def seed_enseignements(classes, subjects, default_teacher):
    """Link all classes with all subjects in the Enseignement table"""
    # Current academic year
    current_year = datetime.now().year
    academic_year = f"{current_year-1}-{current_year}" if datetime.now().month < 9 else f"{current_year}-{current_year+1}"
    
    # Get all teachers
    teachers = User.query.filter_by(role='professeur').all()
    if not teachers:
        teachers = [default_teacher]  # Use admin as fallback
    
    enseignements_added = 0
    
    for classe in classes:
        for subject in subjects:
            # Check if this combination already exists
            existing = Enseignement.query.filter_by(
                classe_id=classe.id,
                cours_id=subject.id,
                annee_scolaire=academic_year
            ).first()
            
            if not existing:
                # Assign a random teacher
                teacher = random.choice(teachers)
                
                # Create new Enseignement entry
                new_enseignement = Enseignement(
                    classe_id=classe.id,
                    cours_id=subject.id,
                    professeur_id=teacher.id,
                    annee_scolaire=academic_year
                )
                db.session.add(new_enseignement)
                enseignements_added += 1
                
                # Commit in batches to avoid memory issues
                if enseignements_added % 50 == 0:
                    db.session.commit()
    
    # Final commit
    db.session.commit()
    print(f"Added {enseignements_added} new enseignements")

def seed_students(classes):
    """Create sample students for each class"""
    # Check if we already have students
    if Eleve.query.count() > 30:
        print("Database already has sufficient student data. Skipping student creation.")
        return Eleve.query.limit(20).all()
    
    # Sample names for generating students
    prenoms = ["Jean", "Marie", "Pierre", "Anne", "Paul", "Claire", "Michel", "Sophie", 
               "Louis", "Jeanne", "Marc", "Lucie", "François", "Isabelle", "André", "Hélène"]
    noms = ["Dupont", "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand",
            "Leroy", "Moreau", "Simon", "Laurent", "Michel", "Lefebvre", "Garcia", "David"]
    
    students_added = 0
    students = []
    
    for classe in classes:
        # Add 5-10 students per class
        num_students = random.randint(5, 10)
        for i in range(num_students):
            # Generate a unique matricule
            matricule = f"{classe.niveau[:2]}{datetime.now().year % 100}{100 + students_added}"
            
            # Create student
            prenom = random.choice(prenoms)
            nom = random.choice(noms)
            
            new_student = Eleve(
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                date_naissance=date(2000 + random.randint(5, 15), random.randint(1, 12), random.randint(1, 28)),
                lieu_naissance="Port-au-Prince",
                adresse="Rue principale",
                telephone=f"509{random.randint(10000000, 99999999)}",
                email=f"{prenom.lower()}.{nom.lower()}@example.com",
                sexe="M" if random.random() > 0.5 else "F",
                classe_id=classe.id,
                date_inscription=date.today() - timedelta(days=random.randint(30, 180)),
                actif=True
            )
            db.session.add(new_student)
            students.append(new_student)
            students_added += 1
            
            # Commit in batches
            if students_added % 20 == 0:
                db.session.commit()
    
    # Final commit
    db.session.commit()
    print(f"Added {students_added} new students")
    return students

def seed_additional_data(admin, students):
    """Create additional data like fees, payments, events, etc."""
    # Create fee types (Frais) if they don't exist
    if Frais.query.count() == 0:
        # Determine academic year
        current_year = datetime.now().year
        academic_year = f"{current_year-1}-{current_year}" if datetime.now().month < 9 else f"{current_year}-{current_year+1}"
        frais_list = [
            Frais(type="Frais de scolarité", montant=15000.0, description="Frais annuels de scolarité", annee_scolaire=academic_year),
            Frais(type="Frais d'inscription", montant=5000.0, description="Frais d'inscription annuels", annee_scolaire=academic_year),
            Frais(type="Frais d'uniforme", montant=3000.0, description="Uniforme scolaire", annee_scolaire=academic_year),
            Frais(type="Frais de cantine", montant=10000.0, description="Frais annuels de cantine", annee_scolaire=academic_year),
            Frais(type="Frais d'examen", montant=2000.0, description="Frais pour les examens", annee_scolaire=academic_year)
        ]
        for frais in frais_list:
            db.session.add(frais)
        db.session.commit()
        print(f"Added {len(frais_list)} fee types")
    else:
        frais_list = Frais.query.all()
    
    # Create some sample payments if they don't exist
    if Paiement.query.count() == 0 and students:
        payments_added = 0
        for eleve in students[:min(10, len(students))]:  # Just for the first 10 students
            paiement = Paiement(
                eleve_id=eleve.id,
                montant=5000.0,
                frais_id=frais_list[0].id,  # assign to "frais de scolarité"
                methode="espèces",
                reference=f"PAIE-{eleve.matricule}-{date.today().strftime('%Y%m%d')}",
                date=date.today() - timedelta(days=random.randint(1, 30)),
                recu_par=admin.id,
                commentaire="Premier versement"
            )
            db.session.add(paiement)
            payments_added += 1
        db.session.commit()
        print(f"Added {payments_added} sample payments")
    
    # Create events if they don't exist
    if Evenement.query.count() == 0:
        evenements = [
            Evenement(
                titre="Réunion des parents",
                description="Réunion d'information pour les parents d'élèves",
                date=date.today() + timedelta(days=10),
                heure_debut=datetime.strptime("18:00", "%H:%M").time(),
                heure_fin=datetime.strptime("20:00", "%H:%M").time(),
                lieu="Salle polyvalente",
                type="réunion",
                cree_par=admin.id
            ),
            Evenement(
                titre="Journée sportive",
                description="Compétitions sportives entre classes",
                date=date.today() + timedelta(days=20),
                heure_debut=datetime.strptime("09:00", "%H:%M").time(),
                heure_fin=datetime.strptime("16:00", "%H:%M").time(),
                lieu="Terrain de sport",
                type="activité",
                cree_par=admin.id
            ),
            Evenement(
                titre="Examens trimestriels",
                description="Période d'examens du premier trimestre",
                date=date.today() + timedelta(days=30),
                heure_debut=datetime.strptime("08:00", "%H:%M").time(),
                heure_fin=datetime.strptime("12:00", "%H:%M").time(),
                lieu="Toutes les salles",
                type="examen",
                cree_par=admin.id
            )
        ]
        for evt in evenements:
            db.session.add(evt)
        db.session.commit()
        print(f"Added {len(evenements)} events")
    
    # Create announcements if they don't exist
    if Annonce.query.count() == 0:
        annonces = [
            Annonce(
                titre="Bienvenue à l'année scolaire 2024-2025",
                contenu="Nous sommes heureux de vous accueillir pour cette nouvelle année scolaire. Nous vous souhaitons une excellente année pleine de réussite.",
                date_creation=datetime.now(),
                date_expiration=date.today() + timedelta(days=30),
                cree_par=admin.id,
                public=True
            ),
            Annonce(
                titre="Nouveaux horaires de la bibliothèque",
                contenu="La bibliothèque sera désormais ouverte de 8h à 17h du lundi au vendredi, et de 9h à 12h le samedi.",
                date_creation=datetime.now(),
                date_expiration=date.today() + timedelta(days=60),
                cree_par=admin.id,
                public=True
            ),
            Annonce(
                titre="Recrutement club de robotique",
                contenu="Le club de robotique recrute de nouveaux membres. Les élèves intéressés peuvent s'inscrire auprès du professeur d'informatique.",
                date_creation=datetime.now(),
                date_expiration=date.today() + timedelta(days=15),
                cree_par=admin.id,
                public=True
            )
        ]
        for annonce in annonces:
            db.session.add(annonce)
        db.session.commit()
        print(f"Added {len(annonces)} announcements")

if __name__ == "__main__":
    seed_database()
