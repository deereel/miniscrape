#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

def test_simple_scraping():
    print("=== Testing MiniScrape Protocol Handling ===\n")
    
    # Get CSRF token
    response = requests.get('http://localhost:5000')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    print(f"CSRF Token: {csrf_token}")
    
    # Test with just 2 URLs to keep it fast
    urls_to_test = [
        'acuitytraining.co.uk',
        'york-it-services.co.uk'
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
    response = requests.post('http://localhost:5000', data=data, headers=headers, timeout=30)
    print(f"Response status code: {response.status_code}")
    
    # Check if results were returned
    if 'Scraping Results' in response.text:
        print("\n✓ Results page received successfully")
        
        if 'Acuity Training' in response.text:
            print("✓ Acuity Training found")
        
        if 'York' in response.text:
            print("✓ York IT Services found")
            
        errors = response.text.count('ERROR')
        if errors > 0:
            print(f"⚠️ Errors found: {errors}")
        else:
            print("✓ All sites scraped successfully")
    else:
        print("\n❌ Results page not found")
        print(f"Response content (first 500 characters):\n{response.text[:500]}")

if __name__ == "__main__":
    try:
        test_simple_scraping()
    except Exception as e:
        print(f"\nError: {e}")
