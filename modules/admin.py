from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime, date
from models import db, User, Contact, Inscription, Annonce, News, Paiement, Eleve

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Décorateur pour vérifier que l'utilisateur est admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTHENTIFICATION ====================

@admin_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion admin"""
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password) and user.role == 'admin':
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Identifiants incorrects ou accès non autorisé.', 'error')
    
    return render_template('admin/login.html')

@admin_blueprint.route('/logout')
@login_required
def logout():
    """Déconnexion admin"""
    logout_user()
    return redirect(url_for('admin.login'))

# ==================== DASHBOARD PRINCIPAL ====================

@admin_blueprint.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard principal de l'administration"""
    # Statistiques générales
    stats = {
        'contacts_non_lus': Contact.query.filter_by(lu=False).count(),
        'contacts_total': Contact.query.count(),
        'inscriptions_en_attente': Inscription.query.filter_by(statut='en_attente').count(),
        'inscriptions_total': Inscription.query.count(),
        'annonces_actives': Annonce.query.filter(
            Annonce.public == True,
            (Annonce.date_expiration.is_(None)) | (Annonce.date_expiration >= date.today())
        ).count(),
        'news_actives': News.query.filter_by(active=True).count(),
        'eleves_actifs': Eleve.query.filter_by(actif=True).count()
    }
    
    # Derniers contacts
    derniers_contacts = Contact.query.order_by(Contact.date_envoi.desc()).limit(5).all()
    
    # Dernières inscriptions
    dernieres_inscriptions = Inscription.query.order_by(Inscription.date_soumission.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         derniers_contacts=derniers_contacts,
                         dernieres_inscriptions=dernieres_inscriptions,
                         datetime=datetime)

# ==================== SECTION FORMULAIRES ====================

@admin_blueprint.route('/formulaires')
@login_required
@admin_required
def formulaires():
    """Vue d'ensemble des formulaires"""
    statut = request.args.get('statut', 'tous')
    type_form = request.args.get('type', 'contacts')
    
    if type_form == 'contacts':
        query = Contact.query
        
        if statut == 'non_lu':
            query = query.filter_by(lu=False)
        elif statut == 'traite':
            query = query.filter_by(traite=True)
        elif statut == 'non_traite':
            query = query.filter_by(traite=False)
        
        items = query.order_by(Contact.date_envoi.desc()).all()
    else:
        items = []
    
    return render_template('admin/formulaires.html', 
                         items=items,
                         statut_actuel=statut,
                         type_form=type_form)

@admin_blueprint.route('/formulaires/contact/<int:id>')
@login_required
@admin_required
def view_contact(id):
    """Voir les détails d'un contact"""
    contact = Contact.query.get_or_404(id)
    
    # Marquer comme lu automatiquement
    if not contact.lu:
        contact.lu = True
        db.session.commit()
    
    return render_template('admin/view_contact.html', contact=contact)

