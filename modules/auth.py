from flask import Blueprint, render_template, redirect, url_for, flash, request, session
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

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        role = 'parent'  # Default role
        
        if password != confirm:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        
        if existing_user:
            flash('Ce nom d\'utilisateur ou cet email est déjà utilisé.', 'danger')
            return render_template('auth/register.html')
        
        # Generate password hash
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            nom=nom,
            prenom=prenom,
            role=role
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
            
    return render_template('auth/register.html')