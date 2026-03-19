#!/usr/bin/env python3
from fast_scraper import scrape

sites = [
    "aquaterra.co.uk",
    "drewry.co.uk",
    "weareyellowball.com",
    "vistechcooling.co.uk",
    "avs-uk.co.uk"
]

print("=" * 80)
print("Scraping Sites")
print("=" * 80)
print()

for site in sites:
    print(f"{'=' * 60}")
    print(f"Site: {site}")
    print(f"{'=' * 60}")
    
    try:
        result = scrape(f"https://{site}")
        print(f"  Company Name: {result.get('company_name', 'N/A')}")
        print(f"  Address: {result.get('address', 'N/A')}")
        print(f"  Officer: {result.get('officer', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"  Error: {e}")
        print()

print("=" * 80)
print("Scraping Completed")
print("=" * 80)
