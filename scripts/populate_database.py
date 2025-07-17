#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to populate the database with all classes and subjects,
then link them in the Enseignement table.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Classe, Cours, Enseignement, User

# List of all classes
CLASSES = [
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

def populate_database():
    """Populate the database with all classes and subjects, then link them."""
    
    with app.app_context():
        # Current academic year
        current_year = datetime.now().year
        academic_year = f"{current_year-1}-{current_year}" if datetime.now().month < 9 else f"{current_year}-{current_year+1}"
        
        # Get a default teacher (admin user or first teacher)
        default_teacher = User.query.filter_by(role='admin').first()
        if not default_teacher:
            default_teacher = User.query.filter_by(role='enseignant').first()
        if not default_teacher:
            default_teacher = User.query.first()  # Fallback to any user
            
        if not default_teacher:
            print("Error: No users found in the database to assign as teachers.")
            return
            
        print(f"Using default teacher: {default_teacher.nom} {default_teacher.prenom} (ID: {default_teacher.id})")
        print(f"Academic year: {academic_year}")
        
        # 1. Add all classes if they don't exist
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
                    capacite=30
                )
                db.session.add(new_class)
                classes_added += 1
                
        db.session.commit()
        print(f"Added {classes_added} new classes.")
        
        # 2. Add all subjects if they don't exist
        subjects_added = 0
        
        # Get existing course codes
        existing_codes = [c.code for c in Cours.query.all()]
        print(f"Found {len(existing_codes)} existing course codes")
        
        # Process each subject individually with separate commits
        for idx, subject_name in enumerate(SUBJECTS):
            try:
                # Check if subject already exists by name
                existing_subject = Cours.query.filter_by(nom=subject_name).first()
                if existing_subject:
                    print(f"Subject already exists: {subject_name}")
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
                
                print(f"Adding subject: {subject_name} with code: {code}")
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
                
            except Exception as e:
                print(f"Error adding subject {subject_name}: {str(e)}")
                db.session.rollback()
                
        db.session.commit()
        print(f"Added {subjects_added} new subjects.")
        
        # 3. Link all classes with all subjects in the Enseignement table
        classes = Classe.query.all()
        subjects = Cours.query.all()
        
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
                    # Create new Enseignement entry
                    new_enseignement = Enseignement(
                        classe_id=classe.id,
                        cours_id=subject.id,
                        professeur_id=default_teacher.id,
                        annee_scolaire=academic_year
                    )
                    db.session.add(new_enseignement)
                    enseignements_added += 1
                    
        db.session.commit()
        print(f"Added {enseignements_added} new enseignements.")
        print("Database population complete!")

if __name__ == "__main__":
    populate_database()
