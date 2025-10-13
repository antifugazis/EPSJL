from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Doleance, User
from functools import wraps
import os

doleances_blueprint = Blueprint('doleances', __name__, url_prefix='/doleances')

UPLOAD_FOLDER = 'static/uploads/recu_doleances'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    """Décorateur pour vérifier que l'utilisateur est admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Accès non autorisé', 'error')
            return redirect(url_for('accueil'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES PUBLIQUES ====================

@doleances_blueprint.route('/formulaire', methods=['GET', 'POST'])
def formulaire():
    """Formulaire de soumission de doléance"""
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            nom_complet_eleve = request.form.get('nom_complet_eleve')
            classe = request.form.get('classe')
            telephone1 = request.form.get('telephone1')
            telephone2 = request.form.get('telephone2')
            email = request.form.get('email')
            description = request.form.get('description')
            
            # Validation
            if not all([nom_complet_eleve, classe, telephone1, description]):
                flash('Veuillez remplir tous les champs obligatoires', 'error')
                return redirect(url_for('doleances.formulaire'))
            
            # Gérer l'upload du fichier
            photo_recu = None
            if 'photo_recu' in request.files:
                file = request.files['photo_recu']
                if file and file.filename and allowed_file(file.filename):
                    # Créer le dossier s'il n'existe pas
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    
                    # Générer un nom de fichier unique
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    
                    file.save(filepath)
                    photo_recu = filepath
            
            # Créer la doléance
            nouvelle_doleance = Doleance(
                nom_complet_eleve=nom_complet_eleve,
                classe=classe,
                telephone1=telephone1,
                telephone2=telephone2,
                email=email,
                photo_recu=photo_recu,
                description=description,
                statut='en_attente'
            )
            
            db.session.add(nouvelle_doleance)
            db.session.commit()
            
            flash('Votre doléance a été soumise avec succès. Nous vous contacterons bientôt.', 'success')
            return redirect(url_for('doleances.formulaire'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la soumission: {str(e)}', 'error')
            return redirect(url_for('doleances.formulaire'))
    
    return render_template('website/doleances.html')

# ==================== ROUTES ADMIN ====================

@doleances_blueprint.route('/admin/liste')
@login_required
@admin_required
def admin_liste():
    """Liste des doléances pour l'admin"""
    statut_filter = request.args.get('statut', '')
    
    query = Doleance.query
    if statut_filter:
        query = query.filter_by(statut=statut_filter)
    
    doleances = query.order_by(Doleance.date_soumission.desc()).all()
    
    # Statistiques
    stats = {
        'total': Doleance.query.count(),
        'en_attente': Doleance.query.filter_by(statut='en_attente').count(),
        'en_cours': Doleance.query.filter_by(statut='en_cours').count(),
        'resolu': Doleance.query.filter_by(statut='resolu').count(),
        'rejete': Doleance.query.filter_by(statut='rejete').count()
    }
    
    return render_template('admin/doleances/liste.html', 
                         doleances=doleances, 
                         stats=stats,
                         statut_actif=statut_filter)

@doleances_blueprint.route('/admin/details/<int:id>')
@login_required
@admin_required
def admin_details(id):
    """Détails d'une doléance"""
    doleance = Doleance.query.get_or_404(id)
    return render_template('admin/doleances/details.html', doleance=doleance)

@doleances_blueprint.route('/admin/traiter/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_traiter(id):
    """Traiter une doléance"""
    doleance = Doleance.query.get_or_404(id)
    
    try:
        statut = request.form.get('statut')
        reponse = request.form.get('reponse')
        
        if statut:
            doleance.statut = statut
            doleance.date_traitement = datetime.now()
            doleance.traite_par = current_user.id
        
        if reponse:
            doleance.reponse_admin = reponse
        
        db.session.commit()
        flash('Doléance mise à jour avec succès', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('doleances.admin_details', id=id))

@doleances_blueprint.route('/admin/supprimer/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def admin_supprimer(id):
    """Supprimer une doléance"""
    doleance = Doleance.query.get_or_404(id)
    
    try:
        # Supprimer le fichier s'il existe
        if doleance.photo_recu and os.path.exists(doleance.photo_recu):
            os.remove(doleance.photo_recu)
        
        db.session.delete(doleance)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
