# src/auth.py
import hashlib
import json
import getpass
import os
import random
import string
from datetime import datetime

USER_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')

ADMIN_USERNAME = "medadmin"
ADMIN_PASSWORD = "Deeadmin@123"

Password_requirements = {
    'min_length': 8,
    'require_upper': True,
    'require_lower': True,
    'require_digit': True,
    'require_special': True,
    'allowed_special': '!@#$%^&*()-_=+[]{}|;:,.<>?'
}

def validate_password(password):
    errors = []
    if len(password) < Password_requirements['min_length']:
        errors.append(f"Password must be at least {Password_requirements['min_length']} characters")
    if Password_requirements['require_upper'] and not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter")
    if Password_requirements['require_lower'] and not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter")
    if Password_requirements['require_digit'] and not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit")
    if Password_requirements['require_special']:
        special_chars = Password_requirements['allowed_special']
        if not any(char in special_chars for char in password):
            errors.append(f"Password must contain at least one special character: {special_chars}")
    return errors

def show_password_requirements():
    print("\nPassword Requirements:")
    print(f"- Minimum length: {Password_requirements['min_length']} characters")
    if Password_requirements['require_upper']:
        print("- At least one uppercase letter (A-Z)")
    if Password_requirements['require_lower']:
        print("- At least one lowercase letter (a-z)")
    if Password_requirements['require_digit']:
        print("- At least one digit (0-9)")
    if Password_requirements['require_special']:
        print(f"- At least one special character: {Password_requirements['allowed_special']}")
    print()

def admin_login():
    print("\n" + "=" * 40)
    print("ADMIN LOGIN".center(40))
    print("=" * 40)
    username = input("Admin Username: ").strip()
    password = getpass.getpass("Admin Password: ")
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def create_user(admin_username):
    print("\n" + "=" * 40)
    print("CREATE NEW USER".center(40))
    print("=" * 40)
    username = input("Enter new username: ").strip()
    users = {}
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'r') as file:
                users = json.load(file)
        except json.JSONDecodeError:
            print("User file corrupted. Starting fresh.")

    if username in users:
        print(f"Username '{username}' already exists!")
        return False

    # Generate password with special chars
    all_chars = string.ascii_letters + string.digits + Password_requirements['allowed_special']
    password = ''.join(random.choices(all_chars, k=12))
    print(f"\nGenerated password: {password}")
    input("Press Enter to continue...")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {
        'password_hash': hashed_password,
        'created_at': datetime.now().isoformat(),
        'created_by': admin_username,
        'login_history': [],
        'password_changed': False
    }
    with open(USER_FILE, 'w') as file:
        json.dump(users, file, indent=4)
    print(f"\nUser '{username}' created successfully!")
    return True

def reset_user_password(admin_username):
    if not admin_login():
        print("\nAdmin login failed!")
        return False
    print("\n" + "="*40)
    print("Reset user password".center(40))
    print("="*40)
    username = input("Enter the username to reset password:").strip()
    users = {}
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'r') as file:
                users = json.load(file)
        except json.JSONDecodeError:
            print("User file corrupted.")
            return False
    if username not in users:
        print(f"User '{username}' does not exist!")
        return False
    all_chars = string.ascii_letters + string.digits + Password_requirements['allowed_special']
    new_password = ''.join(random.choices(all_chars, k=12))
    print(f"\nNew Password for {username} : {new_password}")

    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
    users[username]['password_hash'] = hashed_password
    users[username]['password_changed'] = False
    if 'password_resets' not in users[username]:
        users[username]['password_resets'] = []
    users[username]['password_resets'].append({
        'reset_by': admin_username,
        'timestamp': datetime.now().isoformat()
    })
    with open(USER_FILE, 'w') as file:
        json.dump(users, file, indent=4)
    print(f"\nPassword for '{username}' has been reset successfully!")
    return True

def get_login_history(username):
    if not os.path.exists(USER_FILE):
        return []
    try:
        with open(USER_FILE, 'r') as file:
            users = json.load(file)
        if username in users:
            if isinstance(users[username], dict):
                return users[username].get('login_history', [])
            else:
                return [datetime.now().isoformat()]
        return []
    except:
        return []

def login():
    print("\n" + "=" * 40)
    print("USER LOGIN".center(40))
    print("=" * 40)
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    if not os.path.exists(USER_FILE):
        print("No users registered yet!")
        return False
    try:
        with open(USER_FILE, 'r') as file:
            users = json.load(file)
    except json.JSONDecodeError:
        print("Corrupted user file!")
        return False
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    if username not in users:
        print("\nInvalid username or password")
        return False
    user_data = users[username]
    if isinstance(user_data, str):
        if user_data == hashed_input:
            users[username] = {
                'password_hash': hashed_input,
                'created_at': datetime.now().isoformat(),
                'created_by': 'system',
                'login_history': [datetime.now().isoformat()],
                'password_changed': True
            }
            with open(USER_FILE, 'w') as file:
                json.dump(users, file, indent=4)
            print("\nLogin successful! Your account has been upgraded.")
            return True
        else:
            print("\nInvalid username or password")
            return False
    if user_data['password_hash'] == hashed_input:
        login_time = datetime.now().isoformat()
        user_data['login_history'].append(login_time)
        with open(USER_FILE, 'w') as file:
            json.dump(users, file, indent=4)
        print("\nLogin successful!")
        if not user_data.get('password_changed', True):
            print("\nWARNING: Please change your temporary password!")
            input("Press Enter to continue to medicine search...")
        return True
    print("\nInvalid username or password")
    return False
