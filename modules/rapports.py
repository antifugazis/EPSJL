from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required
from models import *
from models import db
from datetime import datetime, date, timedelta


rapports_blueprint = Blueprint('rapports', __name__, url_prefix='/rapports')

# Helper function to check if user has admin privileges
def is_admin_or_directeur():
    return session.get('user_role') in ['admin', 'directeur']

@rapports_blueprint.route('/')
@login_required
def index():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
    
    return render_template('rapports/index.html')

@rapports_blueprint.route('/statistiques')
@login_required
def statistiques():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
    
    total_eleves = Eleve.query.filter_by(actif=1).count()
    eleves_par_sexe = db.session.query(Eleve.sexe, func.count(Eleve.id)).filter_by(actif=1).group_by(Eleve.sexe).all()
    eleves_par_classe = db.session.query(Classe.nom, func.count(Eleve.id)).join(Eleve, Classe.id == Eleve.classe_id).filter(Eleve.actif==1).group_by(Classe.id).order_by(Classe.niveau, Classe.nom).all()
    presences_mois = db.session.query(Presence.statut, func.count(Presence.id)).filter(func.extract('month', Presence.date) == date.today().month, func.extract('year', Presence.date) == date.today().year).group_by(Presence.statut).all()
    revenus_annee = db.session.query(func.sum(Paiement.montant)).filter(func.extract('year', Paiement.date) == date.today().year).scalar() or 0
    revenus_par_mois = db.session.query(func.extract('month', Paiement.date), func.sum(Paiement.montant)).filter(func.extract('year', Paiement.date) == date.today().year).group_by(func.extract('month', Paiement.date)).order_by(func.extract('month', Paiement.date)).all()
    revenus_par_type = db.session.query(Frais.type, func.sum(Paiement.montant)).join(Paiement, Frais.id == Paiement.frais_id).filter(func.extract('year', Paiement.date) == date.today().year).group_by(Frais.type).all()
    moyennes_par_classe = db.session.query(Classe.nom, func.avg(Note.note / Note.sur * 20)).join(Note, Classe.id == Note.classe_id).join(Eleve, Note.eleve_id == Eleve.id).filter(Note.trimestre == db.session.query(func.max(Note.trimestre))).group_by(Classe.id).order_by(Classe.niveau, Classe.nom).all()
    return render_template('rapports/statistiques.html',
                          total_eleves=total_eleves,
                          eleves_par_sexe=eleves_par_sexe,
                          eleves_par_classe=eleves_par_classe,
                          presences_mois=presences_mois,
                          revenus_annee=revenus_annee,
                          revenus_par_mois=revenus_par_mois,
                          revenus_par_type=revenus_par_type,
                          moyennes_par_classe=moyennes_par_classe)

