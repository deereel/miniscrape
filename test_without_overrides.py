#!/usr/bin/env python3
"""Test scraper without manual overrides to verify Selenium integration"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import scrape_website, scrape
from site_overrides import SITE_OVERRIDES


def test_without_overrides():
    """Test the scraper without manual overrides"""
    
    # Temporarily disable overrides by emptying the dictionary
    original_overrides = SITE_OVERRIDES.copy()
    SITE_OVERRIDES.clear()
    
    try:
        print("Testing without manual overrides:")
        print("=" * 50)
        
        test_urls = [
            "https://www.arts1.co.uk",
            "https://www.onyxcomms.com",
            "https://www.verulamwebdesign.co.uk",
            "https://www.sunrisesoftware.com"
        ]
        
        for url in test_urls:
            print(f"\n{'='*40}")
            print(f"Testing: {url}")
            print(f"{'='*40}")
            
            # First test website scraping
            print("\n[Website Scraping]")
            result = scrape_website(url)
            if result:
                print(f"Company Name: '{result['company_name']}'")
                print(f"Address: '{result['address']}'")
                print(f"Officer: '{result['officer']}'")
                print(f"Registered Name: '{result['registered_name']}'")
                print(f"Source: '{result['source']}'")
            else:
                print("No data extracted from website")
            
            # Then test full scrape (including Companies House)
            print("\n[Full Scrape]")
            full_result = scrape(url)
            if full_result:
                print(f"Company Name: '{full_result['company_name']}'")
                print(f"Address: '{full_result['address']}'")
                print(f"Officer: '{full_result['officer']}'")
                print(f"Source: '{full_result['source']}'")
            else:
                print("Full scrape failed")
                
    finally:
        # Restore original overrides
        SITE_OVERRIDES.update(original_overrides)
        print("\n" + "=" * 50)
        print("Original overrides restored")
        print("=" * 50)


if __name__ == "__main__":
    test_without_overrides()
