#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to populate all classes with all subjects in the Enseignement table.
This ensures every class has access to every subject.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Classe, Cours, Enseignement, User

def populate_enseignements():
    """Populate the Enseignement table with all combinations of classes and subjects."""
    
    with app.app_context():
        # Get all classes and courses
        classes = Classe.query.all()
        cours = Cours.query.all()
        
        # Get a default teacher (admin user or first teacher)
        default_teacher = User.query.filter_by(role='admin').first()
        if not default_teacher:
            default_teacher = User.query.filter_by(role='enseignant').first()
        if not default_teacher:
            default_teacher = User.query.first()  # Fallback to any user
            
        if not default_teacher:
            print("Error: No users found in the database to assign as teachers.")
            return
            
        # Current academic year
        current_year = datetime.now().year
        academic_year = f"{current_year-1}-{current_year}" if datetime.now().month < 9 else f"{current_year}-{current_year+1}"
        
        # Counter for new entries
        new_count = 0
        existing_count = 0
        
        print(f"Found {len(classes)} classes and {len(cours)} subjects")
        print(f"Using default teacher: {default_teacher.nom} {default_teacher.prenom} (ID: {default_teacher.id})")
        print(f"Academic year: {academic_year}")
        print("Starting to populate enseignements...")
        
        # For each class and course combination
        for classe in classes:
            for course in cours:
                # Check if this combination already exists
                existing = Enseignement.query.filter_by(
                    classe_id=classe.id,
                    cours_id=course.id,
                    annee_scolaire=academic_year
                ).first()
                
                if not existing:
                    # Create new Enseignement entry
                    new_enseignement = Enseignement(
                        classe_id=classe.id,
                        cours_id=course.id,
                        professeur_id=default_teacher.id,
                        annee_scolaire=academic_year
                    )
                    db.session.add(new_enseignement)
                    new_count += 1
                else:
                    existing_count += 1
                    
        # Commit all changes
        db.session.commit()
        
        print(f"Done! Added {new_count} new enseignements. {existing_count} already existed.")

if __name__ == "__main__":
    populate_enseignements()
