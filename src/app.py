import os
import json
import hashlib
import random
import string
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory, redirect, url_for
import requests
from functools import wraps

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key_here'  # Change this in production!

USER_FILE = "users.json"
SEARCH_HISTORY_FILE = "search_history.json"

ADMIN_USERNAME = "medadmin"
ADMIN_PASSWORD = "Deeadmin@123"  # Change this in production!

API_URL = "https://api.fda.gov/drug/label.json"

PASSWORD_REQUIREMENTS = {
    'min_length': 8,
    'require_upper': True,
    'require_lower': True,
    'require_digit': True,
    'require_special': True,
    'allowed_special': '!@#$%^&*()-_=+[]{}|;:,.<>?'
}

def validate_password(password):
    errors = []
    if len(password) < PASSWORD_REQUIREMENTS['min_length']:
        errors.append(f"Password must be at least {PASSWORD_REQUIREMENTS['min_length']} characters")
    if PASSWORD_REQUIREMENTS['require_upper'] and not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    if PASSWORD_REQUIREMENTS['require_lower'] and not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    if PASSWORD_REQUIREMENTS['require_digit'] and not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    if PASSWORD_REQUIREMENTS['require_special']:
        if not any(c in PASSWORD_REQUIREMENTS['allowed_special'] for c in password):
            errors.append(f"Password must contain at least one special character: {PASSWORD_REQUIREMENTS['allowed_special']}")
    return errors

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def save_search_history(username, drug_name, success):
    history = []
    if os.path.exists(SEARCH_HISTORY_FILE):
        try:
            with open(SEARCH_HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append({
        'username': username,
        'drug_name': drug_name,
        'timestamp': datetime.now().isoformat(),
        'success': success
    })
    with open(SEARCH_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def root():
    # Serve the frontend index.html
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    users = load_users()

    if username not in users:
        return jsonify({'success': False, 'message': 'Invalid username or password'})
    user_data = users[username]
    hashed_input = hashlib.sha256(password.encode()).hexdigest()

    # Support old format (just hash string)
    if isinstance(user_data, str):
        if user_data == hashed_input:
            users[username] = {
                'password_hash': hashed_input,
                'created_at': datetime.now().isoformat(),
                'created_by': 'system',
                'login_history': [datetime.now().isoformat()],
                'password_changed': True
            }
            save_users(users)
            session['username'] = username
            session['is_admin'] = (username == ADMIN_USERNAME)
            return jsonify({'success': True, 'username': username})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})

    # New format
    if user_data.get('password_hash') == hashed_input:
        user_data.setdefault('login_history', []).append(datetime.now().isoformat())
        save_users(users)
        session['username'] = username
        session['is_admin'] = (username == ADMIN_USERNAME)
        return jsonify({
            'success': True,
            'username': username,
            'requires_password_change': not user_data.get('password_changed', True)
        })
    return jsonify({'success': False, 'message': 'Invalid username or password'})

@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['username'] = username
        session['is_admin'] = True
        return jsonify({'success': True, 'username': username})
    return jsonify({'success': False, 'message': 'Invalid admin credentials'})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/search', methods=['POST'])
def search_drugs():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    data = request.json
    drug_name = data.get('drug_name', '').strip()
    if not drug_name:
        return jsonify({'success': False, 'message': 'Drug name required'})
    params = {
        "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
        "limit": 1
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        api_data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'API Error: {str(e)}'})
    drug_info = {}
    if api_data and 'results' in api_data and api_data['results']:
        drug_data = api_data['results'][0]
        openfda = drug_data.get('openfda', {})
        brand_name = openfda.get('brand_name', [''])[0] if openfda.get('brand_name') else ''
        generic_name = openfda.get('generic_name', [''])[0] if openfda.get('generic_name') else ''
        drug_info = {
            'name': brand_name or generic_name or drug_name,
            'generic_name': ', '.join(openfda.get('generic_name', [])) or 'Not available',
            'uses': drug_data.get('indications_and_usage', ['Not available'])[0],
            'side_effects': drug_data.get('warnings', ['Not available'])[0],
            'dosage': drug_data.get('dosage_and_administration', ['Not available'])[0],
            'ingredients': ', '.join(openfda.get('substance_name', [])) or 'Not available',
            'warnings': drug_data.get('warnings_and_cautions', ['Not available'])[0],
            'mechanism': drug_data.get('mechanism_of_action', ['Not available'])[0],
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    save_search_history(session['username'], drug_name, bool(drug_info))
    return jsonify({
        'success': True,
        'drug_info': drug_info if drug_info else None,
        'message': 'Drug information found' if drug_info else 'No information found'
    })

@app.route('/admin/create_user', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    username = data.get('username', '').strip()
    if not username:
        return jsonify({'success': False, 'message': 'Username required'})
    users = load_users()
    if username in users:
        return jsonify({'success': False, 'message': f"Username '{username}' already exists"})
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {
        'password_hash': hashed_password,
        'created_at': datetime.now().isoformat(),
        'created_by': session['username'],
        'login_history': [],
        'password_changed': False
    }
    save_users(users)
    return jsonify({
        'success': True,
        'message': f"User '{username}' created successfully",
        'generated_password': password
    })

@app.route('/admin/reset_password', methods=['POST'])
@admin_required
def reset_password():
    data = request.json
    username = data.get('username', '').strip()
    if not username:
        return jsonify({'success': False, 'message': 'Username required'})
    users = load_users()
    if username not in users:
        return jsonify({'success': False, 'message': f"User '{username}' does not exist"})
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
    users[username]['password_hash'] = hashed_password
    users[username]['password_changed'] = False
    if 'password_resets' not in users[username]:
        users[username]['password_resets'] = []
    users[username]['password_resets'].append({
        'reset_by': session['username'],
        'timestamp': datetime.now().isoformat()
    })
    save_users(users)
    return jsonify({
        'success': True,
        'message': f"Password for '{username}' has been reset",
        'new_password': new_password
    })

@app.route('/user/history', methods=['GET'])
def get_user_history():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    history = []
    if os.path.exists(SEARCH_HISTORY_FILE):
        try:
            with open(SEARCH_HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except Exception:
            history = []
    user_history = [h for h in history if h['username'] == session['username']]
    return jsonify({'success': True, 'history': user_history})

# Serve static files (index.html, script.js, etc.)
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    # Create empty files if missing
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(SEARCH_HISTORY_FILE):
        with open(SEARCH_HISTORY_FILE, 'w') as f:
            json.dump([], f)
    app.run(debug=True, port=5000)
