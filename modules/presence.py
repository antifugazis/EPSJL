from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from models import Presence, Eleve, Cours, Classe, Enseignement
from models import db
from datetime import datetime, date, timedelta
from sqlalchemy import func
from modules.auth import admin_required

presence_blueprint = Blueprint('presence', __name__, url_prefix='/presence')

@presence_blueprint.route('/')
@login_required
@admin_required
def index():
    today = date.today().strftime('%Y-%m-%d')
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    
    # Get recent attendance records for quick access
    recent_records = (
        db.session.query(
            Presence.date,
            Cours.nom.label('cours_nom'),
            Classe.nom.label('classe_nom'),
            func.count(Presence.id).label('count')
        )
        .join(Cours, Presence.cours_id == Cours.id)
        .join(Enseignement, Enseignement.cours_id == Cours.id)
        .join(Classe, Enseignement.classe_id == Classe.id)
        .filter(Presence.date >= (date.today() - timedelta(days=7)))
        .group_by(Presence.date, Cours.nom, Classe.nom)
        .order_by(Presence.date.desc())
        .limit(5)
        .all()
    )
    
    return render_template('presence/index.html', classes=classes, today=today, recent_records=recent_records)

@presence_blueprint.route('/saisie', methods=['GET', 'POST'])
@login_required
@admin_required
def saisie():
    if request.method == 'POST':
        try:
            date_presence = request.form.get('date')
            cours_id = request.form.get('cours_id')
            eleves_data = request.form.getlist('eleve_id[]')
            statuts = request.form.getlist('statut[]')
            notes = request.form.getlist('note[]')
            
            # Validate inputs
            if not date_presence or not cours_id or not eleves_data:
                flash('Données manquantes. Veuillez remplir tous les champs obligatoires.', 'danger')
                return redirect(request.referrer or url_for('presence.index'))
                
            # Validate date format
            try:
                date_obj = datetime.strptime(date_presence, '%Y-%m-%d').date()
            except ValueError:
                flash('Format de date invalide.', 'danger')
                return redirect(request.referrer or url_for('presence.index'))
                
            # Validate course exists
            cours = Cours.query.get(cours_id)
            if not cours:
                flash('Cours non trouvé.', 'danger')
                return redirect(url_for('presence.index'))
            
            # Begin transaction
            try:
                # Delete existing records for this date and course
                Presence.query.filter_by(date=date_presence, cours_id=cours_id).delete()
                
                # Insert new attendance records
                for i in range(len(eleves_data)):
                    eleve_id = eleves_data[i]
                    statut = statuts[i] if i < len(statuts) else 'absent'  # Default to absent if missing
                    note = notes[i] if i < len(notes) else None
                    
                    # Validate student exists
                    eleve = Eleve.query.get(eleve_id)
                    if not eleve:
                        continue  # Skip invalid student IDs
                        
                    # Create presence record
                    presence = Presence(
                        eleve_id=eleve_id, 
                        cours_id=cours_id, 
                        date=date_obj,  # Use the date object, not the string
                        statut=statut, 
                        notes=note
                    )
                    db.session.add(presence)
                
                db.session.commit()
                flash('Présences enregistrées avec succès!', 'success')
                
                # Redirect to the same page to allow for consecutive days entry
                # Find the class for redirect via Enseignement
                enseignement = Enseignement.query.filter_by(cours_id=cours_id).first()
                classe_id_for_redirect = enseignement.classe_id if enseignement else None
                return redirect(url_for('presence.saisie', date=date_presence, classe_id=classe_id_for_redirect, cours_id=cours_id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Erreur lors de l\'enregistrement des présences: {str(e)}', 'danger')
                return redirect(request.referrer or url_for('presence.index'))
        
        except Exception as e:
            flash(f'Une erreur est survenue: {str(e)}', 'danger')
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
    if not eleves:
        flash('Aucun élève trouvé dans cette classe.', 'warning')
        # Still show the page but with empty list
        
    existing_presences = Presence.query.filter_by(date=date_presence, cours_id=cours_id).all()
    presence_dict = {p.eleve_id: p for p in existing_presences}
    
    # Get previous and next dates for navigation
    date_obj = datetime.strptime(date_presence, '%Y-%m-%d').date()
    prev_date = (date_obj - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')

    return render_template('presence/saisie.html', 
                          date=date_presence,
                          cours=cours,
                          eleves=eleves,
                          presence_dict=presence_dict,
                          prev_date=prev_date,
                          next_date=next_date)

@presence_blueprint.route('/get_cours_by_classe', methods=['GET'])
@login_required
@admin_required
def get_cours_by_classe():
    try:
        classe_id = request.args.get('classe_id')
        if not classe_id:
            return jsonify([]), 400
            
        # Validate classe exists
        classe = Classe.query.get(classe_id)
        if not classe:
            return jsonify({'error': 'Classe non trouvée'}), 404
            
        cours = db.session.query(Cours).join(Enseignement).filter(Enseignement.classe_id == classe_id).order_by(Cours.nom).all()
        result = [{'id': c.id, 'nom': c.nom} for c in cours]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@presence_blueprint.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_presence(id):
    try:
        presence = Presence.query.get_or_404(id)
        
        # Store info for flash message
        eleve_nom = f"{presence.eleve.nom} {presence.eleve.prenom}"
        date_str = presence.date.strftime('%d/%m/%Y')
        cours_nom = presence.cours.nom
        
        # Delete the record
        db.session.delete(presence)
        db.session.commit()
        
        flash(f'Présence supprimée avec succès pour {eleve_nom} du {date_str} au cours de {cours_nom}.', 'success')
        
        # Redirect back to the referring page or to the report page
        return redirect(request.referrer or url_for('presence.rapport'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de la présence: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('presence.rapport'))


@presence_blueprint.route('/delete_batch', methods=['POST'])
@login_required
@admin_required
def delete_batch_presence():
    try:
        # Get parameters
        date_str = request.form.get('date')
        cours_id = request.form.get('cours_id')
        
        if not date_str or not cours_id:
            flash('Paramètres manquants pour la suppression par lot.', 'danger')
            return redirect(request.referrer or url_for('presence.index'))
            
        # Convert string date to date object
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Format de date invalide.', 'danger')
            return redirect(request.referrer or url_for('presence.index'))
        
        # Validate course exists
        cours = Cours.query.get(cours_id)
        if not cours:
            flash('Cours non trouvé.', 'danger')
            return redirect(request.referrer or url_for('presence.index'))
        
        # Count records to be deleted
        count = Presence.query.filter_by(date=date_obj, cours_id=cours_id).count()
        
        # Delete records
        Presence.query.filter_by(date=date_obj, cours_id=cours_id).delete()
        db.session.commit()
        
        flash(f'{count} présences supprimées avec succès pour le cours {cours.nom} du {date_obj.strftime("%d/%m/%Y")}.', 'success')
        return redirect(request.referrer or url_for('presence.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression des présences: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('presence.index'))

@presence_blueprint.route('/rapport')
@login_required
@admin_required
def rapport():
    try:
        eleve_id = request.args.get('eleve_id')
        cours_id = request.args.get('cours_id')
        classe_id = request.args.get('classe_id')
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        statut_filter = request.args.get('statut')
        export_format = request.args.get('export')

        # If no filters, show the form
        if not (eleve_id or cours_id or classe_id or date_debut or date_fin or statut_filter):
            # Calculate dates for predefined reports
            today = date.today().strftime('%Y-%m-%d')
            
            # Calculate week start (Monday of current week)
            week_start = date.today()
            week_start = week_start - timedelta(days=week_start.weekday())
            week_start = week_start.strftime('%Y-%m-%d')
            
            # Calculate month start (first day of current month)
            month_start = date.today().replace(day=1).strftime('%Y-%m-%d')
            
            classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
            cours = Cours.query.order_by(Cours.nom).all()
            eleves = Eleve.query.filter_by(actif=True).order_by(Eleve.nom, Eleve.prenom).all()
            
            # Get attendance statuses for dropdown
            statuts = [
                {'value': 'present', 'label': 'Présent'},
                {'value': 'absent', 'label': 'Absent'},
                {'value': 'retard', 'label': 'En retard'},
                {'value': 'excuse', 'label': 'Excusé'}
            ]
            
            return render_template('presence/rapport_form.html', 
                                classes=classes,
                                cours=cours,
                                eleves=eleves,
                                statuts=statuts,
                                today=today,
                                week_start=week_start,
                                month_start=month_start)

        # Build ORM query based on filters
        query = Presence.query\
                .join(Eleve, Presence.eleve_id == Eleve.id)\
                .join(Cours, Presence.cours_id == Cours.id)\
                .join(Classe, Cours.classe_id == Classe.id)
                
        if eleve_id:
            query = query.filter(Presence.eleve_id == eleve_id)
        if cours_id:
            query = query.filter(Presence.cours_id == cours_id)
        if classe_id:
            query = query.filter(Classe.id == classe_id)
        if date_debut:
            query = query.filter(Presence.date >= date_debut)
        if date_fin:
            query = query.filter(Presence.date <= date_fin)
        if statut_filter:
            query = query.filter(Presence.statut == statut_filter)
            
        # Order by date (most recent first) and then by student name
        query = query.order_by(Presence.date.desc(), Eleve.nom, Eleve.prenom)
        
        # Execute query
        presences = query.all()

        # Prepare stats
        stats = {
            'total': len(presences),
            'present': sum(1 for p in presences if p.statut == 'present'),
            'absent': sum(1 for p in presences if p.statut == 'absent'),
            'retard': sum(1 for p in presences if p.statut == 'retard'),
            'excuse': sum(1 for p in presences if p.statut == 'excuse')
        }
        
        # Calculate attendance rate
        if stats['total'] > 0:
            stats['attendance_rate'] = round((stats['present'] + stats['retard'] + stats['excuse']) / stats['total'] * 100, 1)
        else:
            stats['attendance_rate'] = 0
            
        # Calculate absence rate
        if stats['total'] > 0:
            stats['absence_rate'] = round(stats['absent'] / stats['total'] * 100, 1)
        else:
            stats['absence_rate'] = 0
            
        # Group by student for student-specific statistics if needed
        student_stats = {}
        if not eleve_id and stats['total'] > 0:
            for p in presences:
                if p.eleve_id not in student_stats:
                    student_stats[p.eleve_id] = {
                        'eleve': p.eleve,
                        'total': 0,
                        'present': 0,
                        'absent': 0,
                        'retard': 0,
                        'excuse': 0
                    }
                student_stats[p.eleve_id]['total'] += 1
                student_stats[p.eleve_id][p.statut] += 1
                
            # Calculate rates for each student
            for student_id, stat in student_stats.items():
                if stat['total'] > 0:
                    stat['attendance_rate'] = round((stat['present'] + stat['retard'] + stat['excuse']) / stat['total'] * 100, 1)
                    stat['absence_rate'] = round(stat['absent'] / stat['total'] * 100, 1)
                else:
                    stat['attendance_rate'] = 0
                    stat['absence_rate'] = 0

        # Handle CSV export if requested
        if export_format == 'csv':
            import csv
            from io import StringIO
            from flask import Response
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Date', 'Matricule', 'Nom', 'Prénom', 'Cours', 'Statut', 'Notes'])
            
            # Write data
            for p in presences:
                writer.writerow([
                    p.date.strftime('%Y-%m-%d'),
                    p.eleve.matricule,
                    p.eleve.nom,
                    p.eleve.prenom,
                    p.cours.nom,
                    p.statut,
                    p.notes or ''
                ])
                
            # Create response
            output.seek(0)
            return Response(
                output,
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment;filename=rapport_presence.csv"}
            )

        return render_template('presence/rapport_resultats.html', 
                            presences=presences,
                            stats=stats,
                            student_stats=student_stats if student_stats else None,
                            filters={
                                'eleve_id': eleve_id,
                                'cours_id': cours_id,
                                'classe_id': classe_id,
                                'date_debut': date_debut,
                                'date_fin': date_fin,
                                'statut': statut_filter
                            })
    except Exception as e:
        flash(f'Erreur lors de la génération du rapport: {str(e)}', 'danger')
        return redirect(url_for('presence.rapport'))
