# src/med_search.py
import requests
import json
import os

# API Configuration (using FDA OpenAPI - no key required)
API_URL = "https://api.fda.gov/drug/label.json"
CACHE_FILE = "med_cache.json"

def get_medicine_name():
    """Get medicine name input from user"""
    print("\n" + "=" * 40)
    print("MEDICINE INFORMATION SEARCH".center(40))
    print("=" * 40)
    return input("Enter medicine name (or 'back' to return): ").strip()

def fetch_drug_info(drug_name):
    """Fetch drug information from FDA API"""
    params = {
        "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
        "limit": 1
    }
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise error for bad status
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\nAPI Error: {str(e)}")
        return None

def parse_drug_data(api_data):
    """Extract relevant information from API response"""
    if not api_data or 'results' not in api_data or not api_data['results']:
        return None
    
    drug_data = api_data['results'][0]
    openfda = drug_data.get('openfda', {})
    
    return {
        'name': openfda.get('brand_name', [''])[0] or openfda.get('generic_name', [''])[0],
        'generic_name': ', '.join(openfda.get('generic_name', [])),
        'uses': drug_data.get('indications_and_usage', ['Not available'])[0],
        'side_effects': drug_data.get('warnings', ['Not available'])[0],
        'dosage': drug_data.get('dosage_and_administration', ['Not available'])[0],
        'ingredients': ', '.join(openfda.get('substance_name', []))
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
    print(f"\nUses: {drug_info.get('uses', 'Not available')}")
    print(f"\nSide Effects: {drug_info.get('side_effects', 'Not available')}")
    print(f"\nDosage: {drug_info.get('dosage', 'Not available')}")
    print(f"\nActive Ingredients: {drug_info.get('ingredients', 'Not available')}")
    print("=" * 40)