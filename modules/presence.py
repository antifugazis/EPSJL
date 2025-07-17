from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required
from models import Presence, Eleve, Cours
from models import db
from datetime import datetime, date


presence_blueprint = Blueprint('presence', __name__, url_prefix='/presence')

@presence_blueprint.route('/')
@login_required
def index():
    today = date.today().strftime('%Y-%m-%d')
    from models import Classe
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    return render_template('presence/index.html', classes=classes, today=today)

@presence_blueprint.route('/saisie', methods=['GET', 'POST'])
@login_required
def saisie():
    if request.method == 'POST':
        date_presence = request.form.get('date')
        cours_id = request.form.get('cours_id')
        eleves_data = request.form.getlist('eleve_id[]')
        statuts = request.form.getlist('statut[]')
        notes = request.form.getlist('note[]')

        # Delete existing records for this date and course
        Presence.query.filter_by(date=date_presence, cours_id=cours_id).delete()
        db.session.commit()

        # Insert new attendance records
        for i in range(len(eleves_data)):
            eleve_id = eleves_data[i]
            statut = statuts[i]
            note = notes[i] if i < len(notes) else None
            presence = Presence(eleve_id=eleve_id, cours_id=cours_id, date=date_presence, statut=statut, notes=note)
            db.session.add(presence)
        db.session.commit()

        flash('Présences enregistrées avec succès!', 'success')
        return redirect(url_for('presence.index'))

    # GET request - show form
    date_presence = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    classe_id = request.args.get('classe_id')
    cours_id = request.args.get('cours_id')

    if not classe_id or not cours_id:
        flash('Veuillez sélectionner une classe et un cours.', 'warning')
        return redirect(url_for('presence.index'))

    cours = Cours.query.filter_by(id=cours_id).first()
    if not cours:
        flash('Cours non trouvé.', 'danger')
        return redirect(url_for('presence.index'))

    eleves = Eleve.query.filter_by(classe_id=classe_id, actif=True).order_by(Eleve.nom, Eleve.prenom).all()
    existing_presences = Presence.query.filter_by(date=date_presence, cours_id=cours_id).all()
    presence_dict = {p.eleve_id: p for p in existing_presences}

    return render_template('presence/saisie.html', 
                          date=date_presence,
                          cours=cours,
                          eleves=eleves,
                          presence_dict=presence_dict)

@presence_blueprint.route('/get_cours_by_classe', methods=['GET'])
@login_required
def get_cours_by_classe():
    from models import Cours
    classe_id = request.args.get('classe_id')
    if not classe_id:
        return jsonify([])
    cours = Cours.query.filter_by(classe_id=classe_id).order_by(Cours.nom).all()
    result = [{'id': c.id, 'nom': c.nom} for c in cours]
    return jsonify(result)

@presence_blueprint.route('/rapport')
@login_required
def rapport():
    from models import Presence, Eleve, Cours, Classe
    eleve_id = request.args.get('eleve_id')
    cours_id = request.args.get('cours_id')
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    # If no filters, show the form
    if not (eleve_id or cours_id or date_debut or date_fin):
        # Calculate dates for predefined reports
        today = date.today().strftime('%Y-%m-%d')
        
        # Calculate week start (Monday of current week)
        week_start = date.today()
        week_start = week_start - datetime.timedelta(days=week_start.weekday())
        week_start = week_start.strftime('%Y-%m-%d')
        
        # Calculate month start (first day of current month)
        month_start = date.today().replace(day=1).strftime('%Y-%m-%d')
        
        classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
        cours = Cours.query.order_by(Cours.nom).all()
        eleves = Eleve.query.filter_by(actif=True).order_by(Eleve.nom, Eleve.prenom).all()
        return render_template('presence/rapport_form.html', 
                              classes=classes,
                              cours=cours,
                              eleves=eleves,
                              today=today,
                              week_start=week_start,
                              month_start=month_start)

    # Build ORM query based on filters
    query = Presence.query.join(Eleve, Presence.eleve_id == Eleve.id)
    if eleve_id:
        query = query.filter(Presence.eleve_id == eleve_id)
    if cours_id:
        query = query.filter(Presence.cours_id == cours_id)
    if date_debut:
        query = query.filter(Presence.date >= date_debut)
    if date_fin:
        query = query.filter(Presence.date <= date_fin)
    presences = query.order_by(Presence.date.desc()).all()

    # Prepare stats
    stats = {
        'total': len(presences),
        'present': sum(1 for p in presences if p.statut == 'present'),
        'absent': sum(1 for p in presences if p.statut == 'absent'),
        'retard': sum(1 for p in presences if p.statut == 'retard'),
        'excuse': sum(1 for p in presences if p.statut == 'excuse')
    }

    return render_template('presence/rapport_resultats.html', 
                          presences=presences,
                          stats=stats,
                          filters={
                              'eleve_id': eleve_id,
                              'cours_id': cours_id,
                              'date_debut': date_debut,
                              'date_fin': date_fin
                          })