@admin_blueprint.route('/formulaires/contact/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_contact_status(id):
    """Mettre à jour le statut d'un contact (AJAX)"""
    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'lu' in data:
            contact.lu = data['lu']
        
        if 'traite' in data:
            contact.traite = data['traite']
        
        db.session.commit()
        return jsonify({
            'success': True,
            'lu': contact.lu,
            'traite': contact.traite
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_blueprint.route('/formulaires/contact/<int:id>/notes', methods=['POST'])
@login_required
@admin_required
def update_contact_notes(id):
    """Mettre à jour les notes d'un contact (AJAX)"""
    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'notes' in data:
            contact.notes_admin = data['notes']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_blueprint.route('/formulaires/contact/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_contact(id):
    """Supprimer un contact (AJAX)"""
    contact = Contact.query.get_or_404(id)
    
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SECTION CONTENU ====================

@admin_blueprint.route('/contenu')
@login_required
@admin_required
def contenu():
    """Gestion du contenu (annonces et actualités)"""
    type_contenu = request.args.get('type', 'annonces')
    
    if type_contenu == 'annonces':
        items = Annonce.query.order_by(Annonce.date_creation.desc()).all()
    elif type_contenu == 'actualites':
        items = News.query.order_by(News.priority.desc(), News.date_created.desc()).all()
    else:
        items = []
    
    return render_template('admin/contenu.html', 
                         items=items,
                         type_contenu=type_contenu,
                         date=date)

@admin_blueprint.route('/contenu/annonce/nouvelle', methods=['GET', 'POST'])
@login_required
@admin_required
def nouvelle_annonce():
    """Créer une nouvelle annonce"""
    if request.method == 'POST':
        try:
            titre = request.form.get('titre')
            contenu = request.form.get('contenu')
            public = request.form.get('public') == 'on'
            important = request.form.get('important') == 'on'
            date_expiration = request.form.get('date_expiration')
            
            annonce = Annonce(
                titre=titre,
                contenu=contenu,
                public=public,
                important=important,
                date_expiration=datetime.strptime(date_expiration, '%Y-%m-%d').date() if date_expiration else None
            )
            
            db.session.add(annonce)
            db.session.commit()
            
            flash('Annonce créée avec succès!', 'success')
            return redirect(url_for('admin.contenu', type='annonces'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création de l\'annonce: {str(e)}', 'error')
    
    return render_template('admin/nouvelle_annonce.html')

@admin_blueprint.route('/contenu/annonce/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
@admin_required
def modifier_annonce(id):
    """Modifier une annonce existante"""
    annonce = Annonce.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            annonce.titre = request.form.get('titre')
            annonce.contenu = request.form.get('contenu')
            annonce.public = request.form.get('public') == 'on'
            annonce.important = request.form.get('important') == 'on'
            date_expiration = request.form.get('date_expiration')
            annonce.date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d').date() if date_expiration else None
            
            db.session.commit()
            
            flash('Annonce modifiée avec succès!', 'success')
            return redirect(url_for('admin.contenu', type='annonces'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification de l\'annonce: {str(e)}', 'error')
    
    return render_template('admin/modifier_annonce.html', annonce=annonce)

@admin_blueprint.route('/contenu/annonce/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def supprimer_annonce(id):
    """Supprimer une annonce (AJAX)"""
    annonce = Annonce.query.get_or_404(id)
    
    try:
        db.session.delete(annonce)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_blueprint.route('/contenu/actualite/nouvelle', methods=['GET', 'POST'])
@login_required
@admin_required
def nouvelle_actualite():
    """Créer une nouvelle actualité"""
    if request.method == 'POST':
        try:
            content = request.form.get('content')
            active = request.form.get('active') == 'on'
            priority = int(request.form.get('priority', 0))
            
            news = News(
                content=content,
                active=active,
                priority=priority
            )
            
            db.session.add(news)
            db.session.commit()
            
            flash('Actualité créée avec succès!', 'success')
            return redirect(url_for('admin.contenu', type='actualites'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création de l\'actualité: {str(e)}', 'error')
    
    return render_template('admin/nouvelle_actualite.html')

@admin_blueprint.route('/contenu/actualite/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
@admin_required
def modifier_actualite(id):
    """Modifier une actualité existante"""
    news = News.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            news.content = request.form.get('content')
            news.active = request.form.get('active') == 'on'
            news.priority = int(request.form.get('priority', 0))
            news.date_updated = datetime.utcnow()
            
            db.session.commit()
            
            flash('Actualité modifiée avec succès!', 'success')
            return redirect(url_for('admin.contenu', type='actualites'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification de l\'actualité: {str(e)}', 'error')
    
    return render_template('admin/modifier_actualite.html', news=news)

@admin_blueprint.route('/contenu/actualite/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def supprimer_actualite(id):
    """Supprimer une actualité (AJAX)"""
    news = News.query.get_or_404(id)
    
    try:
        db.session.delete(news)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SECTION ADMISSION ET INSCRIPTION ====================

@admin_blueprint.route('/admissions')
@login_required
@admin_required
def admissions():
    """Gestion des admissions et inscriptions"""
    statut = request.args.get('statut', 'tous')
    
    query = Inscription.query
    
    if statut == 'en_attente':
        query = query.filter_by(statut='en_attente')
    elif statut == 'approuvee':
        query = query.filter_by(statut='approuvee')
    elif statut == 'rejetee':
        query = query.filter_by(statut='rejetee')
    elif statut == 'completee':
        query = query.filter_by(statut='completee')
    
    inscriptions = query.order_by(Inscription.date_soumission.desc()).all()
    
    # Statistiques
    stats = {
        'total': Inscription.query.count(),
        'en_attente': Inscription.query.filter_by(statut='en_attente').count(),
        'approuvee': Inscription.query.filter_by(statut='approuvee').count(),
        'rejetee': Inscription.query.filter_by(statut='rejetee').count(),
        'completee': Inscription.query.filter_by(statut='completee').count()
    }
    
    return render_template('admin/admissions.html', 
                         inscriptions=inscriptions,
                         statut_actuel=statut,
                         stats=stats)

@admin_blueprint.route('/admissions/<int:id>')
@login_required
@admin_required
def view_admission(id):
    """Voir les détails d'une admission"""
    inscription = Inscription.query.get_or_404(id)
    return render_template('admin/view_admission.html', inscription=inscription)

@admin_blueprint.route('/admissions/<int:id>/statut', methods=['POST'])
@login_required
@admin_required
def update_admission_statut(id):
    """Mettre à jour le statut d'une admission (AJAX)"""
    inscription = Inscription.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'statut' in data:
            inscription.statut = data['statut']
            inscription.date_traitement = datetime.utcnow()
        
        if 'notes_admin' in data:
            inscription.notes_admin = data['notes_admin']
        
        db.session.commit()
        return jsonify({'success': True, 'statut': inscription.statut})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_blueprint.route('/admissions/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_admission(id):
    """Supprimer une admission (AJAX)"""
    inscription = Inscription.query.get_or_404(id)
    
    try:
        db.session.delete(inscription)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SECTION PAIEMENTS ====================

@admin_blueprint.route('/paiements')
@login_required
@admin_required
def paiements():
    """Gestion des paiements"""
    # Filtres
    methode = request.args.get('methode', 'tous')
    
    query = Paiement.query
    
    if methode != 'tous':
        query = query.filter_by(methode=methode)
    
    paiements = query.order_by(Paiement.date.desc()).all()
    
    # Statistiques
    total_paiements = db.session.query(db.func.sum(Paiement.montant)).scalar() or 0
    
    stats = {
        'total': Paiement.query.count(),
        'montant_total': total_paiements,
        'especes': Paiement.query.filter_by(methode='espèces').count(),
        'cheque': Paiement.query.filter_by(methode='chèque').count(),
        'virement': Paiement.query.filter_by(methode='virement').count()
    }
    
    return render_template('admin/paiements.html', 
                         paiements=paiements,
                         methode_actuelle=methode,
                         stats=stats)
