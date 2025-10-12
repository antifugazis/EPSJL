from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, ResultatAdmission
from datetime import datetime

resultats_admission_bp = Blueprint('resultats_admission', __name__, url_prefix='/admission')

# Route publique pour consulter les résultats d'admission
@resultats_admission_bp.route('/', methods=['GET', 'POST'])
def consulter():
    """Page publique pour consulter les résultats d'admission"""
    resultat = None
    
    if request.method == 'POST':
        nom_complet = request.form.get('nom_complet', '').strip()
        date_naissance = request.form.get('date_naissance', '').strip()
        
        if nom_complet and date_naissance:
            # Rechercher le résultat (insensible à la casse)
            resultat = ResultatAdmission.query.filter(
                db.func.lower(ResultatAdmission.nom_complet) == nom_complet.lower(),
                ResultatAdmission.date_naissance == datetime.strptime(date_naissance, '%Y-%m-%d').date(),
                ResultatAdmission.publie == True
            ).first()
    
    return render_template('admission/consulter.html', resultat=resultat)

# Routes admin pour gérer les résultats d'admission
@resultats_admission_bp.route('/admin/liste')
def admin_liste():
    """Liste des demandes d'admission (admin)"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    type_examen = request.args.get('type_examen')
    statut = request.args.get('statut')
    
    query = ResultatAdmission.query
    
    if type_examen:
        query = query.filter_by(type_examen=type_examen)
    if statut:
        query = query.filter_by(statut=statut)
    
    resultats = query.order_by(ResultatAdmission.date_soumission.desc()).all()
    
    # Récupérer les types d'examen pour les filtres
    types_examen = db.session.query(ResultatAdmission.type_examen).distinct().all()
    types_examen = [t[0] for t in types_examen if t[0]]
    
    return render_template('admin/resultats_admission/liste.html', 
                         resultats=resultats, 
                         types_examen=types_examen,
                         type_examen_actif=type_examen,
                         statut_actif=statut)

@resultats_admission_bp.route('/admin/<int:demande_id>')
def admin_view(demande_id):
    """Voir les détails d'une demande d'admission"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    demande = ResultatAdmission.query.get_or_404(demande_id)
    return render_template('admin/view_admission.html', demande=demande)

@resultats_admission_bp.route('/admin/<int:demande_id>/notes', methods=['POST'])
def admin_save_notes(demande_id):
    """Enregistrer les notes administratives"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    demande = ResultatAdmission.query.get_or_404(demande_id)
    data = request.get_json()
    demande.notes_admin = data.get('notes', '')
    db.session.commit()
    
    return jsonify({'success': True})

@resultats_admission_bp.route('/admin/<int:demande_id>/statut', methods=['POST'])
def admin_update_statut(demande_id):
    """Mettre à jour le statut d'une demande"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    demande = ResultatAdmission.query.get_or_404(demande_id)
    data = request.get_json()
    demande.statut = data.get('statut')
    db.session.commit()
    
    return jsonify({'success': True})

@resultats_admission_bp.route('/admin/<int:demande_id>/delete', methods=['DELETE'])
def admin_delete(demande_id):
    """Supprimer une demande d'admission"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    demande = ResultatAdmission.query.get_or_404(demande_id)
    db.session.delete(demande)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Demande supprimée avec succès'})
