from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from models import db, Inscription, Eleve, User, Cours
from functools import wraps

# Create blueprint
inscriptions_blueprint = Blueprint('inscriptions', __name__, url_prefix='/inscriptions')

# Helper function to check if user is admin or directeur
def is_admin_or_directeur():
    return current_user.is_authenticated and current_user.role in ['admin', 'directeur']

# Decorator for admin/directeur access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_or_directeur():
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('accueil'))
        return f(*args, **kwargs)
    return decorated_function

# Configuration pour le téléchargement de fichiers
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join('static', 'uploads'))
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dirs():
    upload_folder = UPLOAD_FOLDER
    os.makedirs(upload_folder, exist_ok=True)
    
    # Create subdirectories for different document types
    for subfolder in ['actes_naissance', 'bulletins', 'photos_identite']:
        os.makedirs(os.path.join(upload_folder, subfolder), exist_ok=True)
    
    return upload_folder

def save_uploaded_file(file, subfolder):
    print(f"\n=== DEBUG: save_uploaded_file called for {subfolder} ===")
    print(f"File object: {file}")
    
    try:
        # Check if file object is valid
        if not file:
            print("ERROR: No file object provided")
            return None
            
        if not hasattr(file, 'filename') or not file.filename:
            print(f"ERROR: Invalid or empty filename in {subfolder} file object")
            print(f"File attributes: {dir(file)}")
            return None
            
        print(f"Processing file: {file.filename}")
        print(f"Content type: {file.content_type}")
        print(f"Content length: {file.content_length if hasattr(file, 'content_length') else 'N/A'}")
        
        # Validate file extension
        if not allowed_file(file.filename):
            print(f"ERROR: File type not allowed: {file.filename}")
            print(f"Allowed extensions: {ALLOWED_EXTENSIONS}")
            return None
            
        # Create a secure filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        print(f"Generated unique filename: {unique_filename}")
        
        # Ensure upload directory exists
        upload_path = os.path.join(UPLOAD_FOLDER, subfolder)
        print(f"Upload path: {upload_path}")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(upload_path, exist_ok=True, mode=0o755)
            print(f"Verified/Created directory: {upload_path}")
            
            # Check directory permissions
            if not os.access(upload_path, os.W_OK):
                print(f"ERROR: No write permissions for directory: {upload_path}")
                print(f"Current working directory: {os.getcwd()}")
                print(f"Directory exists: {os.path.exists(upload_path)}")
                print(f"Directory permissions: {oct(os.stat(upload_path).st_mode)[-3:]}")
                return None
                
        except Exception as e:
            print(f"ERROR: Failed to create directory {upload_path}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        
        # Save the file
        file_path = os.path.join(upload_path, unique_filename)
        print(f"Saving to: {file_path}")
        
        try:
            # Save the file
            file.save(file_path)
            print(f"File saved successfully: {file_path}")
            
            # Verify file was saved
            if not os.path.exists(file_path):
                print(f"ERROR: File was not saved: {file_path}")
                return None
                
            # Set file permissions
            try:
                os.chmod(file_path, 0o644)
                print(f"Set file permissions to 644")
            except Exception as e:
                print(f"WARNING: Could not set file permissions: {str(e)}")
            
            print(f"File upload successful: {file_path} ({os.path.getsize(file_path)} bytes)")
            return file_path
            
        except Exception as e:
            print(f"ERROR: Failed to save file {file_path}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Try to remove partially saved file if it exists
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Removed partially saved file: {file_path}")
                except Exception as remove_error:
                    print(f"WARNING: Could not remove partially saved file: {str(remove_error)}")
            
            return None
            
    except Exception as e:
        print(f"UNEXPECTED ERROR in save_uploaded_file:")
        print(f"Type: {type(e).__name__}")
        print(f"Details: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Public route for inscription form
@inscriptions_blueprint.route('/', methods=['GET', 'POST'])
def formulaire():
    if request.method == 'POST':
        try:
            print("\n=== DEBUG: Form Submission Started ===")
            print(f"Form Data: {request.form}")
            
            # Get form data
            data = request.form
            
            # Debug: Print all files in request
            print("\n=== DEBUG: Files in request ===")
            for key in request.files:
                file_list = request.files.getlist(key)
                print(f"File field '{key}': {len(file_list)} file(s)")
                for i, f in enumerate(file_list):
                    print(f"  File {i+1}: {f.filename} (type: {f.content_type}, size: {f.content_length if hasattr(f, 'content_length') else 'N/A'} bytes)")
            
            # Handle file uploads with better error handling
            acte_naissance_path = None
            bulletins_paths = []
            photo_identite_path = None
            
            try:
                # Process acte de naissance
                print("\n=== Processing Acte de Naissance ===")
                if 'acte_naissance' in request.files:
                    file = request.files['acte_naissance']
                    print(f"Acte de naissance file: {file.filename if file.filename else 'No file'}")
                    if file and file.filename != '':
                        print(f"Saving acte de naissance: {file.filename}")
                        acte_naissance_path = save_uploaded_file(file, 'actes_naissance')
                        print(f"Saved to: {acte_naissance_path}")
                        if not acte_naissance_path:
                            error_msg = 'Erreur lors du téléchargement de l\'acte de naissance'
                            print(error_msg)
                            flash(error_msg, 'error')
                
                # Process bulletins de notes (multiple files)
                print("\n=== Processing Bulletins de Notes ===")
                if 'bulletins_notes' in request.files:
                    files = request.files.getlist('bulletins_notes')
                    print(f"Found {len(files)} bulletin(s) to process")
                    for i, file in enumerate(files):
                        if file and file.filename != '':
                            print(f"Processing bulletin {i+1}: {file.filename}")
                            path = save_uploaded_file(file, 'bulletins')
                            print(f"Saved to: {path}")
                            if path:
                                bulletins_paths.append(path)
                
                # Process photo d'identité
                print("\n=== Processing Photo d'identité ===")
                if 'photo_identite' in request.files:
                    file = request.files['photo_identite']
                    print(f"Photo d'identité file: {file.filename if file.filename else 'No file'}")
                    if file and file.filename != '':
                        print(f"Saving photo d'identité: {file.filename}")
                        photo_identite_path = save_uploaded_file(file, 'photos_identite')
                        print(f"Saved to: {photo_identite_path}")
                        if not photo_identite_path:
                            error_msg = 'Erreur lors du téléchargement de la photo d\'identité'
                            print(error_msg)
                            flash(error_msg, 'error')
                            
            except Exception as e:
                error_msg = f'Erreur lors du traitement des fichiers: {str(e)}'
                print(error_msg)
                print(f"Error type: {type(e).__name__}")
                print(f"Error details: {str(e)}")
                import traceback
                traceback.print_exc()
                flash(error_msg, 'error')
            
            # Create new inscription
            nouvelle_inscription = Inscription(
                # Student information
                prenom_eleve=data.get('prenom'),
                nom_eleve=data.get('nom'),
                date_naissance=datetime.strptime(data.get('date_naissance'), '%Y-%m-%d').date(),
                lieu_naissance=data.get('lieu_naissance'),
                genre=data.get('genre'),
                niveau_demande=data.get('niveau'),
                
                # Parent 1 information
                parent1_nom=data.get('parent1_nom'),
                parent1_lien=data.get('parent1_lien'),
                parent1_telephone=data.get('parent1_telephone'),
                parent1_email=data.get('parent1_email'),
                
                # Parent 2 information (optional)
                parent2_nom=data.get('parent2_nom'),
                parent2_lien=data.get('parent2_lien'),
                parent2_telephone=data.get('parent2_telephone'),
                parent2_email=data.get('parent2_email'),
                
                # Additional information
                adresse=data.get('adresse'),
                ville=data.get('ville'),
                pays=data.get('pays', 'Haïti'),
                langues_parlees=','.join(request.form.getlist('langues[]')) if 'langues[]' in request.form else '',
                commentaires=data.get('commentaires'),
                
                # File paths
                acte_naissance=acte_naissance_path,
                bulletins_notes=';'.join(bulletins_paths) if bulletins_paths else None,
                photo_identite=photo_identite_path,
                
                # Default status
                statut='en_attente'
            )
            
            # Save to database
            db.session.add(nouvelle_inscription)
            db.session.commit()
            
            # Redirect to confirmation page
            return redirect(url_for('inscriptions.confirmation', id=nouvelle_inscription.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue lors de l\'enregistrement de votre inscription: {str(e)}', 'danger')
            return redirect(url_for('inscriptions.formulaire'))
    
    # Display form for GET requests
    return render_template('inscription.html')

# Confirmation page
@inscriptions_blueprint.route('/confirmation/<int:id>')
def confirmation(id):
    inscription = Inscription.query.get_or_404(id)
    return render_template('confirmation_inscription.html', inscription=inscription)

# Admin routes
@inscriptions_blueprint.route('/admin', methods=['GET'])
@login_required
@admin_required
def liste():
    statut = request.args.get('statut', 'tous')
    
    query = Inscription.query
    
    if statut != 'tous':
        query = query.filter_by(statut=statut)
    
    inscriptions = query.order_by(Inscription.date_soumission.desc()).all()
    
    # Count inscriptions by status for sidebar
    en_attente_count = Inscription.query.filter_by(statut='en_attente').count()
    
    return render_template('admin/inscriptions.html', 
                         inscriptions=inscriptions, 
                         statut_actuel=statut,
                         inscriptions_count=en_attente_count)

@inscriptions_blueprint.route('/admin/<int:id>', methods=['GET'])
@login_required
@admin_required
def details(id):
    inscription = Inscription.query.get_or_404(id)
    return render_template('admin/view_inscription.html', inscription=inscription)

@inscriptions_blueprint.route('/admin/<int:id>/statut', methods=['POST'])
@login_required
@admin_required
def update_statut(id):
    inscription = Inscription.query.get_or_404(id)
    data = request.get_json()
    
    if 'statut' not in data:
        return jsonify({'success': False, 'error': 'Statut manquant'}), 400
    
    inscription.statut = data['statut']
    inscription.date_traitement = datetime.utcnow()
    
    if 'notes' in data:
        inscription.notes_admin = data['notes']
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'statut': inscription.statut,
            'date_traitement': inscription.date_traitement.isoformat() if inscription.date_traitement else None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@inscriptions_blueprint.route('/admin/<int:id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete(id):
    inscription = Inscription.query.get_or_404(id)
    
    try:
        # Delete associated files
        for file_path in [inscription.acte_naissance, inscription.photo_identite]:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        
        if inscription.bulletins_notes:
            for file_path in inscription.bulletins_notes.split(';'):
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # Delete from database
        db.session.delete(inscription)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@inscriptions_blueprint.route('/admin/<int:id>/convert', methods=['POST'])
@login_required
@admin_required
def convert_to_student(id):
    inscription = Inscription.query.get_or_404(id)
    
    if inscription.statut != 'approuvee':
        return jsonify({'success': False, 'error': 'Seules les inscriptions approuvées peuvent être converties en élèves'}), 400
    
    try:
        # Generate a unique matricule
        current_year = datetime.now().year
        count = Eleve.query.count() + 1
        matricule = f"EPSJA-{current_year}-{count:04d}"
        
        # Create parent user if needed
        parent_id = None
        if inscription.parent1_email:
            parent = User.query.filter_by(email=inscription.parent1_email).first()
            if not parent:
                # Create a new parent user
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt()
                
                # Generate a temporary password
                temp_password = f"temp{uuid.uuid4().hex[:8]}"
                hashed_password = bcrypt.generate_password_hash(temp_password).decode('utf-8')
                
                parent = User(
                    username=inscription.parent1_email.split('@')[0],
                    email=inscription.parent1_email,
                    password_hash=hashed_password,
                    nom=inscription.parent1_nom.split()[-1] if ' ' in inscription.parent1_nom else inscription.parent1_nom,
                    prenom=inscription.parent1_nom.split()[0] if ' ' in inscription.parent1_nom else '',
                    role='parent'
                )
                db.session.add(parent)
                db.session.flush()  # To get the ID without committing
                parent_id = parent.id
            else:
                parent_id = parent.id
        
        # Get the default class if specified in the request
        classe_id = None
        if request.is_json:
            data = request.get_json(silent=True)
            if data:
                classe_id = data.get('classe_id')
        else:
            classe_id = request.form.get('classe_id')
        
        # If no class is specified, get the first available class or create a default one
        if not classe_id:
            # Try to find a class
            default_class = Cours.query.first()
            
            # If no class exists, create a default one
            if not default_class:
                default_class = Cours(
                    nom="Classe par défaut",
                    niveau="1",
                    annee_scolaire=f"{datetime.now().year}-{datetime.now().year + 1}",
                    capacite=30,
                    description="Classe par défaut pour les nouveaux élèves"
                )
                db.session.add(default_class)
                db.session.flush()  # To get the ID without committing
            
            classe_id = default_class.id
        
        # Create new student
        eleve = Eleve(
            matricule=matricule,
            nom=inscription.nom_eleve,
            prenom=inscription.prenom_eleve,
            date_naissance=inscription.date_naissance,
            lieu_naissance=inscription.lieu_naissance,
            sexe='M' if inscription.genre.lower() == 'masculin' else 'F',
            adresse=inscription.adresse,
            telephone=inscription.parent1_telephone,
            email=inscription.parent1_email,
            classe_id=classe_id,
            photo=inscription.photo_identite,
            parent_id=parent_id,
            actif=True,
            date_inscription=datetime.now()
        )
        
        # Add student to database
        db.session.add(eleve)
        
        # Update inscription status
        inscription.statut = 'completee'
        inscription.notes_admin = (inscription.notes_admin or '') + f"\nConverti en élève le {datetime.now().strftime('%d/%m/%Y %H:%M')}. Matricule: {matricule}"
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'eleve_id': eleve.id,
            'matricule': matricule
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
