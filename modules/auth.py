from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')
bcrypt = Bcrypt()

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = 'remember-me' in request.form
        
        # Find user by username
        user = User.query.filter_by(username=username, actif=True).first()
        
        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Log in the user with Flask-Login, respecting remember me option
            login_user(user, remember=remember_me)
            
            # Store user info in session for easy access
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = f"{user.prenom} {user.nom}"
            
            flash('Connexion réussie!', 'success')
            
            # Redirect to the page the user was trying to access, or home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('accueil'))
        else:
            flash('Identifiants invalides. Veuillez réessayer.', 'danger')
            
    return render_template('auth/login.html')

@auth_blueprint.route('/logout')
def logout():
    logout_user()  # Use Flask-Login's logout function
    session.clear()  # Clear any additional session data
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('accueil'))

# @auth_blueprint.route('/register', methods=['GET', 'POST'])
# def register():
#     """Registration disabled as per requirements - authentication only"""
#     # This route is disabled to comply with requirements
#     # "Authentication uniquement, sans possibilité d'inscription ou de création de compte"
#     abort(404)

@auth_blueprint.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('accueil'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# --- Admin Required Decorator ---
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', None) != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function