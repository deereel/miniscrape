#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

def test_scraping():
    print("=== Testing MiniScrape Web Application ===\n")
    
    # Get CSRF token
    response = requests.get('http://localhost:5000')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    print(f"CSRF Token: {csrf_token}")
    
    # Test scraping with fixed URLs
    urls_to_test = [
        'acuitytraining.co.uk',
        'devereintellica.com', 
        'sangersaah.co.uk',
        'themayfairprintingco.com',
        'bartechturbos.com',
        'york-it-services.co.uk',
        'parkcitylondon.co.uk',
        'bpmsltd.co.uk',
        'practicemanagersuk.org',
        'holdsworth-foods.co.uk'
    ]
    
    # Prepare form data
    data = {
        'csrf_token': csrf_token,
        'urls': '\n'.join(urls_to_test),  # Newline-separated URLs
        'submit': 'Scrape'
    }
    
    headers = {
        'Cookie': response.headers.get('Set-Cookie'),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Submit the form
    print("\nSubmitting form...")
    response = requests.post('http://localhost:5000', data=data, headers=headers)
    print(f"Response status code: {response.status_code}")
    
    # Check if results were returned
    if 'Scraping Results' in response.text:
        print("\n✓ Results page received successfully")
        
        # Check if any results are present
        if 'Acuity Training' in response.text:
            print("✓ Acuity Training found")
        
        errors = response.text.count('ERROR')
        if errors > 0:
            print(f"⚠️ Errors found: {errors}")
        else:
            print("✓ All sites scraped successfully")
            
        # Count how many results have data
        results_count = response.text.count('<tr>') - 1  # Subtract header row
        print(f"Results found: {results_count}")
    else:
        print("\n❌ Results page not found")
        print(f"Response content (first 500 characters):\n{response.text[:500]}")

if __name__ == "__main__":
    test_scraping()
