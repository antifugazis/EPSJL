from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required
from models import Paiement
from models import db
from datetime import datetime, date


finances_blueprint = Blueprint('finances', __name__, url_prefix='/finances')

# Helper function to check if user has admin privileges
def is_admin_or_directeur():
    return session.get('user_role') in ['admin', 'directeur']

@finances_blueprint.route('/')
@login_required
def index():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
        
    # Get summary statistics using SQLAlchemy ORM
    from models import Paiement, Frais, Eleve, User
    from sqlalchemy import extract, func
    from datetime import datetime
    current_year = datetime.now().year

    # Total revenue for current year
    total_revenus = db.session.query(func.sum(Paiement.montant)).filter(extract('year', Paiement.date) == current_year).scalar() or 0

    # Total revenue by month for current year
    revenus_par_mois = (
        db.session.query(extract('month', Paiement.date).label('mois'), func.sum(Paiement.montant).label('total'))
        .filter(extract('year', Paiement.date) == current_year)
        .group_by(extract('month', Paiement.date))
        .order_by(extract('month', Paiement.date))
        .all()
    )

    # Total revenue by payment type
    revenus_par_type = (
        db.session.query(Frais.type, func.sum(Paiement.montant).label('total'))
        .join(Frais, Paiement.frais_id == Frais.id)
        .filter(extract('year', Paiement.date) == current_year)
        .group_by(Frais.type)
        .all()
    )

    # Recent payments
    paiements_recents = (
        db.session.query(Paiement, Eleve, Frais, User)
        .join(Eleve, Paiement.eleve_id == Eleve.id)
        .join(Frais, Paiement.frais_id == Frais.id)
        .outerjoin(User, Paiement.recu_par == User.id)
        .order_by(Paiement.date.desc())
        .limit(10)
        .all()
    )

    # Transform paiements_recents for template
    paiements_list = []
    for paiement, eleve, frais, user in paiements_recents:
        paiements_list.append({
            'id': paiement.id,
            'date': paiement.date,
            'montant': paiement.montant,
            'eleve_nom': eleve.nom,
            'eleve_prenom': eleve.prenom,
            'matricule': eleve.matricule,
            'frais_type': frais.type if frais else None,
            'recu_par_nom': user.nom if user else None,
            'recu_par_prenom': user.prenom if user else None,
            'eleve_id': eleve.id
        })

    return render_template('finances/index.html', 
                          total_revenus=total_revenus,
                          revenus_par_mois=revenus_par_mois,
                          revenus_par_type=revenus_par_type,
                          paiements_recents=paiements_list)

@finances_blueprint.route('/frais')
@login_required
def frais():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
        
    annee_scolaire = request.args.get('annee_scolaire', str(datetime.now().year))
    
    # Get all fees using SQLAlchemy ORM
    from models import Frais, Classe
    from sqlalchemy import distinct
    
    # Get all fees for the selected school year
    frais_query = (db.session.query(Frais, Classe.nom.label('classe_nom'))
                  .outerjoin(Classe, Frais.classe_id == Classe.id)
                  .filter(Frais.annee_scolaire == annee_scolaire)
                  .order_by(Frais.type, Classe.nom))
    frais_list = frais_query.all()
    
    # Format results for template
    frais = []
    for f, classe_nom in frais_list:
        frais_item = {
            'id': f.id,
            'type': f.type,
            'description': f.description,
            'montant': f.montant,
            'annee_scolaire': f.annee_scolaire,
            'classe_id': f.classe_id,
            'classe_nom': classe_nom,
            'date_echeance': f.date_echeance
        }
        frais.append(frais_item)
    
    # Get available school years
    annees_query = db.session.query(distinct(Frais.annee_scolaire)).order_by(Frais.annee_scolaire.desc())
    annees = [{'annee_scolaire': a[0]} for a in annees_query.all()]
    
    return render_template('finances/frais.html', 
                          frais=frais,
                          annees=annees,
                          annee_scolaire=annee_scolaire)

