# auth.py
import hashlib
import json
import getpass
import os
from datetime import datetime

USER_FILE = "users.json"

# Password policy configuration - using requested name
Password_requirements = {
    'min_length': 8,
    'require_upper': True,
    'require_lower': True,
    'require_digit': True,
    'require_special': True,
    'allowed_special': '!@#$%^&*()-_=+[]{}|;:,.<>?'
}

def validate_password(password):
    """Enforce password policy requirements"""
    errors = []
    
    # Check minimum length
    if len(password) < Password_requirements['min_length']:
        errors.append(f"Password must be at least {Password_requirements['min_length']} characters")
    
    # Check for uppercase
    if Password_requirements['require_upper'] and not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase
    if Password_requirements['require_lower'] and not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for digits
    if Password_requirements['require_digit'] and not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit")
    
    # Check for special characters
    if Password_requirements['require_special']:
        special_chars = Password_requirements['allowed_special']
        if not any(char in special_chars for char in password):
            errors.append(f"Password must contain at least one special character: {special_chars}")
    
    return errors

def show_password_requirements():
    """Display password policy to user"""
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
    
    print()  # Empty line for spacing

def register_user():
    """Register a new user with password hashing"""
    print("\n" + "=" * 40)
    print("NEW USER REGISTRATION".center(40))
    print("=" * 40)
    
    # Get username
    username = input("Choose a username: ").strip()
    
    # Load existing users or create empty dictionary
    users = {}
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'r') as file:
                users = json.load(file)
        except json.JSONDecodeError:
            print("User file corrupted. Starting fresh.")
    
    # Check if username exists
    if username in users:
        print(f"Username '{username}' already exists!")
        return False
    
    # Show password requirements
    show_password_requirements()
    
    # Get password securely
    while True:
        password = getpass.getpass("Create password: ")
        confirm = getpass.getpass("Confirm password: ")
        
        # Check if passwords match
        if password != confirm:
            print("Passwords don't match. Try again.")
            continue
            
        # Validate password strength
        validation_errors = validate_password(password)
        
        if not validation_errors:
            break  # Password is valid
            
        print("\nPassword does not meet requirements:")
        for error in validation_errors:
            print(f"- {error}")
        print("Please try again.\n")
    
    # Hash password using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Create user entry with login history
    users[username] = {
        'password_hash': hashed_password,
        'created_at': datetime.now().isoformat(),
        'login_history': []
    }
    
    # Save new user
    with open(USER_FILE, 'w') as file:
        json.dump(users, file, indent=4)
    
    print("Registration successful!")
    return True

def login():
    """Authenticate existing user and record login time"""
    print("\n" + "=" * 40)
    print("USER LOGIN".center(40))
    print("=" * 40)
    
    # Get credentials
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    
    # Check if user file exists
    if not os.path.exists(USER_FILE):
        print("No users registered yet!")
        return False
    
    # Load users
    try:
        with open(USER_FILE, 'r') as file:
            users = json.load(file)
    except json.JSONDecodeError:
        print("Corrupted user file!")
        return False
    
    # Hash input password
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    
    # Check if user exists
    if username not in users:
        print("\nInvalid username or password")
        return False
    
    user_data = users[username]
    
    # Handle old format (just password hash)
    if isinstance(user_data, str):
        # Convert to new format
        if user_data == hashed_input:
            # Migrate to new format
            users[username] = {
                'password_hash': hashed_input,
                'created_at': datetime.now().isoformat(),
                'login_history': [datetime.now().isoformat()]
            }
            
            # Save updated user data
            with open(USER_FILE, 'w') as file:
                json.dump(users, file, indent=4)
            
            print("\nLogin successful! Your account has been upgraded.")
            return True
        else:
            print("\nInvalid username or password")
            return False
    
    # Handle new format (dictionary)
    if user_data['password_hash'] == hashed_input:
        # Add login timestamp to history
        login_time = datetime.now().isoformat()
        user_data['login_history'].append(login_time)
        
        # Save updated user data
        with open(USER_FILE, 'w') as file:
            json.dump(users, file, indent=4)
        
        print("\nLogin successful!")
        return True
    
    print("\nInvalid username or password")
    return False