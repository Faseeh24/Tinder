from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ProfileForm
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from datetime import datetime
from models import User
from PIL import Image
import firebase_admin
import os

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('flask_secret_key')
app.config['UPLOAD_FOLDER'] = "static/profile_photos"

cred = credentials.Certificate(os.getenv('path_to_firestore_key'))
firebase_admin.initialize_app(cred)
db = firestore.client()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user_ref = db.collection('users').document(user_id).get()
    if user_ref.exists:
        user_data = user_ref.to_dict()
        return User(id=user_id, **user_data)
    return None

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user_ref = db.collection('users').where('email', '==', form.email.data).get()
        if user_ref:
            flash('Username or email already exists.', 'danger')
        else:
            user_id = db.collection('users').document().id
            user = User(id=user_id, username=form.username.data, email=form.email.data, password_hash=generate_password_hash(form.password.data))
            db.collection('users').document(user_id).set({
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash
            })
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user_ref = db.collection('users').where('email', '==', form.email.data).get()
        if user_ref:
            user_data = user_ref[0].to_dict()
            user = User(id=user_ref[0].id, **user_data)
            if user.check_password(form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_ref = db.collection('profiles').document(current_user.id)
    profile = profile_ref.get().to_dict() if profile_ref.get().exists else {}
    if profile and 'date_of_birth' in profile and isinstance(profile['date_of_birth'], str):
        profile['date_of_birth'] = datetime.fromisoformat(profile['date_of_birth'])
    form = ProfileForm(data=profile)
    if form.validate_on_submit():
        profile_data = {
            'name': form.name.data,
            'date_of_birth': form.date_of_birth.data.isoformat() if form.date_of_birth.data else None,
            'gender': form.gender.data,
            'match_preference': form.match_preference.data,
            'profession': form.profession.data,
            'education_level': form.education_level.data,
            'location': form.location.data,
            'about_me': form.about_me.data,
            'interests': form.selected_interests.data  # Save selected interests
        }
        profile_ref.set(profile_data)
        profile_photo = form.profile_photo.data
        if profile_photo:
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            output_size = (200, 200)
            img = Image.open(profile_photo)
            img.thumbnail(output_size)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], (current_user.email + ".png")))

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)

@app.route('/user/<username>')
def user_profile(username):
    user_ref = db.collection('users').where('username', '==', username).get()
    if user_ref:
        user_data = user_ref[0].to_dict()
        profile_ref = db.collection('profiles').document(user_ref[0].id).get()
        profile = profile_ref.to_dict() if profile_ref.exists else {}
        if profile and 'interests' in profile:
            profile['interests'] = profile['interests'].split(',')  # Convert interests back to a list
        return render_template('user_profile.html', profile=profile, user=user_data)
    return render_template('404.html'), 404

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)