# src/med_search.py
import requests
import json
import os
from datetime import datetime

# FDA Drug API - no key required
API_URL = "https://api.fda.gov/drug/label.json"
CACHE_FILE = "med_cache.json"
SEARCH_HISTORY_FILE = "search_history.json"

def search_medicine():
    """Get medicine name from user"""
    print("\n" + "=" * 40)
    print("MEDICINE INFORMATION SEARCH".center(40))
    print("=" * 40)
    return input("Enter medicine name (or 'exit' to quit): ").strip()

def fetch_drug_info(drug_name):
    """Fetch drug information from FDA API"""
    params = {
        "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
        "limit": 1
    }
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\nAPI Error: {str(e)}")
        return None
    params={
        "search": f'(openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}" OR openfda.substance_name:{drug_name}")', "limit": 5
    }

def parse_drug_data(api_data, drug_name):
    """Extract relevant information from API response"""
    if not api_data or 'results' not in api_data or not api_data['results']:
        return None
    
    drug_data = api_data['results'][0]
    openfda = drug_data.get('openfda', {})
    
    # Get brand name or generic name
    brand_name = openfda.get('brand_name', [''])[0] if openfda.get('brand_name') else ''
    generic_name = openfda.get('generic_name', [''])[0] if openfda.get('generic_name') else ''
    
    return {
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

def display_drug_info(drug_info):
    """Display drug information in terminal"""
    if not drug_info:
        print("\nNo information found for this medicine.")
        return
    
    print("\n" + "=" * 40)
    print("MEDICINE INFORMATION".center(40))
    print("=" * 40)
    print(f"Brand Name: {drug_info.get('name', 'Not available')}")
    print(f"Generic Name: {drug_info.get('generic_name', 'Not available')}")
    print(f"\nPrimary Uses:\n{drug_info.get('uses', 'Not available')}")
    print(f"\nMechanism of Action:\n{drug_info.get('mechanism', 'Not available')}")
    print(f"\nDosage Information:\n{drug_info.get('dosage', 'Not available')}")
    print(f"\nActive Ingredients: {drug_info.get('ingredients', 'Not available')}")
    print(f"\nSide Effects:\n{drug_info.get('side_effects', 'Not available')}")
    print(f"\nWarnings:\n{drug_info.get('warnings', 'Not available')}")
    print(f"\nInformation Last Updated: {drug_info.get('last_updated', 'Not available')}")
    print("=" * 40)

def save_search_history(username, drug_name, success):
    """Save search history to file"""
    history = load_search_history()
    
    entry = {
        'username': username,
        'drug_name': drug_name,
        'timestamp': datetime.now().isoformat(),
        'success': success
    }
    
    history.append(entry)
    
    with open(SEARCH_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def load_search_history():
    """Load search history from file"""
    if os.path.exists(SEARCH_HISTORY_FILE):
        try:
            with open(SEARCH_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []