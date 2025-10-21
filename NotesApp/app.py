from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Note
import datetime
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['SECRET_KEY'] = os.environ.get('NOTIONISH_SECRET', 'replace-with-a-secure-random-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Please provide username and password', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        u = User(username=username, password=pw_hash)
        db.session.add(u)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated_at.desc()).all()
    return render_template('dashboard.html', notes=notes)


@app.route('/note/new')
@login_required
def new_note_page():
    return render_template('editor.html', note=None)


@app.route('/note/<int:note_id>')
@login_required
def edit_note_page(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    return render_template('editor.html', note=note)


# API endpoints
@app.route('/api/note', methods=['POST'])
@login_required
def create_note():
    data = request.get_json(force=True)
    title = (data.get('title') or 'Untitled')[:255]
    content = data.get('content', '')
    note = Note(title=title, content=content, user_id=current_user.id)
    db.session.add(note)
    db.session.commit()
    return jsonify({'ok': True, 'id': note.id})


@app.route('/api/note/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    data = request.get_json(force=True)
    note.title = (data.get('title') or note.title)[:255]
    note.content = data.get('content', note.content)
    note.updated_at = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})


@app.route('/api/note/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return jsonify({'ok': True})


@app.route('/api/notes', methods=['GET'])
@login_required
def api_notes():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated_at.desc()).all()
    out = [{'id': n.id, 'title': n.title, 'updated_at': n.updated_at.isoformat()} for n in notes]
    return jsonify(out)


# Simple error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html') if os.path.exists('templates/404.html') else ("Not Found", 404)


if __name__ == '__main__':
    # For development only. In production use a proper WSGI server.
    app.run(debug=True)
