#!/usr/bin/env python3
from scraper import scrape

print('=== Testing URL Scraping ===')

# Test with and without protocol
test_urls = [
    'acuitytraining.co.uk',       # No protocol
    'https://acuitytraining.co.uk', # With protocol
    'york-it-services.co.uk',
    'https://york-it-services.co.uk'
]

for url in test_urls:
    print(f'\nTesting: {url}')
    try:
        result = scrape(url)
        print(f'Company: {result.get("company_name", "Not found")}')
        print(f'Address: {result.get("address", "Not found")}')
        print(f'Officer: {result.get("officer", "Not found")}')
        print(f'Source: {result.get("source", "Not found")}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        print(traceback.format_exc())
