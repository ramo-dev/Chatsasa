from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

socketio = SocketIO(app)
db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Maintain a list of online users
online_users = set()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    read = db.Column(db.Boolean, default=False)

class DirectMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    read = db.Column(db.Boolean, default=False)

# Create Tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['username'] = user.username
                return redirect(url_for('welcome'))  # Redirect to welcome.html after successful login
            return render_template('index.html', error='Invalid credentials')
        return render_template('index.html', error='Missing username or password')
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('index.html', error='Username already exists')

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            # Redirect to login page after successful signup
            return redirect(url_for('login'))
        return render_template('index.html', error='Missing username or password')
    return render_template('signup.html')


@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('welcome.html')  # Render the welcome.html page for logged-in users



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))

    # Pass the online users to the template
    return render_template('chat.html', online_users=online_users)

session_users = {}

@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        if session['username'] not in session_users:
            session_users[session['username']] = set()
        session_users[session['username']].add(session['username'])
        
        # Broadcast online users to everyone in the session except the current user
        current_user_username = session['username']
        users_in_session = set(session_users.keys()) - {session['username']}
        online_users_in_session = set()
        for user in users_in_session:
            online_users_in_session.update(session_users[user])
        
        emit('online_users', list(online_users_in_session), room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    if 'username' in session and session['username'] in session_users:
        if session['username'] in session_users:
            session_users[session['username']].remove(session['username'])
        
        # Broadcast online users to everyone in the session except the current user
        current_user_username = session['username']
        users_in_session = set(session_users.keys()) - {session['username']}
        online_users_in_session = set()
        for user in users_in_session:
            online_users_in_session.update(session_users[user])
        
        emit('online_users', list(online_users_in_session), room=request.sid)
        emit('online_users', list(session_users[current_user_username]), room=request.sid)

@socketio.on('message')
def handle_message(data):
    sender = data.get('sender')
    content = data.get('content')

    if sender and content:
        new_message = Message(sender=sender, content=content)
        db.session.add(new_message)
        db.session.commit()
        emit('message', data, broadcast=True)

# Add logic to handle direct messages in the same way as messages
@socketio.on('direct-message')
def handle_direct_message(data):
    sender = data.get('sender')
    receiver = data.get('receiver')
    content = data.get('content')

    if sender and receiver and content:
        new_direct_message = DirectMessage(sender=sender, receiver=receiver, content=content)
        db.session.add(new_direct_message)
        db.session.commit()
        
        # Emit the direct message to the specific receiver
        emit('direct-message', data, room=receiver)

# Socket IO 'direct-message-read' event handler to update read status for direct messages
@socketio.on('direct-message-read')
def handle_direct_message_read(direct_message_id):
    direct_message = DirectMessage.query.get(direct_message_id)
    if direct_message:
        direct_message.read = True
        db.session.commit()


if __name__ == '__main__':
    socketio.run(app, debug=True,port=5005,allow_unsafe_werkzeug=True)
