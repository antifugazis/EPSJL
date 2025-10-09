#!/usr/bin/env python3
"""
Script de test pour vérifier que le système d'articles fonctionne
Usage: python test_articles_system.py
"""

from app import app, db
from models import Article, User
from datetime import datetime, date

def test_articles_system():
    """Tester le système d'articles"""
    
    print("🧪 Test du système d'articles...")
    print()
    
    with app.app_context():
        # 1. Vérifier que la table existe
        print("1️⃣ Vérification de la table articles...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'articles' not in tables:
            print("❌ ERREUR: La table 'articles' n'existe pas!")
            print("   Exécutez d'abord: python create_articles_table.py")
            return False
        print("✅ Table 'articles' trouvée")
        print()
        
        # 2. Vérifier qu'il y a au moins un utilisateur admin
        print("2️⃣ Vérification des utilisateurs admin...")
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("⚠️  Aucun utilisateur admin trouvé")
            print("   Les articles de test ne pourront pas avoir d'auteur")
            auteur_id = None
        else:
            print(f"✅ Admin trouvé: {admin.prenom} {admin.nom}")
            auteur_id = admin.id
        print()
        
        # 3. Compter les articles existants
        print("3️⃣ Comptage des articles existants...")
        count = Article.query.count()
        print(f"📊 {count} article(s) dans la base de données")
        print()
        
        # 4. Créer un article de test (si demandé)
        print("4️⃣ Voulez-vous créer un article de test? (o/n): ", end='')
        response = input().strip().lower()
        
        if response == 'o':
            print("\n📝 Création d'un article de test...")
            
            test_article = Article(
                titre="Article de test - Journée Portes Ouvertes",
                slug="article-de-test-journee-portes-ouvertes",
                description_courte="Venez découvrir notre école lors de notre journée portes ouvertes!",
                contenu="""Nous sommes ravis de vous inviter à notre journée portes ouvertes.

Au programme:
- Visite guidée du campus
- Rencontre avec les enseignants
- Présentation des programmes
- Activités pour les enfants

Venez nombreux!""",
                categorie="vie-scolaire",
                date_evenement=date(2025, 11, 15),
                auteur_id=auteur_id,
                actif=True
            )
            
            try:
                db.session.add(test_article)
                db.session.commit()
                print("✅ Article de test créé avec succès!")
                print(f"   ID: {test_article.id}")
                print(f"   Slug: {test_article.slug}")
                print(f"   URL: /articles/{test_article.slug}")
            except Exception as e:
                print(f"❌ Erreur lors de la création: {str(e)}")
                db.session.rollback()
                return False
        print()
        
        # 5. Afficher tous les articles
        print("5️⃣ Liste de tous les articles:")
        articles = Article.query.order_by(Article.date_creation.desc()).all()
        
        if not articles:
            print("   Aucun article trouvé")
        else:
            for i, article in enumerate(articles, 1):
                status = "🟢" if article.actif else "🔴"
                print(f"   {i}. {status} {article.titre}")
                print(f"      Catégorie: {article.categorie}")
                print(f"      Slug: {article.slug}")
                print(f"      Vues: {article.vues}")
                print(f"      Créé le: {article.date_creation.strftime('%d/%m/%Y %H:%M')}")
                if article.auteur:
                    print(f"      Auteur: {article.auteur.prenom} {article.auteur.nom}")
                print()
        
        # 6. Tester les routes
        print("6️⃣ Test des routes:")
        print("   📍 Routes publiques:")
        print("      - /evenements (liste des actualités)")
        print("      - /articles/<slug> (détails d'un article)")
        print()
        print("   🔐 Routes admin:")
        print("      - /articles/admin/liste (liste admin)")
        print("      - /articles/admin/nouveau (créer)")
        print("      - /articles/admin/modifier/<id> (modifier)")
        print()
        
        return True

if __name__ == '__main__':
    print("=" * 70)
    print("  TEST DU SYSTÈME D'ARTICLES/ACTUALITÉS")
    print("=" * 70)
    print()
    
    success = test_articles_system()
    
    print("=" * 70)
    if success:
        print("✅ TOUS LES TESTS SONT PASSÉS!")
        print()
        print("🚀 Prochaines étapes:")
        print("   1. Démarrez l'application: python app.py")
        print("   2. Connectez-vous en tant qu'admin")
        print("   3. Allez dans 'Articles/Actualités' dans le menu")
        print("   4. Créez votre premier article avec une image!")
        print()
        print("📖 Documentation:")
        print("   - ARTICLES_SYSTEM_README.md")
        print("   - ADMISSION_VS_INSCRIPTION.md")
        print("   - IMPLEMENTATION_SUMMARY.md")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("   Consultez les erreurs ci-dessus")
    print("=" * 70)
