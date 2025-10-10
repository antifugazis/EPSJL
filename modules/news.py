from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, News
from functools import wraps
from datetime import datetime

news_blueprint = Blueprint('news', __name__)

# Decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Accès refusé. Vous devez être administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@news_blueprint.route('/admin/news')
@login_required
@admin_required
def admin_news():
    """Page d'administration des actualités"""
    news_items = News.query.order_by(News.priority.desc(), News.date_created.desc()).all()
    return render_template('admin/news.html', news_items=news_items)

@news_blueprint.route('/admin/news/add', methods=['POST'])
@login_required
@admin_required
def add_news():
    """Ajouter une nouvelle actualité"""
    content = request.form.get('content')
    priority = request.form.get('priority', 0)
    
    if not content:
        flash('Le contenu de l\'actualité est requis', 'danger')
        return redirect(url_for('news.admin_news'))
    
    news_item = News(
        content=content,
        priority=int(priority),
        active=True
    )
    
    db.session.add(news_item)
    db.session.commit()
    
    flash('Actualité ajoutée avec succès', 'success')
    return redirect(url_for('news.admin_news'))

@news_blueprint.route('/admin/news/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_news(id):
    """Modifier une actualité existante"""
    news_item = News.query.get_or_404(id)
    
    content = request.form.get('content')
    priority = request.form.get('priority')
    active = 'active' in request.form
    
    if content:
        news_item.content = content
    
    if priority is not None:
        news_item.priority = int(priority)
    
    news_item.active = active
    news_item.date_updated = datetime.now()
    
    db.session.commit()
    
    flash('Actualité mise à jour avec succès', 'success')
    return redirect(url_for('news.admin_news'))

@news_blueprint.route('/admin/news/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_news(id):
    """Supprimer une actualité"""
    news_item = News.query.get_or_404(id)
    
    db.session.delete(news_item)
    db.session.commit()
    
    flash('Actualité supprimée avec succès', 'success')
    return redirect(url_for('news.admin_news'))

@news_blueprint.route('/api/news')
def get_news():
    """API pour récupérer les actualités actives"""
    news_items = News.query.filter_by(active=True).order_by(News.priority.desc(), News.date_created.desc()).all()
    return jsonify([{
        'id': item.id,
        'content': item.content
    } for item in news_items])

@news_blueprint.route('/admin/news/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_news(id):
    """Activer/désactiver une actualité"""
    news_item = News.query.get_or_404(id)
    news_item.active = not news_item.active
    
    db.session.commit()
    
    status = 'activée' if news_item.active else 'désactivée'
    flash(f'Actualité {status} avec succès', 'success')
    return redirect(url_for('news.admin_news'))
