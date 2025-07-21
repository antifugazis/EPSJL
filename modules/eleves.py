from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from models import Eleve
from models import db
import os
import traceback
from werkzeug.utils import secure_filename
from datetime import datetime

eleves_blueprint = Blueprint('eleves', __name__, url_prefix='/eleves')

# Ensure upload directories exist
def ensure_upload_dirs():
    upload_folder = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    eleves_folder = os.path.join(upload_folder, 'eleves')
    if not os.path.exists(eleves_folder):
        os.makedirs(eleves_folder, exist_ok=True)
    return upload_folder

# Helper function to check if user has admin privileges
def is_admin_or_directeur():
    return session.get('user_role') in ['admin', 'directeur']

@eleves_blueprint.route('/')
@login_required
def liste():
    search = request.args.get('search', '')
    classe_id = request.args.get('classe_id', '')

    # Get all classes for the filter
    from models import Classe
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()

    # Build the query using SQLAlchemy ORM
    query = Eleve.query.filter_by(actif=True)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Eleve.nom.ilike(search_term)) |
            (Eleve.prenom.ilike(search_term)) |
            (Eleve.matricule.ilike(search_term))
        )
    if classe_id:
        try:
            classe_id_int = int(classe_id)
            query = query.filter_by(classe_id=classe_id_int)
        except ValueError:
            pass  # Ignore invalid classe_id values
    eleves = query.order_by(Eleve.nom, Eleve.prenom).all()

    return render_template('eleves/liste.html', eleves=eleves, classes=classes, search=search, classe_id=classe_id)

@eleves_blueprint.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    from models import Classe, User
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    parents = User.query.filter_by(role='parent').order_by(User.nom, User.prenom).all()

    if request.method == 'POST':
        # Debug: Print all form data
        print('DEBUG: Form data received:', dict(request.form))

        matricule = request.form.get('matricule')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        date_naissance_str = request.form.get('date_naissance')
        lieu_naissance = request.form.get('lieu_naissance')
        sexe = request.form.get('sexe')
        adresse = request.form.get('adresse')
        telephone = request.form.get('telephone')
        email = request.form.get('email')
        classe_id = request.form.get('classe_id') or None
        parent_id = request.form.get('parent_id') or None
        notes = request.form.get('notes')

        print(f"DEBUG: Parsed values - matricule: {matricule}, nom: {nom}, prenom: {prenom}, date_naissance: {date_naissance_str}, lieu_naissance: {lieu_naissance}, sexe: {sexe}, adresse: {adresse}, telephone: {telephone}, email: {email}, classe_id: {classe_id}, parent_id: {parent_id}, notes: {notes}")

        # Validate required fields
        if not all([matricule, nom, prenom, date_naissance_str, lieu_naissance, sexe]):
            print("DEBUG: Missing required fields.")
            flash("Tous les champs obligatoires doivent être remplis.", "danger")
            return render_template('eleves/ajouter.html', classes=classes, parents=parents)

        # Parse date
        try:
            date_naissance = datetime.strptime(date_naissance_str, '%Y-%m-%d').date() if date_naissance_str else None
            print(f"DEBUG: Parsed date_naissance: {date_naissance}")
        except Exception as e:
            print(f"DEBUG: Date parsing error: {e}")
            flash('Format de date de naissance invalide.', 'danger')
            return render_template('eleves/ajouter.html', classes=classes, parents=parents)

        try:
            # Ensure upload directory exists
            upload_folder = ensure_upload_dirs()
            print(f"DEBUG: Upload folder: {upload_folder}")

            # Handle photo upload
            photo = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename:
                    filename = secure_filename(file.filename)
                    photo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file_path = os.path.join(upload_folder, 'eleves', photo)
                    file.save(file_path)
                    print(f"DEBUG: Photo saved to {file_path}")

            # Create new student
            new_eleve = Eleve(
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                date_naissance=date_naissance,
                sexe=sexe,
                adresse=adresse,
                telephone=telephone,
                email=email,
                photo=photo,
                classe_id=classe_id,
                parent_id=parent_id,
                date_inscription=datetime.now().date(),
                lieu_naissance=lieu_naissance,
                actif=True
            )
            print(f"DEBUG: Eleve instance created: {new_eleve}")
            db.session.add(new_eleve)
            db.session.commit()
            print("DEBUG: Student committed to database.")
            flash('Elève ajouté avec succès!', 'success')
            return redirect(url_for('eleves.liste'))
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Exception occurred: {e}")
            flash('Erreur lors de l\'ajout de l\'elève : ' + str(e), 'danger')
            return render_template('eleves/ajouter.html', classes=classes, parents=parents)

    return render_template('eleves/ajouter.html', classes=classes, parents=parents)


@eleves_blueprint.route('/<int:eleve_id>')
@login_required
def details(eleve_id):
    from models import Presence, Note, Paiement
    eleve = Eleve.query.get(eleve_id)
    if not eleve:
        flash("Élève non trouvé.", "danger")
        return redirect(url_for('eleves.liste'))
    presences = Presence.query.filter_by(eleve_id=eleve_id).order_by(Presence.date.desc()).limit(10).all()
    notes = Note.query.filter_by(eleve_id=eleve_id).order_by(Note.date.desc()).limit(10).all()
    paiements = Paiement.query.filter_by(eleve_id=eleve_id).order_by(Paiement.date.desc()).limit(10).all()
    return render_template('eleves/details.html', 
                          eleve=eleve, 
                          presences=presences, 
                          notes=notes, 
                          paiements=paiements)

