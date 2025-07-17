from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required
from models import Note, Eleve, Cours
from models import db
from datetime import datetime, date


notes_blueprint = Blueprint('notes', __name__, url_prefix='/notes')

@notes_blueprint.route('/')
@login_required
def index():
    from models import Classe
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    return render_template('notes/index.html', classes=classes)

@notes_blueprint.route('/saisie', methods=['GET', 'POST'])
@login_required
def saisie():
    if request.method == 'POST':
        cours_id = request.form.get('cours_id')
        trimestre = request.form.get('trimestre')
        type_note = request.form.get('type')
        date_note = request.form.get('date')
        eleves_data = request.form.getlist('eleve_id[]')
        notes = request.form.getlist('note[]')
        sur = request.form.get('sur', 20)
        commentaires = request.form.getlist('commentaire[]')
        
        from models import Note
        from datetime import datetime
        # Ensure date_note is a datetime.date object
        if isinstance(date_note, str):
            date_note = datetime.strptime(date_note, "%Y-%m-%d").date()
        for i in range(len(eleves_data)):
            eleve_id = eleves_data[i]
            note_value = notes[i] if i < len(notes) and notes[i] else 0
            commentaire = commentaires[i] if i < len(commentaires) else None
            existing = Note.query.filter_by(eleve_id=eleve_id, cours_id=cours_id, trimestre=trimestre, type=type_note).first()
            if existing:
                existing.valeur = note_value
                existing.sur = sur
                existing.date = date_note
                existing.commentaire = commentaire
            else:
                new_note = Note(
                    eleve_id=eleve_id,
                    cours_id=cours_id,
                    trimestre=trimestre,
                    type=type_note,
                    valeur=note_value,
                    sur=sur,
                    date=date_note,
                    commentaire=commentaire
                )
                db.session.add(new_note)
        db.session.commit()
        flash('Notes enregistrées avec succès!', 'success')
        return redirect(url_for('notes.index'))
    
    # GET request - show form
    classe_id = request.args.get('classe_id')
    cours_id = request.args.get('cours_id')
    trimestre = request.args.get('trimestre', 1)
    type_note = request.args.get('type', 'devoir')
    
    if not classe_id or not cours_id:
        flash('Veuillez sélectionner une classe et un cours.', 'warning')
        return redirect(url_for('notes.index'))

    from models import Cours, Classe
    cours = Cours.query.filter_by(id=cours_id).first()
    if not cours:
        flash('Cours non trouvé.', 'danger')
        return redirect(url_for('notes.index'))
    classe_nom = Classe.query.get(classe_id).nom if classe_id else None
    from models import Eleve, Note
    eleves = Eleve.query.filter_by(classe_id=classe_id, actif=1).order_by(Eleve.nom, Eleve.prenom).all()
    existing_notes = Note.query.join(Eleve, Note.eleve_id == Eleve.id)
    existing_notes = existing_notes.filter(
        Note.cours_id == cours_id,
        Note.trimestre == trimestre,
        Note.type == type_note,
        Eleve.classe_id == classe_id
    ).all()
    notes_dict = {n.eleve_id: n for n in existing_notes}
    return render_template('notes/saisie.html',
                          cours=cours,
                          eleves=eleves,
                          notes_dict=notes_dict,
                          trimestre=trimestre,
                          type_note=type_note,
                          date_note=date.today().strftime('%Y-%m-%d'))

