from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user
import os
from datetime import datetime
import json
from models import Cours

# Import SQLAlchemy models
from models import db, User, Eleve, Evenement, Annonce

# Import modules
from modules.auth import auth_blueprint
from modules.eleves import eleves_blueprint
from modules.cours import cours_blueprint
from modules.presence import presence_blueprint
from modules.notes import notes_blueprint
from modules.finances import finances_blueprint
from modules.rapports import rapports_blueprint
from modules.calendrier import calendrier_blueprint
from modules.communication import communication_blueprint

# Configuration
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(eleves_blueprint)
app.register_blueprint(cours_blueprint)
app.register_blueprint(presence_blueprint)
app.register_blueprint(notes_blueprint)
app.register_blueprint(finances_blueprint)
app.register_blueprint(rapports_blueprint)
app.register_blueprint(calendrier_blueprint)
app.register_blueprint(communication_blueprint)

# Home route
@app.route('/')
def accueil():
    # Get some stats for the homepage using SQLAlchemy
    
    # Get total number of students
    total_eleves = Eleve.query.filter_by(actif=True).count()
    
    # Get upcoming events
    from datetime import date
    today = date.today()
    evenements = Evenement.query.filter(Evenement.date >= today).order_by(Evenement.date).limit(5).all()
    
    # Get recent announcements
    annonces = Annonce.query.order_by(Annonce.date_creation.desc()).limit(3).all()
    
    return render_template('accueil.html', 
                          total_eleves=total_eleves,
                          evenements=evenements,
                          annonces=annonces)

# API endpoints
@app.route('/api/cours')
@login_required
def api_cours():
    classe_id = request.args.get('classe_id')
    print(f"DEBUG: Fetching courses for class_id: {classe_id}")
    if not classe_id:
        print("DEBUG: No class_id provided")
        return jsonify([])
    try:
        classe_id_int = int(classe_id)
    except (TypeError, ValueError):
        print("DEBUG: Invalid class_id provided")
        return jsonify([])
    
    from models import Enseignement, Cours, db
    
    # Query the database to get courses for the selected class
    try:
        # Join Enseignement and Cours tables to get courses for the selected class
        courses = db.session.query(Cours).join(
            Enseignement, Cours.id == Enseignement.cours_id
        ).filter(
            Enseignement.classe_id == classe_id_int
        ).order_by(Cours.nom).all()
        
        print(f"DEBUG: Found {len(courses)} courses for class {classe_id}")
        
        cours_list = [
            {
                'id': c.id,
                'code': c.code,
                'nom': c.nom,
                'coefficient': c.coefficient
            } for c in courses
        ]
        
        print(f"DEBUG: Sending response: {cours_list}")
        return jsonify(cours_list)
        
    except Exception as e:
        print(f"ERROR in api_cours: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('erreurs/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('erreurs/500.html'), 500

# Context processor for common data
@app.context_processor
def inject_data():
    current_year = datetime.now().year
    school_name = "École Presbytérale Saint Joseph de L'Asile"
    return dict(current_year=current_year, school_name=school_name)

# Create database tables if they don't exist
# Note: before_first_request is deprecated in newer Flask versions
# We'll use app.app_context() and create tables directly when the app starts

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True, port=5012)