@eleves_blueprint.route('/<int:eleve_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier(eleve_id):
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    from models import Classe, User
    eleve = Eleve.query.get(eleve_id)
    if not eleve:
        flash('Elève non trouvé.', 'danger')
        return redirect(url_for('eleves.liste'))

    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    parents = User.query.filter_by(role='parent').order_by(User.nom, User.prenom).all()

    if request.method == 'POST':
        # Get form data
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        date_naissance_str = request.form.get('date_naissance')
        lieu_naissance = request.form.get('lieu_naissance')
        sexe = request.form.get('sexe')
        adresse = request.form.get('adresse')
        telephone = request.form.get('telephone')
        email = request.form.get('email')
        classe_id = request.form.get('classe_id') or None
        parent_id = request.form.get('parent_id') or None
        # Remove notes field as it doesn't exist in the Eleve model
        # notes = request.form.get('notes')
        actif = True if request.form.get('actif') else False
        
        # Validate required fields
        if not all([nom, prenom, date_naissance_str, lieu_naissance, sexe]):
            flash("Tous les champs obligatoires doivent être remplis.", "danger")
            return render_template('eleves/modifier.html', eleve=eleve, classes=classes, parents=parents)
        
        # Debug information
        print(f"DEBUG: Form data received in modifier: {dict(request.form)}")
        print(f"DEBUG: date_naissance_str: {date_naissance_str}, type: {type(date_naissance_str)}")
        
        # Parse date
        try:
            if date_naissance_str and isinstance(date_naissance_str, str):
                date_naissance = datetime.strptime(date_naissance_str, '%Y-%m-%d').date()
                print(f"DEBUG: Parsed date_naissance: {date_naissance}, type: {type(date_naissance)}")
            else:
                date_naissance = None
                print(f"DEBUG: date_naissance set to None")
        except Exception as e:
            print(f"DEBUG: Date parsing error: {e}")
            flash('Format de date de naissance invalide.', 'danger')
            return render_template('eleves/modifier.html', eleve=eleve, classes=classes, parents=parents)

        try:
            # Ensure upload directory exists
            upload_folder = ensure_upload_dirs()
            
            # Handle photo upload
            photo = eleve.photo
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename:
                    filename = secure_filename(file.filename)
                    photo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file_path = os.path.join(upload_folder, 'eleves', photo)
                    file.save(file_path)

            # Debug current values before update
            print(f"DEBUG: Current eleve values before update:")
            print(f"DEBUG: eleve.nom: {eleve.nom}, type: {type(eleve.nom)}")
            print(f"DEBUG: eleve.prenom: {eleve.prenom}, type: {type(eleve.prenom)}")
            print(f"DEBUG: eleve.date_naissance: {eleve.date_naissance}, type: {type(eleve.date_naissance)}")
            print(f"DEBUG: eleve.lieu_naissance: {eleve.lieu_naissance}, type: {type(eleve.lieu_naissance)}")
            
            # Debug new values
            print(f"DEBUG: New values to be set:")
            print(f"DEBUG: nom: {nom}, type: {type(nom)}")
            print(f"DEBUG: prenom: {prenom}, type: {type(prenom)}")
            print(f"DEBUG: date_naissance: {date_naissance}, type: {type(date_naissance)}")
            print(f"DEBUG: lieu_naissance: {lieu_naissance}, type: {type(lieu_naissance)}")
            print(f"DEBUG: classe_id: {classe_id}, type: {type(classe_id)}")
            print(f"DEBUG: parent_id: {parent_id}, type: {type(parent_id)}")

            # Convert classe_id and parent_id to integers if they're strings and not empty
            if classe_id and isinstance(classe_id, str):
                try:
                    classe_id = int(classe_id)
                    print(f"DEBUG: Converted classe_id to int: {classe_id}")
                except ValueError:
                    classe_id = None
                    print(f"DEBUG: Could not convert classe_id to int, setting to None")
            
            if parent_id and isinstance(parent_id, str):
                try:
                    parent_id = int(parent_id)
                    print(f"DEBUG: Converted parent_id to int: {parent_id}")
                except ValueError:
                    parent_id = None
                    print(f"DEBUG: Could not convert parent_id to int, setting to None")

            # Update student
            eleve.nom = nom
            eleve.prenom = prenom
            eleve.date_naissance = date_naissance
            eleve.lieu_naissance = lieu_naissance
            eleve.sexe = sexe
            eleve.adresse = adresse
            eleve.telephone = telephone
            eleve.email = email
            eleve.photo = photo
            eleve.classe_id = classe_id
            eleve.parent_id = parent_id
            # Remove notes field as it doesn't exist in the Eleve model
            # eleve.notes = notes
            eleve.actif = actif
            
            db.session.commit()
            flash('Elève modifié avec succès!', 'success')
            return redirect(url_for('eleves.details', eleve_id=eleve_id))
        except Exception as e:
            db.session.rollback()
            import traceback
            error_traceback = traceback.format_exc()
            print(f"DEBUG: Exception details: {str(e)}")
            print(f"DEBUG: Traceback: {error_traceback}")
            flash('Erreur lors de la modification de l\'elève : ' + str(e), 'danger')
            return render_template('eleves/modifier.html', eleve=eleve, classes=classes, parents=parents)

    return render_template('eleves/modifier.html', eleve=eleve, classes=classes, parents=parents)