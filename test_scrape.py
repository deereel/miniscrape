#!/usr/bin/env python3
from scraper import scrape

# Test single URL
url = 'https://www.arts1.co.uk'
print(f"Testing URL: {url}")

try:
    result = scrape(url)
    
    print("\n=== Scraping Result ===")
    for key, value in result.items():
        print(f"{key}: {value}")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    print(traceback.format_exc())
