"""
Script de test pour la section Archives
"""

from app import app, db
from models import User, ArchiveDossier, ArchiveFichier
from werkzeug.security import generate_password_hash
from datetime import datetime

def test_archives():
    with app.app_context():
        print("=" * 60)
        print("TEST DE LA SECTION ARCHIVES")
        print("=" * 60)
        
        # 1. Vérifier que les tables existent
        print("\n1. Vérification des tables...")
        try:
            dossiers_count = ArchiveDossier.query.count()
            fichiers_count = ArchiveFichier.query.count()
            print(f"   ✓ Table archive_dossiers existe ({dossiers_count} entrées)")
            print(f"   ✓ Table archive_fichiers existe ({fichiers_count} entrées)")
        except Exception as e:
            print(f"   ✗ Erreur: {e}")
            return False
        
        # 2. Vérifier qu'un utilisateur admin existe
        print("\n2. Vérification des utilisateurs...")
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"   ✓ Utilisateur admin trouvé: {admin.username}")
        else:
            print("   ⚠ Aucun utilisateur admin trouvé")
            print("   Création d'un utilisateur admin de test...")
            admin = User(
                username='admin_test',
                email='admin@test.com',
                password_hash=generate_password_hash('admin123'),
                nom='Admin',
                prenom='Test',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print(f"   ✓ Utilisateur admin créé: {admin.username}")
        
        # 3. Créer un dossier de test
        print("\n3. Création d'un dossier de test...")
        try:
            test_dossier = ArchiveDossier(
                nom="Dossier de Test",
                nombre_fichiers=0,
                informations_supplementaires="Ceci est un dossier de test créé automatiquement",
                sauvegarde_serveur=True,
                confidentiel=False,
                cree_par=admin.id
            )
            db.session.add(test_dossier)
            db.session.commit()
            print(f"   ✓ Dossier créé avec succès (ID: {test_dossier.id})")
        except Exception as e:
            print(f"   ✗ Erreur lors de la création: {e}")
            db.session.rollback()
            return False
        
        # 4. Créer un dossier confidentiel de test
        print("\n4. Création d'un dossier confidentiel de test...")
        try:
            test_dossier_conf = ArchiveDossier(
                nom="Dossier Confidentiel de Test",
                nombre_fichiers=0,
                informations_supplementaires="Dossier protégé par PIN: 1234",
                sauvegarde_serveur=True,
                confidentiel=True,
                code_pin=generate_password_hash('1234'),
                cree_par=admin.id
            )
            db.session.add(test_dossier_conf)
            db.session.commit()
            print(f"   ✓ Dossier confidentiel créé (ID: {test_dossier_conf.id})")
            print(f"   ℹ Code PIN: 1234")
        except Exception as e:
            print(f"   ✗ Erreur lors de la création: {e}")
            db.session.rollback()
            return False
        
        # 5. Vérifier les filtres
        print("\n5. Test des filtres...")
        try:
            tous = ArchiveDossier.query.filter_by(supprime=False).count()
            confidentiels = ArchiveDossier.query.filter_by(supprime=False, confidentiel=True).count()
            print(f"   ✓ Tous les dossiers: {tous}")
            print(f"   ✓ Dossiers confidentiels: {confidentiels}")
        except Exception as e:
            print(f"   ✗ Erreur: {e}")
            return False
        
        # 6. Test de suppression (mise à la corbeille)
        print("\n6. Test de la corbeille...")
        try:
            test_dossier.supprime = True
            test_dossier.date_suppression = datetime.now()
            db.session.commit()
            print(f"   ✓ Dossier déplacé vers la corbeille")
            
            # Restauration
            test_dossier.supprime = False
            test_dossier.date_suppression = None
            db.session.commit()
            print(f"   ✓ Dossier restauré")
        except Exception as e:
            print(f"   ✗ Erreur: {e}")
            db.session.rollback()
            return False
        
        # 7. Résumé
        print("\n" + "=" * 60)
        print("RÉSUMÉ DES TESTS")
        print("=" * 60)
        print(f"✓ Tous les tests sont passés avec succès!")
        print(f"\nDossiers créés:")
        print(f"  - {test_dossier.nom} (ID: {test_dossier.id})")
        print(f"  - {test_dossier_conf.nom} (ID: {test_dossier_conf.id}, PIN: 1234)")
        print(f"\nAccès à la section: http://localhost:8000/archives")
        print(f"Utilisateur admin: {admin.username}")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    success = test_archives()
    exit(0 if success else 1)