@rapports_blueprint.route('/academique')
@login_required
def academique():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
    
    classe_id = request.args.get('classe_id')
    trimestre = request.args.get('trimestre')
    
    if not classe_id or not trimestre:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Get all classes
                cursor.execute("SELECT id, nom FROM classes ORDER BY niveau, nom")
                classes = cursor.fetchall()
                
                # Get all trimesters
                cursor.execute("SELECT DISTINCT trimestre FROM notes ORDER BY trimestre")
                trimestres = cursor.fetchall()
        finally:
            conn.close()
        
        return render_template('rapports/academique_form.html',
                              classes=classes,
                              trimestres=trimestres)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get class info
            cursor.execute("SELECT * FROM classes WHERE id = %s", (classe_id,))
            classe = cursor.fetchone()
            
            if not classe:
                flash('Classe non trouvée.', 'danger')
                return redirect(url_for('rapports.academique'))
            
            # Get all students in this class
            cursor.execute("""
                SELECT id, matricule, nom, prenom
                FROM eleves
                WHERE classe_id = %s AND actif = 1
                ORDER BY nom, prenom
            """, (classe_id,))
            eleves = cursor.fetchall()
            
            # Get all courses for this class
            cursor.execute("""
                SELECT id, nom, coefficient
                FROM cours
                WHERE classe_id = %s
                ORDER BY nom
            """, (classe_id,))
            cours = cursor.fetchall()
            
            # Get all grades for these students in the selected trimester
            cursor.execute("""
                SELECT n.*, e.nom as eleve_nom, e.prenom as eleve_prenom, c.nom as cours_nom
                FROM notes n
                JOIN eleves e ON n.eleve_id = e.id
                JOIN cours c ON n.cours_id = c.id
                WHERE e.classe_id = %s AND n.trimestre = %s
                ORDER BY e.nom, e.prenom, c.nom
            """, (classe_id, trimestre))
            notes = cursor.fetchall()
            
            # Organize grades by student and course
            resultats = {}
            for eleve in eleves:
                resultats[eleve['id']] = {
                    'eleve': eleve,
                    'cours': {},
                    'moyenne_generale': 0
                }
            
            for note in notes:
                eleve_id = note['eleve_id']
                cours_id = note['cours_id']
                
                if eleve_id in resultats:
                    if cours_id not in resultats[eleve_id]['cours']:
                        resultats[eleve_id]['cours'][cours_id] = {
                            'notes': [],
                            'moyenne': 0
                        }
                    
                    resultats[eleve_id]['cours'][cours_id]['notes'].append(note)
            
            # Calculate averages for each student and course
            for eleve_id, data in resultats.items():
                total_points = 0
                total_coef = 0
                
                for cours_id, cours_data in data['cours'].items():
                    if cours_data['notes']:
                        total = sum(n['note'] / n['sur'] * 20 for n in cours_data['notes'])
                        moyenne = total / len(cours_data['notes'])
                        cours_data['moyenne'] = moyenne
                        
                        # Find course coefficient
                        for c in cours:
                            if c['id'] == cours_id:
                                coef = c['coefficient']
                                total_points += moyenne * coef
                                total_coef += coef
                                break
                
                if total_coef > 0:
                    data['moyenne_generale'] = total_points / total_coef
            
            # Sort students by average
            resultats_tries = sorted(resultats.values(), key=lambda x: x['moyenne_generale'], reverse=True)
    finally:
        conn.close()
    
    return render_template('rapports/academique_resultats.html',
                          classe=classe,
                          trimestre=trimestre,
                          cours=cours,
                          resultats=resultats_tries)

