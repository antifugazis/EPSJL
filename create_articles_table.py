#!/usr/bin/env python3
"""
Script pour créer la table articles dans la base de données
Usage: python create_articles_table.py
"""

from app import app, db
from models import Article
import os

def create_articles_table():
    """Créer la table articles et le dossier uploads"""
    
    print("🔧 Création de la table articles...")
    
    with app.app_context():
        # Créer toutes les tables (y compris articles)
        db.create_all()
        print("✅ Table articles créée avec succès!")
        
        # Créer le dossier uploads/articles si nécessaire
        upload_folder = 'static/uploads/articles'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            print(f"✅ Dossier {upload_folder} créé avec succès!")
        else:
            print(f"ℹ️  Le dossier {upload_folder} existe déjà")
        
        # Vérifier que la table existe
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'articles' in tables:
            print("\n✅ SUCCÈS: La table 'articles' est prête à être utilisée!")
            print("\n📊 Colonnes de la table:")
            columns = inspector.get_columns('articles')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("\n❌ ERREUR: La table 'articles' n'a pas été créée")
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("  CRÉATION DE LA TABLE ARTICLES")
    print("=" * 60)
    print()
    
    success = create_articles_table()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migration terminée avec succès!")
        print("\nVous pouvez maintenant:")
        print("  1. Démarrer l'application: python app.py")
        print("  2. Vous connecter en tant qu'admin")
        print("  3. Aller dans Articles/Actualités")
        print("  4. Créer votre premier article!")
    else:
        print("❌ La migration a échoué")
        print("Vérifiez les erreurs ci-dessus")
    print("=" * 60)
