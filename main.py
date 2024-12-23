from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room
from forms import RegistrationForm, LoginForm, ProfileForm
from firebase_admin import credentials, firestore
from matching import calculate_similarity
from gmail_smtp import send_sign_up_email
from dotenv import load_dotenv
from datetime import datetime
from models import User
from PIL import Image
import firebase_admin
import os

app = Flask(__name__)
socketio = SocketIO(app)
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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
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
            send_sign_up_email(user.email)
            # flash('Account created successfully! Please log in.', 'success')
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
                # flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    current_profile_ref = db.collection('profiles').document(current_user.id)
    current_profile = current_profile_ref.get().to_dict() if current_profile_ref.get().exists else {}

    # Fetch all profiles
    profiles_ref = db.collection('profiles').stream()
    profiles = []
    for profile in profiles_ref:
        if profile.id == current_user.id:
            continue
        profile_data = profile.to_dict()
        user_ref = db.collection('users').document(profile.id).get()
        if user_ref.exists:
            user_data = user_ref.to_dict()
            profile_data['username'] = user_data.get('username')
            profile_data['email'] = user_data.get('email')
        profiles.append(profile_data)

    # Suggest profiles based on similarity score
    suggested_users = []
    for profile in profiles:
        similarity_score = calculate_similarity(current_profile, profile)
        profile['similarity_score'] = similarity_score
        suggested_users.append(profile)

    # Sort profiles by similarity score in descending order
    suggested_users = sorted(suggested_users, key=lambda x: x['similarity_score'], reverse=True)

    return render_template('dashboard.html', name=current_user.username, suggested_users=suggested_users)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    name = request.args.get('name')
    gender = request.args.get('gender')
    location = request.args.get('location')
    interests = request.args.get('interests')

    # Fetch all profiles
    profiles_ref = db.collection('profiles').stream()
    profiles = []
    for profile in profiles_ref:
        profile_data = profile.to_dict()
        user_ref = db.collection('users').document(profile.id).get()
        if user_ref.exists:
            user_data = user_ref.to_dict()
            profile_data['username'] = user_data.get('username')
            profile_data['email'] = user_data.get('email')
        profiles.append(profile_data)

    # Filter profiles based on search criteria
    search_results = []
    for profile in profiles:
        if name and name.lower() not in profile.get('name', '').lower():
            continue
        if gender and gender.lower() != profile.get('gender', '').lower():
            continue
        if location and location.lower() not in profile.get('location', '').lower():
            continue
        if interests:
            profile_interests = profile.get('interests', '').lower().split(',')
            search_interests = interests.lower().split(',')
            if not any(interest.strip() in profile_interests for interest in search_interests):
                continue
        search_results.append(profile)

    return render_template('search.html', search_results=search_results)

@app.route('/chat')
@login_required
def chat():
    # Fetch users with whom the current user has previous chats
    chats_ref = db.collection('chats').where('participants', 'array_contains', current_user.id).stream()
    chat_users = set()
    for chat in chats_ref:
        chat_data = chat.to_dict()
        for participant in chat_data['participants']:
            if participant != current_user.id:
                user_ref = db.collection('users').document(participant).get()
                if user_ref.exists:
                    chat_users.add(user_ref.to_dict())
    return render_template('chat.html', chat_users=chat_users)

@app.route('/chat/<username>')
@login_required
def chat_with_user(username):
    user_ref = db.collection('users').where('username', '==', username).get()
    if len(user_ref) == 0:
        return render_template('404.html'), 404
    other_user_data = user_ref[0].to_dict()
    other_user_id = user_ref[0].id
    chat_id = '_'.join(sorted([current_user.username, username]))
    
    try:
        messages_ref = db.collection('chats').document(chat_id).collection('messages').order_by('timestamp').stream()
        messages = [message.to_dict() for message in messages_ref]
    except Exception as e:
        app.logger.error(f"Error fetching messages: {e}")
        messages = []
    return render_template('chat.html', receiver=other_user_data, messages=messages)

# @app.route('/chat/<username>')
# @login_required
# def chat_with_user(username):
#     user_ref = db.collection('users').where('username', '==', username).get()
#     if not user_ref:
#         return render_template('404.html'), 404
#     other_user_data = user_ref[0].to_dict()
#     other_user_id = user_ref[0].id
#     chat_id = '_'.join(sorted([current_user.username, username]))
#     messages_ref = db.collection('chats').document(chat_id).collection('messages').order_by('timestamp').stream()
#     messages = [message.to_dict() for message in messages_ref]
#     return render_template('chat.html', receiver=other_user_data, messages=messages)

@app.route('/get_old_messages/<username>')
@login_required
def get_old_messages(username):
    user_ref = db.collection('users').where('username', '==', username).get()
    if not user_ref:
        return jsonify({'error': 'User not found'}), 404
    other_user_id = user_ref[0].id
    chat_id = '_'.join(sorted([current_user.username, username]))
    messages_ref = db.collection('chats').document(chat_id).collection('messages').order_by('timestamp').stream()
    messages = [message.to_dict() for message in messages_ref]
    return jsonify(messages)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'msg': f"{username} has joined the room."}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', {'msg': f"{username} has left the room."}, room=room)

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info(f"Received message data: {data}")
    chat_id = data['room']
    message_data = {
        'sender_id': current_user.id,
        'receiver_id': data['receiver_id'],
        'message_text': data['message'],
        'timestamp': datetime.utcnow().isoformat()
    }
    app.logger.info(f"Storing message data: {message_data}")
    db.collection('chats').document(chat_id).collection('messages').add(message_data)
    emit('receive_message', message_data, room=chat_id)

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
            output_size = (300, 300)
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
    socketio.run(app, debug=True)