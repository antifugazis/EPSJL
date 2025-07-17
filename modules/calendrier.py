from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required
from models import Evenement
from models import db
from datetime import datetime, date, timedelta


calendrier_blueprint = Blueprint('calendrier', __name__, url_prefix='/calendrier')

@calendrier_blueprint.route('/')
def index():
    from models import Evenement
    # Get month and year from query parameters, default to current month/year
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
        
    # Get current date for highlighting today in the calendar
    now = datetime.now().date()
    # Validate month and year
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    # Get events for this month using ORM
    events = Evenement.query.filter(Evenement.date.between(first_day, last_day)).order_by(Evenement.date, Evenement.heure_debut).all()
    # Organize events by day
    events_by_day = {}
    for event in events:
        day = event.date.day
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)
    calendar_data = []
    first_weekday = first_day.weekday()
    for _ in range(first_weekday):
        calendar_data.append({'day': None, 'events': []})
    for day in range(1, last_day.day + 1):
        calendar_data.append({'day': day, 'events': events_by_day.get(day, [])})
    while len(calendar_data) % 7 != 0:
        calendar_data.append({'day': None, 'events': []})
    weeks = []
    for i in range(0, len(calendar_data), 7):
        weeks.append(calendar_data[i:i+7])
    month_name = first_day.strftime('%B')
    return render_template('calendrier/index.html',
                          weeks=weeks,
                          month=month,
                          year=year,
                          month_name=month_name,
                          prev_month=(month - 1) if month > 1 else 12,
                          prev_year=year if month > 1 else year - 1,
                          next_month=(month + 1) if month < 12 else 1,
                          next_year=year if month < 12 else year + 1,
                          now=now)

@calendrier_blueprint.route('/evenements')
@login_required
def evenements():
    from models import Evenement, User
    from sqlalchemy import desc
    from datetime import date
    
    # Get upcoming events
    evenements_a_venir = Evenement.query.join(
        User, Evenement.organisateur_id == User.id, isouter=True
    ).filter(
        Evenement.date >= date.today()
    ).order_by(
        Evenement.date, Evenement.heure_debut
    ).limit(20).all()
    
    # Get past events
    evenements_passes = Evenement.query.join(
        User, Evenement.organisateur_id == User.id, isouter=True
    ).filter(
        Evenement.date < date.today()
    ).order_by(
        desc(Evenement.date), Evenement.heure_debut
    ).limit(20).all()
    
    return render_template('calendrier/evenements.html',
                          evenements_a_venir=evenements_a_venir,
                          evenements_passes=evenements_passes)

@calendrier_blueprint.route('/evenements/<int:evenement_id>')
def details(evenement_id):
    from models import Evenement, User
    
    # Get event with organizer information
    event = Evenement.query.join(
        User, Evenement.organisateur_id == User.id, isouter=True
    ).add_columns(
        Evenement, 
        User.prenom.label('organisateur_prenom'),
        User.nom.label('organisateur_nom')
    ).filter(Evenement.id == evenement_id).first()
    
    if not event:
        flash('Événement non trouvé.', 'danger')
        return redirect(url_for('calendrier.index'))
        
    # Extract the event object from the result
    event_data = event[0]
    event_data.organisateur_prenom = event.organisateur_prenom
    event_data.organisateur_nom = event.organisateur_nom
    
    return render_template('calendrier/details.html', event=event_data)

@calendrier_blueprint.route('/evenements/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter():
    # Check if user has admin or director privileges
    if not session.get('user_role') in ['admin', 'directeur', 'professeur']:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('calendrier.evenements'))
    
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        date_event = request.form['date']
        heure_debut = request.form['heure_debut']
        heure_fin = request.form['heure_fin']
        lieu = request.form['lieu']
        public = int(request.form.get('public', 0))
        important = int(request.form.get('important', 0))
        event = Evenement(
            titre=titre,
            description=description,
            date=date_event,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            lieu=lieu,
            public=public,
            important=important
        )
        db.session.add(event)
        db.session.commit()
        flash('Événement ajouté avec succès!', 'success')
        return redirect(url_for('calendrier.index'))
    return render_template('calendrier/ajouter.html')

@calendrier_blueprint.route('/evenements/<int:evenement_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier(evenement_id):
    # Check if user has admin or director privileges
    if not session.get('user_role') in ['admin', 'directeur', 'professeur']:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('calendrier.evenements'))
    
    event = Evenement.query.get(evenement_id)
    if not event:
        flash('Événement non trouvé.', 'danger')
        return redirect(url_for('calendrier.evenements'))
    
    # Check if user is the organizer or has admin/director privileges
    if event.organisateur_id != session.get('user_id') and session.get('user_role') not in ['admin', 'directeur']:
        flash('Vous n\'êtes pas autorisé à modifier cet événement.', 'danger')
        return redirect(url_for('calendrier.evenements'))
    
    if request.method == 'POST':
        event.titre = request.form['titre']
        event.description = request.form['description']
        event.date = request.form['date']
        event.heure_debut = request.form['heure_debut']
        event.heure_fin = request.form['heure_fin']
        event.lieu = request.form['lieu']
        event.public = int(request.form.get('public', 0))
        event.important = int(request.form.get('important', 0))
        db.session.commit()
        flash('Événement modifié avec succès!', 'success')
        return redirect(url_for('calendrier.details', evenement_id=evenement_id))
    return render_template('calendrier/modifier.html', event=event)

@calendrier_blueprint.route('/evenements/<int:evenement_id>/supprimer', methods=['POST'])
@login_required
def supprimer(evenement_id):
    # Check if user has admin or director privileges
    if not session.get('user_role') in ['admin', 'directeur', 'professeur']:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('calendrier.evenements'))
    
    event = Evenement.query.get(evenement_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        flash('Événement supprimé avec succès!', 'success')
    return redirect(url_for('calendrier.index'))

@calendrier_blueprint.route('/api/evenements', methods=['GET'])
def api_evenements():
    from models import Evenement
    from datetime import datetime
    
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify([])
    
    # Convert string dates to datetime objects
    try:
        start_date = datetime.strptime(start_date.split('T')[0], '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date.split('T')[0], '%Y-%m-%d').date()
    except ValueError:
        return jsonify([]), 400
    
    # Get events between start and end dates
    events = Evenement.query.filter(
        Evenement.date.between(start_date, end_date)
    ).order_by(Evenement.date, Evenement.heure_debut).all()
    
    # Format events for FullCalendar
    formatted_events = []
    for event in events:
        start_time = event.heure_debut.strftime('%H:%M:%S') if event.heure_debut else '00:00:00'
        end_time = event.heure_fin.strftime('%H:%M:%S') if event.heure_fin else '23:59:59'
        
        formatted_events.append({
            'id': event.id,
            'title': event.titre,
            'start': f"{event.date.strftime('%Y-%m-%d')}T{start_time}",
            'end': f"{event.date.strftime('%Y-%m-%d')}T{end_time}",
            'description': event.description,
            'location': event.lieu,
            'color': get_event_color(event.type),
            'url': url_for('calendrier.details', evenement_id=event.id)
        })
    
    return jsonify(formatted_events)

def get_event_color(event_type):
    colors = {
        'academique': '#4285F4',  # Blue
        'sportif': '#34A853',     # Green
        'culturel': '#FBBC05',    # Yellow
        'religieux': '#9C27B0',   # Purple
        'administratif': '#EA4335', # Red
        'autre': '#757575'        # Gray
    }
    return colors.get(event_type, '#757575')
