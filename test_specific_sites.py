#!/usr/bin/env python3
"""Test script to verify scraping of specific sites"""

from scraper import scrape
import time


def test_specific_sites():
    """Test scraping of specific websites"""
    sites = [
        "arts1.co.uk",
        "markjohnstonracing.com", 
        "onyxcomms.com",
        "verulamwebdesign.co.uk",
        "sunrisesoftware.com"
    ]
    
    print("=" * 50)
    print("Testing Specific Sites")
    print("=" * 50)
    
    results = []
    
    for site in sites:
        print(f"\nTesting: {site}")
        url = f"https://www.{site}" if not site.startswith("http") else site
        
        try:
            result = scrape(url)
            results.append(result)
            
            print(f"  Company Name: {result.get('company_name', 'N/A')}")
            print(f"  Address: {result.get('address', 'N/A')}")
            print(f"  Officer: {result.get('officer', 'N/A')}")
            print(f"  Source: {result.get('source', 'N/A')}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        # Add delay to avoid rate limiting
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)
    
    return results


if __name__ == "__main__":
    test_specific_sites()
