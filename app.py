from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, send_from_directory, abort
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date
import os
import json
import uuid
from functools import wraps
from flask_migrate import Migrate
from models import Cours, db, User, Eleve, Evenement, Annonce, Inscription, Contact, ResultatAdmission

# Import modules
from modules.auth import auth_blueprint
from modules.eleves import eleves_blueprint
from modules.cours import cours_blueprint
from modules.presence import presence_blueprint
from modules.notes import notes_blueprint
from modules.finances import finances_blueprint
from modules.rapports import rapports_blueprint
from modules.calendrier import calendrier_blueprint
from modules.communication import communication_blueprint
from modules.inscriptions import inscriptions_blueprint
from modules.news import news_blueprint
from modules.whatsapp_management import whatsapp_management_blueprint
from modules.archives import archives_blueprint
from modules.admin import admin_blueprint
from modules.articles import articles_bp
from modules.resultats_admission import resultats_admission_bp

# Configuration
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
migrate = Migrate(app, db)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(eleves_blueprint)
app.register_blueprint(cours_blueprint)
app.register_blueprint(presence_blueprint)
app.register_blueprint(notes_blueprint)
app.register_blueprint(finances_blueprint)
app.register_blueprint(rapports_blueprint)
app.register_blueprint(calendrier_blueprint)
app.register_blueprint(communication_blueprint)
app.register_blueprint(inscriptions_blueprint)
app.register_blueprint(news_blueprint)
app.register_blueprint(whatsapp_management_blueprint)
app.register_blueprint(archives_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(articles_bp)
app.register_blueprint(resultats_admission_bp)

# Home route
@app.route('/')
def accueil():
    # Get some stats for the homepage using SQLAlchemy
    
    # Get total number of students
    total_eleves = Eleve.query.filter_by(actif=True).count()
    
    # Get upcoming events
    from datetime import date
    today = date.today()
    evenements = Evenement.query.filter(Evenement.date >= today).order_by(Evenement.date).limit(5).all()
    
    # Get recent announcements
    annonces = Annonce.query.order_by(Annonce.date_creation.desc()).limit(5).all()
    
    return render_template('website/accueil.html', total_eleves=total_eleves, upcoming_events=evenements, recent_announcements=annonces)

@app.route('/a-propos')
def a_propos():
    return render_template('website/a-propos.html')

@app.route('/programmes')
def programmes():
    return render_template('website/programmes.html')

@app.route('/equipe')
def equipe():
    return render_template('website/team.html')

@app.route('/admission', methods=['GET', 'POST'])
def admission():
    if request.method == 'POST':
        try:
            # Get form data from simplified form
            nom_eleve = request.form.get('eleve-nom')
            ancienne_classe = request.form.get('ancienne-classe')
            promotion = request.form.get('promotion')

            # Split full name into first and last name
            if nom_eleve:
                name_parts = nom_eleve.strip().split()
                if len(name_parts) >= 2:
                    prenom_eleve = ' '.join(name_parts[:-1])  # Everything except last name
                    nom_eleve_split = name_parts[-1]  # Last name only
                elif len(name_parts) == 1:
                    prenom_eleve = name_parts[0]
                    nom_eleve_split = ""
                else:
                    prenom_eleve = nom_eleve
                    nom_eleve_split = ""
            else:
                prenom_eleve = "Non spécifié"
                nom_eleve_split = "Non spécifié"

            # Create admission result record
            nouvelle_demande = ResultatAdmission(
                nom=nom_eleve_split,
                prenom=prenom_eleve,
                classe=ancienne_classe if ancienne_classe else "Non spécifié",
                promotion=promotion if promotion else "2024-2025",
                statut='en_attente',  # Default status for new applications
                publie=False,  # Not published until approved
                date_publication=datetime.now()  # Explicitly set the publication date
            )

            # Save to database
            db.session.add(nouvelle_demande)
            db.session.commit()

            # Show success message
            flash('Votre demande d\'admission a été soumise avec succès. Nous vous contacterons bientôt pour les prochaines étapes.', 'success')
            return redirect(url_for('admission'))

        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue lors de la soumission de votre demande: {str(e)}', 'error')
            return redirect(url_for('admission'))

    # GET request - show the form
    return render_template('website/admission.html')


@app.route('/evenements')
def evenements():
    from models import Article
    categorie = request.args.get('categorie')
    
    query = Article.query.filter_by(actif=True)
    if categorie:
        query = query.filter_by(categorie=categorie)
    
    articles = query.order_by(Article.date_creation.desc()).all()
    return render_template('website/events.html', articles=articles, categorie_active=categorie)

@app.route('/gallery')
def gallery():
    return render_template('website/gallery.html')

@app.route('/temoignages')
def temoignages():
    return render_template('website/temoignages.html')

@app.route('/payment')
def payment():
    return render_template('website/payment.html')

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            nom = request.form.get('name')
            email = request.form.get('email')
            sujet = request.form.get('subject')
            message = request.form.get('message')
            
            # Créer un nouveau message de contact
            nouveau_message = Contact(
                nom=nom,
                email=email,
                sujet=sujet,
                message=message
            )
            
            # Sauvegarder dans la base de données
            db.session.add(nouveau_message)
            db.session.commit()
            
            # Afficher un message de succès
            flash('Votre message a été envoyé avec succès. Nous vous contacterons bientôt.', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue lors de l\'envoi de votre message: {str(e)}', 'error')
            return redirect(url_for('contact'))
    
    # Afficher le formulaire pour les requêtes GET
    return render_template('website/contact.html')




# Configuration pour le téléchargement de fichiers
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Créer le dossier de téléchargement s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, subfolder):
    if file and allowed_file(file.filename):
        # Créer un nom de fichier unique
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Créer le sous-dossier s'il n'existe pas
        upload_path = os.path.join(UPLOAD_FOLDER, subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Sauvegarder le fichier
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        return file_path
    return None

# Redirect old inscription URL to new blueprint route
@app.route('/inscription')
def old_inscription():
    return redirect(url_for('inscriptions.formulaire'))

# Redirect old confirmation URL to new blueprint route
@app.route('/inscription/confirmation/<int:id>')
def confirmation_inscription(id):
    return redirect(url_for('inscriptions.confirmation', id=id))

# Redirect old admin inscriptions URL to new blueprint route
@app.route('/admin/inscriptions')
@login_required
def admin_inscriptions():
    statut = request.args.get('statut', 'tous')
    return redirect(url_for('inscriptions.liste', statut=statut))

# Redirect old update status URL to new blueprint route
@app.route('/admin/inscription/<int:id>/statut', methods=['POST'])
@login_required
def update_inscription_statut(id):
    return redirect(url_for('inscriptions.update_statut', id=id))

# Redirect old view inscription URL to new blueprint route
@app.route('/admin/inscription/<int:id>')
@login_required
def view_inscription(id):
    return redirect(url_for('inscriptions.details', id=id))

# Redirect old delete inscription URL to new blueprint route
@app.route('/admin/inscription/<int:id>', methods=['DELETE'])
@login_required
def delete_inscription(id):
    return redirect(url_for('inscriptions.delete', id=id))

# Interface d'administration pour gérer les messages de contact
@app.route('/admin/contacts')
@login_required
def admin_contacts():
    if not current_user.is_authenticated or current_user.role != 'admin':
        abort(403)
    
    statut = request.args.get('statut', 'tous')
    
    query = Contact.query
    
    if statut == 'non_lu':
        query = query.filter_by(lu=False)
    elif statut == 'traite':
        query = query.filter_by(traite=True)
    
    contacts = query.order_by(Contact.date_envoi.desc()).all()
    return render_template('admin/contacts.html', 
                         contacts=contacts, 
                         statut_actuel=statut)

# Mettre à jour le statut d'un message de contact (AJAX)
@app.route('/admin/contact/<int:id>/status', methods=['POST'])
@login_required
def update_contact_status(id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
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

# Enregistrer les notes d'un message de contact (AJAX)
@app.route('/admin/contact/<int:id>/notes', methods=['POST'])
@login_required
def update_contact_notes(id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'notes' in data:
            contact.notes_admin = data['notes']
        
        db.session.commit()
        return jsonify({
            'success': True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Supprimer un message de contact (AJAX)
@app.route('/admin/contact/<int:id>', methods=['DELETE'])
@login_required
def delete_contact(id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    contact = Contact.query.get_or_404(id)
    
    try:
        # Supprimer de la base de données
        db.session.delete(contact)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# API endpoints
@app.route('/api/cours')
@login_required
def api_cours():
    classe_id = request.args.get('classe_id')
    print(f"DEBUG: Fetching courses for class_id: {classe_id}")
    if not classe_id:
        print("DEBUG: No class_id provided")
        return jsonify([])
    try:
        classe_id_int = int(classe_id)
    except (TypeError, ValueError):
        print("DEBUG: Invalid class_id provided")
        return jsonify([])
    
    from models import Enseignement, Cours, db
    
    # Query the database to get courses for the selected class
    try:
        # Join Enseignement and Cours tables to get courses for the selected class
        courses = db.session.query(Cours).join(
            Enseignement, Cours.id == Enseignement.cours_id
        ).filter(
            Enseignement.classe_id == classe_id_int
        ).order_by(Cours.nom).all()
        
        print(f"DEBUG: Found {len(courses)} courses for class {classe_id}")
        
        cours_list = [
            {
                'id': c.id,
                'code': c.code,
                'nom': c.nom,
                'coefficient': c.coefficient
            } for c in courses
        ]
        
        print(f"DEBUG: Sending response: {cours_list}")
        return jsonify(cours_list)
        
    except Exception as e:
        print(f"ERROR in api_cours: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('erreurs/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('erreurs/500.html'), 500

# Context processor for common data
@app.context_processor
def inject_data():
    current_year = datetime.now().year
    school_name = "École Presbytérale Saint Joseph de L'Asile"
    
    # Get recent public announcements for the ticker
    annonces = None
    try:
        print("DEBUG: Fetching announcements for ticker")
        # Check if the important field exists in the Annonce model
        has_important_field = hasattr(Annonce, 'important')
        print(f"DEBUG: has_important_field = {has_important_field}")
        
        # Count total announcements in the database
        total_annonces = Annonce.query.count()
        print(f"DEBUG: Total announcements in database: {total_annonces}")
        
        # Count public announcements
        public_count = Annonce.query.filter(Annonce.public == 1).count()
        print(f"DEBUG: Public announcements count: {public_count}")
        
        # Base query for public announcements that are not expired
        # Using is_() instead of == for None comparison as recommended by SQLAlchemy
        base_query = Annonce.query.filter(
            Annonce.public == 1,
            (Annonce.date_expiration.is_(None)) | (Annonce.date_expiration >= date.today())
        )
        
        # Check SQL generated
        print(f"DEBUG: SQL Query: {str(base_query)}")
        
        # Order by importance if the field exists, otherwise just by date
        if has_important_field:
            # Using SQLite integer for boolean (1 for True, 0 for False)
            annonces = base_query.order_by(Annonce.important.desc(), Annonce.date_creation.desc()).limit(10).all()
        else:
            annonces = base_query.order_by(Annonce.date_creation.desc()).limit(10).all()
            
        print(f"DEBUG: Found {len(annonces) if annonces else 0} announcements for ticker")
        if annonces:
            for i, a in enumerate(annonces):
                # Show raw SQLite values (0/1) for boolean fields
                print(f"DEBUG: Announcement {i+1}: id={a.id}, title={a.titre}, public={a.public} (raw: {int(a.public)}), important={a.important if has_important_field else 'N/A'} (raw: {int(a.important) if has_important_field else 'N/A'})")
        else:
            print("DEBUG: No announcements found. This could be due to:")  
            print("  1. No announcements in the database")
            print("  2. No public announcements (public=1)")
            print("  3. All announcements are expired")
            print("  4. Boolean value mismatch between Python (True/False) and SQLite (1/0)")
            print("DEBUG: Try running a direct query on the database to check raw values:")  
            print("  SELECT id, titre, public, important, date_expiration FROM annonces;")
            print("DEBUG: If public=1 announcements exist but aren't showing, check date_expiration values.")
            print(f"DEBUG: Today's date for comparison: {date.today()}")
            
            # Try a simpler query just to see if any public announcements exist
            simple_query = Annonce.query.filter(Annonce.public == 1).all()
            print(f"DEBUG: Simple query (just public=1) found {len(simple_query)} announcements")
            if simple_query:
                for i, a in enumerate(simple_query):
                    print(f"DEBUG: Simple query result {i+1}: id={a.id}, title={a.titre}, date_expiration={a.date_expiration}")
                print("DEBUG: If announcements appear here but not in the ticker, the date_expiration filter is excluding them")
    except Exception as e:
        print(f"Error fetching announcements for context: {str(e)}")
    
    return dict(
        current_year=current_year, 
        school_name=school_name,
        annonces=annonces
    )

# Create database tables if they don't exist
# Template filters
@app.template_filter('nl2br')
def nl2br_filter(s):
    """Convert newlines to <br> tags"""
    if s is None:
        return ''
    return s.replace('\n', '<br>\n')

# Note: before_first_request is deprecated in newer Flask versions
# We'll use app.app_context() and create tables directly when the app starts

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True, host='0.0.0.0', port=8010)