@notes_blueprint.route('/bulletin')
@login_required
def bulletin():
    eleve_id = request.args.get('eleve_id')
    trimestre = request.args.get('trimestre')
    
    if not eleve_id or not trimestre:
        # Show form to select student and trimester
        from models import Classe
        classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
        return render_template('notes/bulletin_form.html', classes=classes)
    
    from models import Eleve, Classe, Cours, Note, User
    eleve = Eleve.query.filter_by(id=eleve_id).first()
    if not eleve:
        flash('Élève non trouvé.', 'danger')
        return redirect(url_for('notes.bulletin'))
    classe_nom = Classe.query.get(eleve.classe_id).nom if eleve.classe_id else None
    # Get all courses for this student's class via Enseignement
    from models import Enseignement
    cours = (
        Cours.query
        .join(Enseignement, Enseignement.cours_id == Cours.id)
        .filter(Enseignement.classe_id == eleve.classe_id)
        .order_by(Cours.nom)
        .all()
    )
    # Get all grades for this student in the selected trimester
    notes = (Note.query
             .join(Cours, Note.cours_id == Cours.id)
             .filter(Note.eleve_id == eleve_id, Note.trimestre == trimestre)
             .order_by(Cours.nom, Note.type)
             .all())
            
    # Organize grades by course
    notes_by_cours = {}
    for note in notes:
        cours_id = note.cours_id
        if cours_id not in notes_by_cours:
            notes_by_cours[cours_id] = []
        notes_by_cours[cours_id].append(note)
    
    # Calculate averages for each course
    moyennes = {}
    for cours_id, cours_notes in notes_by_cours.items():
        total = sum(n.valeur / n.sur * 20 for n in cours_notes)
        moyenne = total / len(cours_notes) if cours_notes else 0
        moyennes[cours_id] = moyenne
    
    # Calculate overall average
    if moyennes:
        total_coef = sum(c.coefficient for c in cours if c.id in moyennes)
        total_points = sum(moyennes[c.id] * c.coefficient for c in cours if c.id in moyennes)
        moyenne_generale = total_points / total_coef if total_coef > 0 else 0
    else:
        moyenne_generale = 0
    
    # Get class ranking using ORM
    from models import Eleve, Note
    from sqlalchemy import func
    classement_query = (
        db.session.query(
            Eleve.id,
            Eleve.nom,
            Eleve.prenom,
            func.avg(Note.valeur / Note.sur * 20).label('moyenne')
        )
        .join(Note, Eleve.id == Note.eleve_id)
        .filter(Eleve.classe_id == eleve.classe_id, Note.trimestre == trimestre)
        .group_by(Eleve.id)
        .order_by(func.avg(Note.valeur / Note.sur * 20).desc())
    )
    classement = classement_query.all()
    # Find student's rank
    rang = 1
    for c in classement:
        if c.id == eleve.id:
            break
        rang += 1
    return render_template('notes/bulletin.html',
                          eleve=eleve,
                          trimestre=trimestre,
                          cours=cours,
                          notes_by_cours=notes_by_cours,
                          moyennes=moyennes,
                          moyenne_generale=moyenne_generale,
                          rang=rang,
                          effectif=len(classement))

@notes_blueprint.route('/get_eleves_by_classe', methods=['GET'])
@login_required
def get_eleves_by_classe():
    classe_id = request.args.get('classe_id')
    
    if not classe_id:
        return jsonify([])
    
    from models import Eleve
    eleves = Eleve.query.filter_by(classe_id=classe_id, actif=1).order_by(Eleve.nom, Eleve.prenom).all()
    eleves_list = [
        {
            'id': e.id,
            'matricule': e.matricule,
            'nom': e.nom,
            'prenom': e.prenom
        } for e in eleves
    ]
    return jsonify(eleves_list)

@notes_blueprint.route('/toutes-les-notes')
@login_required
def toutes_les_notes():
    """Display all notes for all students"""
    # Get filter parameters
    classe_id = request.args.get('classe_id')
    trimestre = request.args.get('trimestre', '1')
    cours_id = request.args.get('cours_id')
    
    # Get all classes for the filter dropdown
    from models import Classe, Cours
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    cours_list = Cours.query.order_by(Cours.nom).all()
    
    # Build the query
    from models import Note, Eleve
    query = Note.query.join(Eleve, Note.eleve_id == Eleve.id).join(Cours, Note.cours_id == Cours.id)
    
    # Apply filters
    if classe_id:
        query = query.filter(Eleve.classe_id == classe_id)
    if trimestre:
        query = query.filter(Note.trimestre == trimestre)
    if cours_id:
        query = query.filter(Note.cours_id == cours_id)
    
    # Get the notes with student and course information
    notes = query.order_by(Eleve.nom, Eleve.prenom, Cours.nom).all()
    
    return render_template('notes/toutes_les_notes.html', 
                           notes=notes, 
                           classes=classes,
                           cours_list=cours_list,
                           selected_classe_id=classe_id,
                           selected_trimestre=trimestre,
                           selected_cours_id=cours_id)
