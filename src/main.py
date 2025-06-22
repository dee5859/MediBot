# src/main.py
import auth
import med_search
import os
import json
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def show_main_menu():
    """Display main menu with input validation"""
    clear_screen()
    print("\n" + "=" * 40)
    print("MEDIBOT TERMINAL SYSTEM".center(40))
    print("=" * 40)
    print("1. Login")
    print("2. Admin Tools")
    print("3. Exit")
    
    while True:
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid choice! Please enter 1, 2, or 3")

def medicine_search_interface(username):
    """Medicine search and display interface"""
    while True:
        clear_screen()
        drug_name = med_search.search_medicine()
        
        if drug_name.lower() == 'exit':
            print("\nReturning to main menu...")
            break
            
        if not drug_name:
            print("\nPlease enter a valid medicine name.")
            input("Press Enter to continue...")
            continue
            
        print(f"\nSearching for '{drug_name}'...")
        
        # Fetch drug info
        api_data = med_search.fetch_drug_info(drug_name)
        drug_info = med_search.parse_drug_data(api_data, drug_name)
        
        # Display results
        med_search.display_drug_info(drug_info)
        
        # Save search history
        med_search.save_search_history(
            username, 
            drug_name, 
            bool(drug_info)  # True if info found
        )
        
        input("\nPress Enter to search again...")

def admin_tools():
    """Admin management interface"""
    print("\n" + "=" * 40)
    print("ADMIN TOOLS".center(40))
    print("=" * 40)
    print("1. Create New User")
    print("2. View User List")
    print("3. Reset User Password")
    print("4. View Login History")
    print("5. Back to Main Menu")
    
    choice = input("\nSelect option (1-5): ").strip()
    return choice

def view_user_list():
    """Display list of all users"""
    if not os.path.exists(auth.USER_FILE):
        print("\nNo users registered yet!")
        return
        
    try:
        with open(auth.USER_FILE, 'r') as file:
            users = json.load(file)
            
        print("\n" + "=" * 40)
        print("USER LIST".center(40))
        print("=" * 40)
        for i, (username, data) in enumerate(users.items(), 1):
            # Handle both old and new user formats
            if isinstance(data, dict):
                created_at = datetime.fromisoformat(data['created_at']).strftime("%Y-%m-%d")
                creator = data.get('created_by', 'system')
            else:  # Old string format
                created_at = "Unknown"
                creator = "system"
                
            print(f"{i}. {username} (Created: {created_at} by {creator})")
        print("=" * 40)
        
    except Exception as e:
        print(f"\nError loading user list: {str(e)}")

def reset_password_interface():
    """Interface for password reset"""
    print("\n" + "=" * 40)
    print("RESET USER PASSWORD".center(40))
    print("=" * 40)
    username = input("Enter username to reset password: ").strip()
    if auth.reset_user_password(auth.ADMIN_USERNAME):
        print(f"\nPassword for {username} has been reset successfully!")
    else:
        print(f"\nFailed to reset password for {username}")
    input("\nPress Enter to continue...")

def view_login_history_interface():
    """Interface for viewing login history"""
    print("\n" + "=" * 40)
    print("VIEW LOGIN HISTORY".center(40))
    print("=" * 40)
    username = input("Enter username to view login history: ").strip()
    history = auth.get_login_history(username)
    
    print("\n" + "=" * 40)
    print(f"LOGIN HISTORY FOR {username.upper()}".center(40))
    print("=" * 40)
    
    if not history:
        print("No login history found")
    else:
        for i, timestamp in enumerate(history, 1):
            dt = datetime.fromisoformat(timestamp)
            print(f"{i}. {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("=" * 40)
    input("\nPress Enter to continue...")

def main():
    """Main program loop"""
    while True:
        choice = show_main_menu()
        
        if choice == '1':  # Regular user login
            if auth.login():
                username = input("Username: ").strip()
                input("\nPress Enter to access MediBot...")
                print("\n" + "=" * 40)
                print("ACCESS GRANTED! Welcome to MediBot.")
                print("=" * 40)
                print("Session started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # Enter medicine search interface
                medicine_search_interface(username)
                
        elif choice == '2':  # Admin tools
            if auth.admin_login():
                while True:
                    clear_screen()
                    admin_choice = admin_tools()
                    
                    if admin_choice == '1':  # Create user
                        auth.create_user(auth.ADMIN_USERNAME)
                        input("\nPress Enter to continue...")
                    elif admin_choice == '2':  # View user list
                        view_user_list()
                        input("\nPress Enter to continue...")
                    elif admin_choice == '3':  # Reset password
                        reset_password_interface()
                    elif admin_choice == '4':  # View login history
                        view_login_history_interface()
                    elif admin_choice == '5':  # Back to main
                        break
                    else:
                        print("\nInvalid choice!")
                        input("Press Enter to continue...")
            else:
                print("\nAdmin authentication failed!")
                input("Press Enter to continue...")
                
        elif choice == '3':  # Exit
            print("\nExiting MediBot. Goodbye!")
            break

if __name__ == "__main__":
    main()