@rapports_blueprint.route('/presence')
@login_required
def presence():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
    
    classe_id = request.args.get('classe_id')
    date_debut = request.args.get('date_debut', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_fin = request.args.get('date_fin', date.today().strftime('%Y-%m-%d'))
    
    if not classe_id:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Get all classes
                cursor.execute("SELECT id, nom FROM classes ORDER BY niveau, nom")
                classes = cursor.fetchall()
        finally:
            conn.close()
        
        return render_template('rapports/presence_form.html',
                              classes=classes,
                              date_debut=date_debut,
                              date_fin=date_fin)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get class info
            cursor.execute("SELECT * FROM classes WHERE id = %s", (classe_id,))
            classe = cursor.fetchone()
            
            if not classe:
                flash('Classe non trouvée.', 'danger')
                return redirect(url_for('rapports.presence'))
            
            # Get all students in this class
            cursor.execute("""
                SELECT id, matricule, nom, prenom
                FROM eleves
                WHERE classe_id = %s AND actif = 1
                ORDER BY nom, prenom
            """, (classe_id,))
            eleves = cursor.fetchall()
            
            # Get attendance for these students in the selected period
            cursor.execute("""
                SELECT p.*, e.nom as eleve_nom, e.prenom as eleve_prenom, c.nom as cours_nom
                FROM presences p
                JOIN eleves e ON p.eleve_id = e.id
                JOIN cours c ON p.cours_id = c.id
                WHERE e.classe_id = %s AND p.date BETWEEN %s AND %s
                ORDER BY p.date, e.nom, e.prenom
            """, (classe_id, date_debut, date_fin))
            presences = cursor.fetchall()
            
            # Organize attendance by student
            resultats = {}
            for eleve in eleves:
                resultats[eleve['id']] = {
                    'eleve': eleve,
                    'present': 0,
                    'absent': 0,
                    'retard': 0,
                    'excuse': 0,
                    'total': 0,
                    'taux_presence': 0
                }
            
            for presence in presences:
                eleve_id = presence['eleve_id']
                
                if eleve_id in resultats:
                    resultats[eleve_id][presence['statut']] += 1
                    resultats[eleve_id]['total'] += 1
            
            # Calculate attendance rate
            for eleve_id, data in resultats.items():
                if data['total'] > 0:
                    data['taux_presence'] = (data['present'] + data['retard'] + data['excuse']) / data['total'] * 100
            
            # Sort students by attendance rate
            resultats_tries = sorted(resultats.values(), key=lambda x: x['taux_presence'], reverse=True)
    finally:
        conn.close()
    
    return render_template('rapports/presence_resultats.html',
                          classe=classe,
                          date_debut=date_debut,
                          date_fin=date_fin,
                          resultats=resultats_tries)

@rapports_blueprint.route('/financier')
@login_required
def financier():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
    
    date_debut = request.args.get('date_debut', (date.today().replace(month=1, day=1)).strftime('%Y-%m-%d'))
    date_fin = request.args.get('date_fin', date.today().strftime('%Y-%m-%d'))
    type_frais = request.args.get('type_frais')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Build query based on filters
            query = """
                SELECT p.*, e.matricule, e.nom as eleve_nom, e.prenom as eleve_prenom,
                       f.type as frais_type, f.description as frais_description,
                       c.nom as classe_nom
                FROM paiements p
                JOIN eleves e ON p.eleve_id = e.id
                JOIN frais f ON p.frais_id = f.id
                LEFT JOIN classes c ON e.classe_id = c.id
                WHERE p.date BETWEEN %s AND %s
            """
            params = [date_debut, date_fin]
            
            if type_frais:
                query += " AND f.type = %s"
                params.append(type_frais)
            
            query += " ORDER BY p.date"
            
            cursor.execute(query, params)
            paiements = cursor.fetchall()
            
            # Get summary by fee type
            cursor.execute("""
                SELECT f.type, SUM(p.montant) as total
                FROM paiements p
                JOIN frais f ON p.frais_id = f.id
                WHERE p.date BETWEEN %s AND %s
                GROUP BY f.type
            """, (date_debut, date_fin))
            resume_par_type = cursor.fetchall()
            
            # Get summary by class
            cursor.execute("""
                SELECT c.nom, SUM(p.montant) as total
                FROM paiements p
                JOIN eleves e ON p.eleve_id = e.id
                LEFT JOIN classes c ON e.classe_id = c.id
                WHERE p.date BETWEEN %s AND %s
                GROUP BY c.id
            """, (date_debut, date_fin))
            resume_par_classe = cursor.fetchall()
            
            # Get summary by month
            cursor.execute("""
                SELECT YEAR(p.date) as annee, MONTH(p.date) as mois, SUM(p.montant) as total
                FROM paiements p
                WHERE p.date BETWEEN %s AND %s
                GROUP BY YEAR(p.date), MONTH(p.date)
                ORDER BY YEAR(p.date), MONTH(p.date)
            """, (date_debut, date_fin))
            resume_par_mois = cursor.fetchall()
            
            # Get total
            total = sum(p['montant'] for p in paiements)
    finally:
        conn.close()
    
    return render_template('rapports/financier.html',
                          date_debut=date_debut,
                          date_fin=date_fin,
                          type_frais=type_frais,
                          paiements=paiements,
                          resume_par_type=resume_par_type,
                          resume_par_classe=resume_par_classe,
                          resume_par_mois=resume_par_mois,
                          total=total)
