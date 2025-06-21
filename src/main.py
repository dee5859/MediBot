import auth
import med_search
from datetime import datetime 


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
        
        api_data = med_search.fetch_drug_info(drug_name)
        drug_info = med_search.parse_drug_data(api_data, drug_name)  # Pass drug_name here
        
        med_search.display_drug_info(drug_info)
        
        med_search.save_search_history(
            username, 
            drug_name, 
            bool(drug_info) 
        )
        
        input("\nPress Enter to search again...")
        

def main():
    """Main program loop"""
    current_user = None 
    
    while True:
        choice = show_main_menu()
        
        if choice == '1':
            auth.register_user()
            input("\nPress Enter to continue...")
        elif choice == '2':
            if auth.login():
                current_user = input("Username: ").strip()  # Get username
                input("\nPress Enter to access MediBot...")
                print("\n" + "=" * 40)
                print("ACCESS GRANTED! Welcome to MediBot.")
                print("=" * 40)
                print("Session started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                medicine_search_interface(current_user)
        elif choice == '3':
            print("\nExiting MediBot. Goodbye!")
            break

if __name__ == "__main__":
    main()