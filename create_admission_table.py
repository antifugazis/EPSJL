#!/usr/bin/env python3
"""
Script pour créer la table resultats_admission dans la base de données
Usage: python create_admission_table.py
"""

from app import app, db
from models import ResultatAdmission

def create_admission_table():
    """Créer la table resultats_admission"""
    
    print("🔧 Création de la table resultats_admission...")
    
    with app.app_context():
        # Créer toutes les tables (y compris resultats_admission)
        db.create_all()
        print("✅ Table resultats_admission créée avec succès!")
        
        # Vérifier que la table existe
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'resultats_admission' in tables:
            print("\n✅ SUCCÈS: La table 'resultats_admission' est prête à être utilisée!")
            print("\n📊 Colonnes de la table:")
            columns = inspector.get_columns('resultats_admission')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("\n❌ ERREUR: La table 'resultats_admission' n'a pas été créée")
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("  CRÉATION DE LA TABLE RÉSULTATS D'ADMISSION")
    print("=" * 60)
    print()
    
    success = create_admission_table()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migration terminée avec succès!")
        print("\nVous pouvez maintenant:")
        print("  1. Démarrer l'application: python app.py")
        print("  2. Vous connecter en tant qu'admin")
        print("  3. Aller dans 'Résultats d'Admission'")
        print("  4. Ajouter des résultats d'admission!")
        print("\n📍 Page publique: http://localhost:8000/admission")
    else:
        print("❌ La migration a échoué")
        print("Vérifiez les erreurs ci-dessus")
    print("=" * 60)
