#!/usr/bin/env python3
"""Debug form submission"""

import requests
import re

session = requests.Session()

# 1. Get main page to get CSRF token
response = session.get('http://localhost:5000')
csrf_token_match = re.search(r'<input.*?name="csrf_token".*?value="([^"]+)"', response.text)

if csrf_token_match:
    csrf_token = csrf_token_match.group(1)
    print("CSRF Token:", csrf_token)
    
    # 2. Submit the form
    test_data = {
        'csrf_token': csrf_token,
        'urls': 'https://www.arts1.co.uk',
        'submit': 'Scrape'
    }
    
    headers = {
        'Referer': 'http://localhost:5000',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    scrape_response = session.post('http://localhost:5000', data=test_data, headers=headers)
    print("\nResponse Status:", scrape_response.status_code)
    print("\nFirst 1000 characters of response:")
    print(repr(scrape_response.text[:1000]))
    
    if 'Scraping Results' in scrape_response.text:
        print("\nOK: Results page detected!")
        print("\nChecking for 'Arts1' in results:")
        arts1_count = scrape_response.text.count('Arts1')
        print(f"Found 'Arts1' {arts1_count} times")
        
        # Look for results table
        if 'Company Name' in scrape_response.text:
            print("\nOK: Results table detected")
        
        # Try to extract company name from results
        company_name = re.search(r'<td[^>]*>(.*?Arts1.*?)</td>', scrape_response.text, re.DOTALL)
        if company_name:
            print(f"\nOK: Company name extracted: {company_name.group(1).strip()}")
    else:
        print("\nERROR: Not redirected to results page - still on main page")
        print("\nForm errors in response:")
        errors = re.findall(r'<div class="form-error">(.*?)</div>', scrape_response.text)
        if errors:
            print("\n".join(f"  - {e.strip()}" for e in errors))
else:
    print("❌ Failed to find CSRF token")