@finances_blueprint.route('/frais/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_frais():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
        
    if request.method == 'POST':
        type_frais = request.form.get('type')
        description = request.form.get('description')
        montant = request.form.get('montant')
        annee_scolaire = request.form.get('annee_scolaire')
        classe_id = request.form.get('classe_id') or None
        date_echeance_str = request.form.get('date_echeance') or None
        date_echeance = None
        if date_echeance_str:
            try:
                date_echeance = datetime.strptime(date_echeance_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Format de date invalide pour la date d\'échéance.', 'danger')
                return redirect(url_for('finances.ajouter_frais'))
        
        if not all([type_frais, montant, annee_scolaire]):
            flash('Veuillez remplir tous les champs obligatoires.', 'warning')
            return redirect(url_for('finances.ajouter_frais'))
        
        # Create new fee using SQLAlchemy ORM
        from models import Frais
        new_frais = Frais(
            type=type_frais,
            description=description,
            montant=float(montant),
            annee_scolaire=annee_scolaire,
            classe_id=classe_id,
            date_echeance=date_echeance
        )
        
        db.session.add(new_frais)
        db.session.commit()
        
        flash('Frais ajouté avec succès!', 'success')
        return redirect(url_for('finances.frais'))
    
    # Get classes using SQLAlchemy ORM
    from models import Classe
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    
    # Format classes for template
    classes_list = [{
        'id': c.id,
        'nom': c.nom,
        'niveau': c.niveau
    } for c in classes]
    
    return render_template('finances/ajouter_frais.html', 
                          classes=classes_list,
                          annee_courante=datetime.now().year)

@finances_blueprint.route('/paiements')
@login_required
def paiements():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
        
    eleve_id = request.args.get('eleve_id')
    classe_id = request.args.get('classe_id')
    type_frais = request.args.get('type_frais')
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    # Use SQLAlchemy ORM for queries
    from models import Paiement, Eleve, Frais, User, Classe
    from sqlalchemy import distinct
    
    # Build base query
    query = (db.session.query(Paiement, Eleve, Frais, User)
             .join(Eleve, Paiement.eleve_id == Eleve.id)
             .join(Frais, Paiement.frais_id == Frais.id)
             .join(User, Paiement.recu_par == User.id))
    
    # Apply filters
    if eleve_id:
        query = query.filter(Paiement.eleve_id == eleve_id)
    
    if classe_id:
        query = query.filter(Eleve.classe_id == classe_id)
    
    if type_frais:
        query = query.filter(Frais.type == type_frais)
    
    if date_debut:
        query = query.filter(Paiement.date >= date_debut)
    
    if date_fin:
        query = query.filter(Paiement.date <= date_fin)
    
    # Order by date
    query = query.order_by(Paiement.date.desc())
    
    # Execute query
    paiements_data = query.all()
    
    # Format results for template
    paiements = []
    for p, e, f, u in paiements_data:
        paiements.append({
            'id': p.id,
            'date': p.date,
            'montant': p.montant,
            'methode': p.methode,
            'reference': p.reference,
            'commentaire': p.commentaire,
            'eleve_id': e.id,
            'matricule': e.matricule,
            'eleve_nom': e.nom,
            'eleve_prenom': e.prenom,
            'frais_type': f.type,
            'recu_par_nom': u.nom,
            'recu_par_prenom': u.prenom
        })
    
    # Get classes for filter
    classes = Classe.query.order_by(Classe.niveau, Classe.nom).all()
    classes_list = [{'id': c.id, 'nom': c.nom} for c in classes]
    
    # Get fee types for filter
    types_frais_query = db.session.query(distinct(Frais.type)).order_by(Frais.type)
    types_frais = [{'type': t[0]} for t in types_frais_query.all()]
    
    return render_template('finances/paiements.html', 
                          paiements=paiements,
                          classes=classes_list,
                          types_frais=types_frais,
                          eleve_id=eleve_id,
                          classe_id=classe_id,
                          type_frais=type_frais,
                          date_debut=date_debut,
                          date_fin=date_fin)

@finances_blueprint.route('/paiements/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_paiement():
    if not is_admin_or_directeur():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
        
    if request.method == 'POST':
        eleve_id = request.form.get('eleve_id')
        frais_id = request.form.get('frais_id')
        montant = request.form.get('montant')
        methode = request.form.get('methode')
        reference = request.form.get('reference')
        date_paiement = request.form.get('date')
        commentaire = request.form.get('commentaire')
        
        if not all([eleve_id, frais_id, montant, methode, date_paiement]):
            flash('Veuillez remplir tous les champs obligatoires.', 'warning')
            return redirect(url_for('finances.ajouter_paiement'))
        
        # Create new payment using SQLAlchemy ORM
        from models import Paiement
        new_paiement = Paiement(
            eleve_id=eleve_id,
            frais_id=frais_id,
            montant=float(montant),
            methode=methode,
            reference=reference,
            date=date_paiement,
            recu_par=session['user_id'],
            commentaire=commentaire
        )
        
        db.session.add(new_paiement)
        db.session.commit()
        
        flash('Paiement enregistré avec succès!', 'success')
        return redirect(url_for('finances.paiements', eleve_id=eleve_id))
    
    # GET request - show form
    eleve_id = request.args.get('eleve_id')
    eleve_classe_id = None
    
    # Get all students using SQLAlchemy ORM
    from models import Eleve, Classe, Frais
    
    # Get all active students with their class information
    eleves_query = db.session.query(Eleve, Classe.nom.label('classe_nom'))\
                    .outerjoin(Classe, Eleve.classe_id == Classe.id)\
                    .filter(Eleve.actif == 1)\
                    .order_by(Eleve.nom, Eleve.prenom)
    eleves_data = eleves_query.all()
    
    # Format students for template
    eleves = []
    for e, classe_nom in eleves_data:
        eleves.append({
            'id': e.id,
            'matricule': e.matricule,
            'nom': e.nom,
            'prenom': e.prenom,
            'classe_nom': classe_nom
        })
    
    # If eleve_id is provided, get their class
    if eleve_id:
        eleve = Eleve.query.get(eleve_id)
        if eleve:
            eleve_classe_id = eleve.classe_id
    
    # Get all fees for the current year
    current_year = str(datetime.now().year)
    frais = Frais.query.filter_by(annee_scolaire=current_year).order_by(Frais.type).all()
    frais_list = [{
        'id': f.id,
        'type': f.type,
        'description': f.description,
        'montant': f.montant,
        'classe_id': f.classe_id
    } for f in frais]
    
    return render_template('finances/ajouter_paiement.html', 
                          eleves=eleves,
                          frais=frais_list,
                          eleve_id=eleve_id,
                          eleve_classe_id=eleve_classe_id,
                          date_paiement=date.today().strftime('%Y-%m-%d'))

@finances_blueprint.route('/get_frais_by_eleve', methods=['GET'])
@login_required
def get_frais_by_eleve():
    eleve_id = request.args.get('eleve_id')
    
    if not eleve_id:
        return jsonify([])
    
    # Get student's class using SQLAlchemy ORM
    from models import Eleve, Frais
    from sqlalchemy import or_
    from datetime import datetime
    
    # Get student's class ID
    eleve = Eleve.query.get(eleve_id)
    if not eleve:
        return jsonify([])
    
    classe_id = eleve.classe_id
    current_year = str(datetime.now().year)
    
    # Get fees for this class or general fees
    frais_query = Frais.query.filter(
        Frais.annee_scolaire == current_year,
        or_(Frais.classe_id == None, Frais.classe_id == classe_id)
    ).order_by(Frais.type)
    
    frais_list = frais_query.all()
    
    # Format results for JSON response
    frais = [{
        'id': f.id,
        'type': f.type,
        'description': f.description,
        'montant': f.montant,
        'annee_scolaire': f.annee_scolaire,
        'classe_id': f.classe_id,
        'date_echeance': f.date_echeance.isoformat() if f.date_echeance else None
    } for f in frais_list]
    
    return jsonify(frais)

@finances_blueprint.route('/situation/<int:eleve_id>')
@login_required
def situation(eleve_id):
    # Get student info using SQLAlchemy ORM
    from models import Eleve, Classe, Frais, Paiement
    from sqlalchemy import or_
    from datetime import datetime
    
    # Get student with class info
    eleve_query = db.session.query(Eleve, Classe.nom.label('classe_nom'))\
                   .outerjoin(Classe, Eleve.classe_id == Classe.id)\
                   .filter(Eleve.id == eleve_id)
    eleve_data = eleve_query.first()
    
    if not eleve_data:
        flash('Élève non trouvé.', 'danger')
        return redirect(url_for('finances.paiements'))
    
    eleve_obj, classe_nom = eleve_data
    
    # Format student data for template
    eleve = {
        'id': eleve_obj.id,
        'matricule': eleve_obj.matricule,
        'nom': eleve_obj.nom,
        'prenom': eleve_obj.prenom,
        'classe_id': eleve_obj.classe_id,
        'classe_nom': classe_nom
    }
    
    # Get all fees applicable to this student
    current_year = str(datetime.now().year)
    frais_query = Frais.query.filter(
        Frais.annee_scolaire == current_year,
        or_(Frais.classe_id == None, Frais.classe_id == eleve_obj.classe_id)
    ).order_by(Frais.type)
    
    frais_list = frais_query.all()
    
    # Format fees for template
    frais = [{
        'id': f.id,
        'type': f.type,
        'description': f.description,
        'montant': f.montant,
        'annee_scolaire': f.annee_scolaire,
        'classe_id': f.classe_id
    } for f in frais_list]
    
    # Get all payments made by this student
    paiements_query = db.session.query(Paiement, Frais.type.label('frais_type'), Frais.description.label('frais_description'))\
                      .join(Frais, Paiement.frais_id == Frais.id)\
                      .filter(Paiement.eleve_id == eleve_id)\
                      .order_by(Paiement.date.desc())
    
    paiements_data = paiements_query.all()
    
    # Format payments for template
    paiements = [{
        'id': p.id,
        'eleve_id': p.eleve_id,
        'frais_id': p.frais_id,
        'montant': p.montant,
        'date': p.date,
        'methode': p.methode,
        'reference': p.reference,
        'commentaire': p.commentaire,
        'frais_type': frais_type,
        'frais_description': frais_description
    } for p, frais_type, frais_description in paiements_data]
    
    # Calculate balance for each fee type
    soldes = {}
    for f in frais:
        soldes[f['id']] = {
            'montant_du': f['montant'],
            'montant_paye': 0,
            'solde': f['montant']
        }
    
    for p in paiements:
        if p['frais_id'] in soldes:
            soldes[p['frais_id']]['montant_paye'] += p['montant']
            soldes[p['frais_id']]['solde'] -= p['montant']
    
    # Calculate total balance
    total_du = sum(f['montant'] for f in frais)
    total_paye = sum(p['montant'] for p in paiements)
    solde_total = total_du - total_paye
    
    return render_template('finances/situation.html', 
                          eleve=eleve,
                          frais=frais,
                          paiements=paiements,
                          soldes=soldes,
                          total_du=total_du,
                          total_paye=total_paye,
                          solde_total=solde_total)
