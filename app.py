from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_entries():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    entries = load_entries()
    return render_template('index.html', entries=entries[::-1], emotions=['happy', 'sad', 'angry', 'joyful', 'tired','hungry','stressful'])

@app.route('/save', methods=['POST'])
def save():
    emotion = request.form.get('emotion')
    notes = request.form.get('notes')
    plans_texts = request.form.getlist('plans[]')

    entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'emotion': emotion,
        'notes': notes,
        'plans': [{'text': text, 'done': False} for text in plans_texts if text.strip()]
    }

    entries = load_entries()
    entries.append(entry)
    save_entries(entries)
    return redirect(url_for('index'))

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    entries = load_entries()
    if 0 <= entry_id < len(entries):
        entries.pop(len(entries) - 1 - entry_id)  # because we reverse when displaying
        save_entries(entries)
    return redirect(url_for('index'))

@app.route('/toggle_done/<int:entry_id>/<int:plan_index>', methods=['POST'])
def toggle_done(entry_id, plan_index):
    entries = load_entries()
    real_index = len(entries) - 1 - entry_id
    if 0 <= real_index < len(entries):
        entry = entries[real_index]
        if 0 <= plan_index < len(entry['plans']):
            entry['plans'][plan_index]['done'] = not entry['plans'][plan_index]['done']
            save_entries(entries)
            return jsonify(success=True)
    return jsonify(success=False), 400

if __name__ == '__main__':
    app.run(debug=True)

