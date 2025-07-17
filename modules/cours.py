from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required
from models import Cours, Classe, Enseignement
from models import db


cours_blueprint = Blueprint('cours', __name__, url_prefix='/cours')

# Helper function to check if user has admin privileges
def is_admin_or_directeur():
    return session.get('user_role') in ['admin', 'directeur']

@cours_blueprint.route('/')
@login_required
def liste():
    # Use SQLAlchemy ORM to get all Enseignements (course assignments), joining Cours, Classe, and User (professor)
    from models import User
    enseignements = (
        db.session.query(Enseignement, Cours, Classe, User)
        .join(Cours, Enseignement.cours_id == Cours.id)
        .join(Classe, Enseignement.classe_id == Classe.id)
        .join(User, Enseignement.professeur_id == User.id)
        .order_by(Classe.niveau, Classe.nom, Cours.nom)
        .all()
    )
    cours_list = []
    for ens, cours, classe, prof in enseignements:
        professeur_nom = f"{prof.prenom} {prof.nom}".strip()
        cours_list.append({
            'id': cours.id,
            'nom': cours.nom,
            'description': cours.description,
            'coefficient': cours.coefficient,
            'classe_nom': classe.nom,
            'professeur_nom': professeur_nom
        })
    return render_template('cours/liste.html', cours=cours_list)

@cours_blueprint.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    from models import User

    if request.method == 'POST':
        nom = request.form.get('nom')
        description = request.form.get('description')
        classe_id = request.form.get('classe_id')
        professeur_id = request.form.get('professeur_id')
        coefficient = request.form.get('coefficient', 1)

        # Create the course
        cours = Cours(nom=nom, description=description, coefficient=coefficient)
        db.session.add(cours)
        db.session.commit()  # Commit to get cours.id

        # Create the Enseignement association
        enseignement = Enseignement(cours_id=cours.id, classe_id=classe_id, professeur_id=professeur_id, annee_scolaire='2024-2025')
        db.session.add(enseignement)
        db.session.commit()

        flash('Cours ajouté avec succès!', 'success')
        return redirect(url_for('cours.liste'))

    # Get data for form
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    professeurs = User.query.filter_by(role='professeur').order_by(User.nom, User.prenom).all()
    return render_template('cours/ajouter.html', classes=classes, professeurs=professeurs)

@cours_blueprint.route('/<int:cours_id>')
@login_required
def details(cours_id):
    # Fetch the Enseignement for this course (assuming one class/prof per course instance)
    enseignement = Enseignement.query.filter_by(cours_id=cours_id).first()
    if not enseignement:
        flash('Cours non trouvé.', 'danger')
        return redirect(url_for('cours.liste'))
    cours = enseignement.cours
    classe = enseignement.classe
    professeur = enseignement.professeur
    # Get students in this class
    eleves = classe.eleves if classe else []
    return render_template('cours/details.html', cours={
        'id': cours.id,
        'nom': cours.nom,
        'description': cours.description,
        'coefficient': cours.coefficient,
        'classe_nom': classe.nom if classe else None,
        'professeur_nom': f"{professeur.prenom} {professeur.nom}" if professeur else None
    }, eleves=eleves)

@cours_blueprint.route('/<int:cours_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier(cours_id):
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))

    from models import User
    enseignement = Enseignement.query.filter_by(cours_id=cours_id).first()
    if not enseignement:
        flash('Cours non trouvé.', 'danger')
        return redirect(url_for('cours.liste'))
    cours = enseignement.cours

    if request.method == 'POST':
        nom = request.form.get('nom')
        description = request.form.get('description')
        classe_id = request.form.get('classe_id')
        professeur_id = request.form.get('professeur_id')
        coefficient = request.form.get('coefficient', 1)

        # Update course
        cours.nom = nom
        cours.description = description
        cours.coefficient = coefficient
        # Update Enseignement association
        enseignement.classe_id = classe_id
        enseignement.professeur_id = professeur_id
        db.session.commit()

        flash('Cours modifié avec succès!', 'success')
        return redirect(url_for('cours.details', cours_id=cours.id))

    # Get data for form
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    professeurs = User.query.filter_by(role='professeur').order_by(User.nom, User.prenom).all()
    return render_template('cours/modifier.html', cours=cours, classes=classes, professeurs=professeurs, enseignement=enseignement)
