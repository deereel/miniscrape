#!/usr/bin/env python3
"""Debug script to see what data is extracted from website vs Companies House"""

from scraper import scrape_website, search_companies_house
import time


def debug_scrape(site):
    """Debug function to show website vs Companies House data"""
    print(f"\n{'='*50}")
    print(f"Debugging: {site}")
    print(f"{'='*50}")
    
    url = f"https://www.{site}"
    
    # Test website scraping
    print(f"\n[1] Website Scraping:")
    try:
        site_data = scrape_website(url)
        print(f"  Company Name: '{site_data.get('company_name', '')}'")
        print(f"  Address: '{site_data.get('address', '')}'")
        print(f"  Officer: '{site_data.get('officer', '')}'")
        print(f"  Registered Name: '{site_data.get('registered_name', '')}'")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test Companies House search
    print(f"\n[2] Companies House Search:")
    try:
        # Try to extract company name from domain
        domain_word = site.split('.')[0]
        ch_data = search_companies_house(domain_word)
        print(f"  Company Name: '{ch_data.get('company_name', '')}'")
        print(f"  Address: '{ch_data.get('address', '')}'")
        print(f"  Officer: '{ch_data.get('officer', '')}'")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    time.sleep(1)


if __name__ == "__main__":
    sites = [
        "arts1.co.uk",
        "onyxcomms.com",
        "verulamwebdesign.co.uk",
        "sunrisesoftware.com"
    ]
    
    for site in sites:
        debug_scrape(site)
