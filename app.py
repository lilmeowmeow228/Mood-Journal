from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATA_FILE = 'data.json'
USERS_FILE = 'users.json'

def load_entries():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.context_processor
def inject_logged_in():
    return dict(logged_in=('user' in session), current_user=session.get('user'))

@app.route('/')
def index():
    all_entries = load_entries()
    username = session.get('user')
    if username:
        user_entries = [e for e in all_entries if e.get('user') == username]
    else:
        user_entries = []
    return render_template(
        'index.html',
        entries=user_entries[::-1],
        emotions=['happy', 'sad', 'angry', 'joyful', 'tired', 'hungry', 'stressful']
    )

@app.route('/save', methods=['POST'])
def save():
    if 'user' not in session:
        flash("Please log in to save your entries.")
        return redirect(url_for('login'))

    emotion = request.form.get('emotion')
    notes = request.form.get('notes')
    plans_texts = request.form.getlist('plans[]')

    entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user': session['user'],
        'emotion': emotion,
        'notes': notes,
        'plans': [{'text': text, 'done': False} for text in plans_texts if text.strip()]
    }

    entries = load_entries()
    entries.append(entry)
    save_entries(entries)
    flash("Entry saved successfully.")
    return redirect(url_for('index'))

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    username = session.get('user')
    entries = load_entries()
    user_entries = [e for e in entries if e.get('user') == username]

    if 0 <= entry_id < len(user_entries):
        real_entry = user_entries[-(entry_id + 1)]
        entries.remove(real_entry)
        save_entries(entries)

    return redirect(url_for('index'))

@app.route('/toggle_done/<int:entry_id>/<int:plan_index>', methods=['POST'])
def toggle_done(entry_id, plan_index):
    username = session.get('user')
    entries = load_entries()
    user_entries = [e for e in entries if e.get('user') == username]

    if 0 <= entry_id < len(user_entries):
        real_entry = user_entries[-(entry_id + 1)]
        try:
            real_entry['plans'][plan_index]['done'] = not real_entry['plans'][plan_index]['done']
            save_entries(entries)
            return jsonify(success=True)
        except IndexError:
            pass

    return jsonify(success=False), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username], password):
            session['user'] = username
            flash("Logged in successfully.")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash("Username already exists.")
            return redirect(url_for('register'))

        users[username] = generate_password_hash(password)
        save_users(users)
        flash("Registration successful. You can now log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You were logged out.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
