from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import date, datetime
from models import Annonce, Document, db
from flask_login import login_required
import os
import uuid
from modules.whatsapp_notifications import send_announcement_to_whatsapp

communication_blueprint = Blueprint('communication', __name__, url_prefix='/communication')

@communication_blueprint.route('/')
def index():
    print("DEBUG: Fetching announcements for communication index page")
    
    # Get public announcements
    try:
        annonces = Annonce.query.filter(
            Annonce.public == 1,
            (Annonce.date_expiration.is_(None)) | (Annonce.date_expiration >= date.today())
        ).order_by(Annonce.important.desc(), Annonce.date_creation.desc()).all()
        
        print(f"DEBUG: Found {len(annonces)} announcements for index page")
        for i, a in enumerate(annonces):
            print(f"DEBUG: Announcement {i+1}: id={a.id}, title={a.titre}, public={a.public}, important={a.important}")
    except Exception as e:
        print(f"ERROR in index route: {str(e)}")
        annonces = []
    
    return render_template('communication/index.html', annonces=annonces)

@communication_blueprint.route('/annonces')
def annonces():
    print("DEBUG: Fetching announcements for /annonces page")
    
    # Count total announcements in the database
    total_annonces = Annonce.query.count()
    print(f"DEBUG: Total announcements in database: {total_annonces}")
    
    # Dump all announcements for debugging
    all_announcements = Annonce.query.all()
    print(f"DEBUG: All announcements in database:")
    for a in all_announcements:
        print(f"DEBUG: ID={a.id}, Title={a.titre}, Public={a.public} (raw: {int(a.public)}), Important={a.important if hasattr(a, 'important') else 'N/A'}, Date_Expiration={a.date_expiration}, Created={a.date_creation}")
    
    # Check today's date for comparison
    today = date.today()
    print(f"DEBUG: Today's date for comparison: {today}")
    
    # Get all public announcements
    try:
        annonces = Annonce.query.filter(
            Annonce.public == 1,
            (Annonce.date_expiration.is_(None)) | (Annonce.date_expiration >= date.today())
        ).order_by(Annonce.important.desc(), Annonce.date_creation.desc()).all()
        
        print(f"DEBUG: Found {len(annonces)} announcements for /annonces page")
        for i, a in enumerate(annonces):
            print(f"DEBUG: Announcement {i+1}: id={a.id}, title={a.titre}, public={a.public} (raw: {int(a.public)}), important={a.important} (raw: {int(a.important)}), date_expiration={a.date_expiration}")
        
        if len(annonces) == 0:
            # Try a simpler query just to see if any public announcements exist
            simple_query = Annonce.query.filter(Annonce.public == 1).all()
            print(f"DEBUG: Simple query (just public=1) found {len(simple_query)} announcements")
            if simple_query:
                for i, a in enumerate(simple_query):
                    print(f"DEBUG: Simple query result {i+1}: id={a.id}, title={a.titre}, date_expiration={a.date_expiration}")
                print("DEBUG: If announcements appear here but not in the main query, the date_expiration filter is excluding them")
    except Exception as e:
        print(f"ERROR in annonces route: {str(e)}")
        annonces = []
    
    return render_template('communication/annonces.html', annonces=annonces)

@communication_blueprint.route('/annonces/<int:annonce_id>')
def details_annonce(annonce_id):
    annonce = Annonce.query.get(annonce_id)
    if not annonce:
        flash('Annonce non trouvée.', 'danger')
        return redirect(url_for('communication.annonces'))
    # Check if announcement is public or user is logged in
    if not annonce.public and not session.get('user_id'):
        flash('Vous n\'êtes pas autorisé à voir cette annonce.', 'danger')
        return redirect(url_for('communication.annonces'))
    return render_template('communication/details_annonce.html', annonce=annonce)

