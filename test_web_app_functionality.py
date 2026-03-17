#!/usr/bin/env python3
"""Test web application functionality"""

import requests
import time
import re

def test_web_application():
    print("=== Web Application Functionality Test ===")
    
    # Wait for server to be ready
    time.sleep(1)
    
    session = requests.Session()
    
    # Test 1: Access main page
    try:
        response = session.get('http://localhost:5000')
        print(f"1. Main page response: {response.status_code}")
        print(f"   Content type: {response.headers.get('Content-Type')}")
    except Exception as e:
        print(f"1. Error accessing main page: {e}")
        return False
    
    if response.status_code != 200:
        return False
    
    # Test 2: Check if form exists
    form_match = re.search(r'<form', response.text, re.IGNORECASE)
    print(f"2. Form found: {bool(form_match)}")
    
    # Find CSRF token in hidden input
    csrf_token_match = re.search(r'<input.*?name="csrf_token".*?value="([^"]+)"', response.text)
    print(f"3. CSRF token found: {bool(csrf_token_match)}")
    
    # Test 3: Submit test data
    if csrf_token_match:
        csrf_token = csrf_token_match.group(1)
        test_data = {
            'csrf_token': csrf_token,
            'urls': 'https://www.arts1.co.uk',
            'submit': 'Scrape'
        }
        
        headers = {
            'Referer': 'http://localhost:5000',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            scrape_response = session.post('http://localhost:5000', data=test_data, headers=headers)
            print(f"4. Scrape request response: {scrape_response.status_code}")
            
            # Check if results contain expected data
            if 'Scraping Results' in scrape_response.text:
                print("5. OK: Results page detected")
                
                # Check for company name in results
                if 'Arts1 School of Performance' in scrape_response.text:
                    print("6. OK: Scraping results verified - Arts1 School of Performance found")
                else:
                    print("6. ERROR: Company name not found in results")
            else:
                print("5. ERROR: Results page not found")
                print("\nResponse snippet:", scrape_response.text[:500])
        except Exception as e:
            print(f"5. Error submitting scrape request: {e}")
    
    print("\n=== All tests completed ===")
    return True

if __name__ == "__main__":
    test_web_application()
