# main.py
import auth

def clear_screen():
    """More reliable screen clearing"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def show_main_menu():
    """Improved menu with input validation"""
    clear_screen()
    print("\n" + "=" * 40)
    print("MEDIBOT TERMINAL SYSTEM".center(40))
    print("=" * 40)
    print("1. Register new user")
    print("2. Login")
    print("3. Exit")
    
    while True:  # Keep asking until valid input
        choice = input("\nChoose option (1-3): ").strip()  # Remove whitespace
        
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid choice! Please enter 1, 2, or 3")

def main():
    """Main program loop"""
    while True:
        choice = show_main_menu()  
        print(f"DEBUG: Input was '{choice}' with length {len(choice)}")
        if choice == '1':
            auth.register_user()
            input("\nPress Enter to continue...")
        elif choice == '2':
            if auth.login():
                input("\nPress Enter to enter MediBot...")
                print("\n ACCESS GRANTED! Welcome to MediBot.")
                # We'll add medicine search here later
                break
        elif choice == '3':
            print("\n Exiting MediBot. Goodbye!")
            break

if __name__ == "__main__":
    print("Program started successfully!")
    main()