#!/usr/bin/env python3
"""Test script to verify the fast scraper on specific sites"""

from fast_scraper import scrape
import warnings
# Ignore SSL warnings for testing
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# List of sites to test
test_sites = [
    "blossomhouseschool.co.uk",
    "ballyhoo-pr.co.uk", 
    "charnwood-milling.co.uk",
    "argolin.com",
    "booth-ac.com",
    "independentlifting.com",
    "beeteealarmsltd.co.uk",
    "airstudios.com",
    "wymondhamcollege.org",
    "beckprosper.com"
]

print("=" * 80)
print("Testing Fast Scraper on Specific Sites")
print("=" * 80)
print()

for site in test_sites:
    print(f"{'='*60}")
    print(f"Scraping: {site}")
    print(f"{'='*60}")
    
    try:
        # Ensure we have https protocol
        url = site if site.startswith("http") else f"https://{site}"
        result = scrape(url)
        
        print(f"Company Name: {result.get('company_name', 'N/A')}")
        print(f"Address: {result.get('address', 'N/A')}")
        print(f"Officer: {result.get('officer', 'N/A')}")
        print(f"Source: {result.get('source', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"Error scraping {site}: {str(e)}")
        print()

print("=" * 80)
print("Testing Completed")
print("=" * 80)
