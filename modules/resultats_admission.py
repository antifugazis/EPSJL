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
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        classe = request.form.get('classe', '').strip()
        promotion = request.form.get('promotion', '').strip()
        
        if nom and classe and promotion:
            # Rechercher le résultat (insensible à la casse)
            resultat = ResultatAdmission.query.filter(
                db.func.lower(ResultatAdmission.nom) == nom.lower(),
                ResultatAdmission.classe == classe,
                ResultatAdmission.promotion == promotion,
                ResultatAdmission.publie == True
            ).first()
            
            # Si prénom fourni, filtrer aussi par prénom
            if prenom and resultat:
                if resultat.prenom.lower() != prenom.lower():
                    resultat = None
    
    # Récupérer les promotions disponibles
    promotions = db.session.query(ResultatAdmission.promotion).filter_by(publie=True).distinct().all()
    promotions = [p[0] for p in promotions]
    
    return render_template('admission/consulter.html', resultat=resultat, promotions=promotions)

# Routes admin pour gérer les résultats d'admission
@resultats_admission_bp.route('/admin/liste')
def admin_liste():
    """Liste des résultats d'admission (admin)"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    promotion = request.args.get('promotion')
    classe = request.args.get('classe')
    
    query = ResultatAdmission.query
    
    if promotion:
        query = query.filter_by(promotion=promotion)
    if classe:
        query = query.filter_by(classe=classe)
    
    resultats = query.order_by(ResultatAdmission.promotion.desc(), ResultatAdmission.classe, ResultatAdmission.nom).all()
    
    # Récupérer les promotions et classes pour les filtres
    promotions = db.session.query(ResultatAdmission.promotion).distinct().all()
    promotions = [p[0] for p in promotions]
    
    classes = db.session.query(ResultatAdmission.classe).distinct().all()
    classes = [c[0] for c in classes]
    
    return render_template('admin/resultats_admission/liste.html', 
                         resultats=resultats, 
                         promotions=promotions,
                         classes=classes,
                         promotion_active=promotion,
                         classe_active=classe)

@resultats_admission_bp.route('/admin/nouveau', methods=['GET', 'POST'])
def admin_nouveau():
    """Créer un nouveau résultat d'admission"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        classe = request.form.get('classe')
        promotion = request.form.get('promotion')
        statut = request.form.get('statut', 'admis')
        publie = 'publie' in request.form
        
        resultat = ResultatAdmission(
            nom=nom,
            prenom=prenom,
            classe=classe,
            promotion=promotion,
            statut=statut,
            publie=publie
        )
        
        db.session.add(resultat)
        db.session.commit()
        
        flash('Résultat d\'admission créé avec succès!', 'success')
        return redirect(url_for('resultats_admission.admin_liste'))
    
    return render_template('admin/resultats_admission/nouveau.html')

@resultats_admission_bp.route('/admin/modifier/<int:resultat_id>', methods=['GET', 'POST'])
def admin_modifier(resultat_id):
    """Modifier un résultat d'admission"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    resultat = ResultatAdmission.query.get_or_404(resultat_id)
    
    if request.method == 'POST':
        resultat.nom = request.form.get('nom')
        resultat.prenom = request.form.get('prenom')
        resultat.classe = request.form.get('classe')
        resultat.promotion = request.form.get('promotion')
        resultat.statut = request.form.get('statut', 'admis')
        resultat.publie = 'publie' in request.form
        
        db.session.commit()
        
        flash('Résultat d\'admission modifié avec succès!', 'success')
        return redirect(url_for('resultats_admission.admin_liste'))
    
    return render_template('admin/resultats_admission/modifier.html', resultat=resultat)

@resultats_admission_bp.route('/admin/supprimer/<int:resultat_id>', methods=['POST'])
def admin_supprimer(resultat_id):
    """Supprimer un résultat d'admission"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    resultat = ResultatAdmission.query.get_or_404(resultat_id)
    db.session.delete(resultat)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Résultat supprimé avec succès'})

@resultats_admission_bp.route('/admin/importer', methods=['GET', 'POST'])
def admin_importer():
    """Importer plusieurs résultats d'admission en masse"""
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'directeur']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        classe = request.form.get('classe')
        promotion = request.form.get('promotion')
        statut = request.form.get('statut', 'admis')
        publie = 'publie' in request.form
        
        # Récupérer la liste des élèves (un par ligne: Nom Prénom)
        eleves_text = request.form.get('eleves', '')
        lignes = [l.strip() for l in eleves_text.split('\n') if l.strip()]
        
        count = 0
        for ligne in lignes:
            parts = ligne.split(maxsplit=1)
            if len(parts) >= 1:
                nom = parts[0]
                prenom = parts[1] if len(parts) > 1 else ''
                
                resultat = ResultatAdmission(
                    nom=nom,
                    prenom=prenom,
                    classe=classe,
                    promotion=promotion,
                    statut=statut,
                    publie=publie
                )
                db.session.add(resultat)
                count += 1
        
        db.session.commit()
        flash(f'{count} résultat(s) d\'admission importé(s) avec succès!', 'success')
        return redirect(url_for('resultats_admission.admin_liste'))
    
    return render_template('admin/resultats_admission/importer.html')