@communication_blueprint.route('/annonces/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_annonce():
    if request.method == 'POST':
        titre = request.form['titre']
        contenu = request.form['contenu']
        date_expiration_str = request.form.get('date_expiration')
        date_expiration = datetime.strptime(date_expiration_str, '%Y-%m-%d').date() if date_expiration_str else None
        public = int(request.form.get('public', 0))
        important = int(request.form.get('important', 0))
        annonce = Annonce(
            titre=titre,
            contenu=contenu,
            date_creation=date.today(),
            date_expiration=date_expiration if date_expiration else None,
            public=public,
            important=important
        )
        db.session.add(annonce)
        db.session.commit()
        
        # Send WhatsApp notification for public announcements
        if public:
            try:
                result = send_announcement_to_whatsapp(annonce)
                if result.get('error'):
                    flash(f'Annonce ajoutée, mais erreur lors de l\'envoi des notifications WhatsApp: {result["error"]}', 'warning')
                else:
                    flash('Annonce ajoutée avec succès et notifications WhatsApp envoyées!', 'success')
            except Exception as e:
                flash(f'Annonce ajoutée, mais erreur lors de l\'envoi des notifications WhatsApp: {str(e)}', 'warning')
        else:
            flash('Annonce ajoutée avec succès!', 'success')
            
        return redirect(url_for('communication.annonces'))
    return render_template('communication/ajouter_annonce.html')

@communication_blueprint.route('/annonces/<int:annonce_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_annonce(annonce_id):
    annonce = Annonce.query.get(annonce_id)
    if not annonce:
        flash('Annonce non trouvée.', 'danger')
        return redirect(url_for('communication.annonces'))
    if request.method == 'POST':
        annonce.titre = request.form['titre']
        annonce.contenu = request.form['contenu']
        annonce.date_expiration = request.form.get('date_expiration') or None
        was_public = annonce.public
        annonce.public = int(request.form.get('public', 0))
        annonce.important = int(request.form.get('important', 0))
        db.session.commit()
        
        # Send WhatsApp notification if the announcement wasn't public before but is now
        if not was_public and annonce.public:
            try:
                result = send_announcement_to_whatsapp(annonce)
                if result.get('error'):
                    flash(f'Annonce modifiée, mais erreur lors de l\'envoi des notifications WhatsApp: {result["error"]}', 'warning')
                else:
                    flash('Annonce modifiée avec succès et notifications WhatsApp envoyées!', 'success')
            except Exception as e:
                flash(f'Annonce modifiée, mais erreur lors de l\'envoi des notifications WhatsApp: {str(e)}', 'warning')
        else:
            flash('Annonce modifiée avec succès!', 'success')
            
        return redirect(url_for('communication.annonces'))
    return render_template('communication/modifier_annonce.html', annonce=annonce)

@communication_blueprint.route('/annonces/<int:annonce_id>/supprimer', methods=['POST'])
@login_required
def supprimer_annonce(annonce_id):
    annonce = Annonce.query.get(annonce_id)
    if not annonce:
        flash('Annonce non trouvée.', 'danger')
        return redirect(url_for('communication.annonces'))
    db.session.delete(annonce)
    db.session.commit()
    flash('Annonce supprimée avec succès!', 'success')
    return redirect(url_for('communication.annonces'))

@communication_blueprint.route('/documents')
def documents():
    documents_publics = Document.query.filter_by(public=1).order_by(Document.date_upload.desc()).all()
    # If user is logged in, get private documents too
    if session.get('user_id'):
        documents_prives = Document.query.filter_by(public=0).order_by(Document.date_upload.desc()).all()
    else:
        documents_prives = []
    return render_template('communication/documents.html', documents_publics=documents_publics, documents_prives=documents_prives)

@communication_blueprint.route('/documents/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_document():
    # Check if user has admin or director privileges
    if not session.get('user_role') in ['admin', 'directeur', 'professeur']:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('communication.documents'))
    
    if request.method == 'POST':
        titre = request.form.get('titre')
        description = request.form.get('description')
        type_document = request.form.get('type')
        public = 1 if request.form.get('public') else 0
        
        # Handle file upload
        if 'fichier' not in request.files:
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(request.url)
        
        fichier = request.files['fichier']
        if fichier.filename == '':
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(request.url)
        
        # Save file
        from werkzeug.utils import secure_filename
        import os
        from app import app
        
        filename = secure_filename(fichier.filename)
        # Generate unique filename
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        fichier.save(os.path.join(upload_dir, unique_filename))
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO documents (titre, description, fichier, type, date_upload, uploader_id, public)
                    VALUES (%s, %s, %s, %s, NOW(), %s, %s)
                """, (titre, description, unique_filename, type_document, session.get('user_id'), public))
                conn.commit()
                
                flash('Document ajouté avec succès!', 'success')
                return redirect(url_for('communication.documents'))
        finally:
            conn.close()
    
    return render_template('communication/ajouter_document.html')

@communication_blueprint.route('/documents/<int:document_id>/supprimer', methods=['POST'])
@login_required
def supprimer_document(document_id):
    # Check if user has admin or director privileges
    if not session.get('user_role') in ['admin', 'directeur', 'professeur']:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('communication.documents'))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
            document = cursor.fetchone()
            
            if not document:
                flash('Document non trouvé.', 'danger')
                return redirect(url_for('communication.documents'))
            
            # Check if user is the uploader or has admin/director privileges
            if document['uploader_id'] != session.get('user_id') and session.get('user_role') not in ['admin', 'directeur']:
                flash('Vous n\'êtes pas autorisé à supprimer ce document.', 'danger')
                return redirect(url_for('communication.documents'))
            
            # Delete file
            import os
            from app import app
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', document['fichier'])
            if os.path.exists(file_path):
                os.remove(file_path)
            
            cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
            conn.commit()
            
            flash('Document supprimé avec succès!', 'success')
            return redirect(url_for('communication.documents'))
    finally:
        conn.close()

@communication_blueprint.route('/api/annonces/recentes')
def api_annonces_recentes():
    # Get recent announcements for the ticker
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT titre, id
                FROM annonces
                WHERE public = 1 
                AND (date_expiration IS NULL OR date_expiration >= CURDATE())
                ORDER BY important DESC, date_creation DESC
                LIMIT 5
            """)
            annonces = cursor.fetchall()
    finally:
        conn.close()
    
    return jsonify(annonces)
