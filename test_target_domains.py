#!/usr/bin/env python3
"""Test script to verify scraping of target domains mentioned in recommendations"""

from scraper import scrape
from fast_scraper import scrape as fast_scrape
import time

def test_target_domains():
    """Test scraping of specific domains mentioned in recommendations"""
    sites = [
        "drewry.co.uk",
        "weareyellowball.com", 
        # Adding a few more to test
        "arts1.co.uk",
        "markjohnstonracing.com",
        "onyxcomms.com"
    ]
    
    print("=" * 60)
    print("Testing Target Domains (from recommendations)")
    print("=" * 60)
    
    results = []
    
    for site in sites:
        print(f"\nTesting: {site}")
        url = f"https://www.{site}" if not site.startswith("http") else site
        
        try:
            print("  Regular scraper:")
            result = scrape(url)
            results.append(("regular", site, result))
            
            print(f"    Company Name: {result.get('company_name', 'N/A')}")
            print(f"    Address: {result.get('address', 'N/A')}")
            print(f"    Officer: {result.get('officer', 'N/A')}")
            print(f"    Source: {result.get('source', 'N/A')}")
            print(f"    Confidence: {result.get('confidence', {})}")
            
        except Exception as e:
            print(f"    Error: {e}")
        
        # Add delay to avoid rate limiting
        time.sleep(1)
        
        try:
            print("  Fast scraper:")
            result_fast = fast_scrape(url)
            results.append(("fast", site, result_fast))
            
            print(f"    Company Name: {result_fast.get('company_name', 'N/A')}")
            print(f"    Address: {result_fast.get('address', 'N/A')}")
            print(f"    Officer: {result_fast.get('officer', 'N/A')}")
            print(f"    Source: {result_fast.get('source', 'N/A')}")
            print(f"    Confidence: {result_fast.get('confidence', {})}")
            
        except Exception as e:
            print(f"    Error: {e}")
        
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    test_target_domains()