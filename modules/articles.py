from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Article, User
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')

UPLOAD_FOLDER = 'static/uploads/articles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_slug(titre):
    """Créer un slug à partir du titre"""
    slug = titre.lower()
    slug = re.sub(r'[àáâãäå]', 'a', slug)
    slug = re.sub(r'[èéêë]', 'e', slug)
    slug = re.sub(r'[ìíîï]', 'i', slug)
    slug = re.sub(r'[òóôõö]', 'o', slug)
    slug = re.sub(r'[ùúûü]', 'u', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = slug.strip('-')
    return slug

# Route pour afficher tous les articles (page publique)
@articles_bp.route('/')
def liste():
    categorie = request.args.get('categorie')
    query = Article.query.filter_by(actif=True)
    
    if categorie:
        query = query.filter_by(categorie=categorie)
    
    articles = query.order_by(Article.date_creation.desc()).all()
    return render_template('articles/liste.html', articles=articles, categorie_active=categorie)

# Route pour afficher un article
@articles_bp.route('/<slug>')
def details(slug):
    article = Article.query.filter_by(slug=slug, actif=True).first_or_404()
    
    # Incrémenter le compteur de vues
    article.vues += 1
    db.session.commit()
    
    # Articles similaires (même catégorie)
    articles_similaires = Article.query.filter(
        Article.id != article.id,
        Article.categorie == article.categorie,
        Article.actif == True
    ).order_by(Article.date_creation.desc()).limit(3).all()
    
    return render_template('articles/details.html', article=article, articles_similaires=articles_similaires)

# Route admin pour lister les articles
@articles_bp.route('/admin/liste')
def admin_liste():
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    articles = Article.query.order_by(Article.date_creation.desc()).all()
    return render_template('admin/articles/liste.html', articles=articles)

# Route admin pour créer un article
@articles_bp.route('/admin/nouveau', methods=['GET', 'POST'])
def admin_nouveau():
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        titre = request.form.get('titre')
        description_courte = request.form.get('description_courte')
        contenu = request.form.get('contenu')
        categorie = request.form.get('categorie')
        date_evenement = request.form.get('date_evenement')
        actif = 'actif' in request.form
        
        # Créer le slug
        slug = create_slug(titre)
        
        # Vérifier si le slug existe déjà
        existing = Article.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Gérer l'upload de l'image
        image_path = None
        if 'image_couverture' in request.files:
            file = request.files['image_couverture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                # Créer le dossier si nécessaire
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_path = filepath
        
        # Créer l'article
        article = Article(
            titre=titre,
            slug=slug,
            description_courte=description_courte,
            contenu=contenu,
            image_couverture=image_path,
            categorie=categorie,
            date_evenement=datetime.strptime(date_evenement, '%Y-%m-%d').date() if date_evenement else None,
            auteur_id=session.get('user_id'),
            actif=actif
        )
        
        db.session.add(article)
        db.session.commit()
        
        flash('Article créé avec succès!', 'success')
        return redirect(url_for('articles.admin_liste'))
    
    return render_template('admin/articles/nouveau.html')

# Route admin pour modifier un article
@articles_bp.route('/admin/modifier/<int:article_id>', methods=['GET', 'POST'])
def admin_modifier(article_id):
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'POST':
        article.titre = request.form.get('titre')
        article.description_courte = request.form.get('description_courte')
        article.contenu = request.form.get('contenu')
        article.categorie = request.form.get('categorie')
        date_evenement = request.form.get('date_evenement')
        article.date_evenement = datetime.strptime(date_evenement, '%Y-%m-%d').date() if date_evenement else None
        article.actif = 'actif' in request.form
        
        # Mettre à jour le slug si le titre a changé
        new_slug = create_slug(article.titre)
        if new_slug != article.slug:
            existing = Article.query.filter(Article.slug == new_slug, Article.id != article_id).first()
            if not existing:
                article.slug = new_slug
        
        # Gérer l'upload de la nouvelle image
        if 'image_couverture' in request.files:
            file = request.files['image_couverture']
            if file and file.filename and allowed_file(file.filename):
                # Supprimer l'ancienne image si elle existe
                if article.image_couverture and os.path.exists(article.image_couverture):
                    try:
                        os.remove(article.image_couverture)
                    except:
                        pass
                
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                article.image_couverture = filepath
        
        db.session.commit()
        flash('Article modifié avec succès!', 'success')
        return redirect(url_for('articles.admin_liste'))
    
    return render_template('admin/articles/modifier.html', article=article)

# Route admin pour supprimer un article
@articles_bp.route('/admin/supprimer/<int:article_id>', methods=['POST'])
def admin_supprimer(article_id):
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    article = Article.query.get_or_404(article_id)
    
    # Supprimer l'image si elle existe
    if article.image_couverture and os.path.exists(article.image_couverture):
        try:
            os.remove(article.image_couverture)
        except:
            pass
    
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Article supprimé avec succès'})
