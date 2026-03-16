#!/usr/bin/env python3
"""Test script to verify name parsing for specific sites"""

from scraper import scrape, _parse_person_name
import time


def test_name_parsing_sites():
    """Test name parsing for specific websites"""
    sites = [
        "arts1.co.uk",
        "markjohnstonracing.com", 
        "onyxcomms.com",
        "verulamwebdesign.co.uk",
        "sunrisesoftware.com"
    ]
    
    print("=" * 50)
    print("Testing Name Parsing")
    print("=" * 50)
    
    for site in sites:
        print(f"\nTesting: {site}")
        url = f"https://www.{site}" if not site.startswith("http") else site
        
        try:
            result = scrape(url)
            officer = result.get('officer', '')
            
            print(f"  Raw Officer: {officer}")
            
            if officer:
                parsed = _parse_person_name(officer)
                print(f"  Parsed:")
                print(f"    First: {parsed['first']}")
                print(f"    Last: {parsed['last']}")
                print(f"    Middle: {parsed['middle']}")
                print(f"    Title: {parsed['prefix']}")
                print(f"    Suffix: {parsed['suffix']}")
            
            print(f"  Source: {result.get('source', 'N/A')}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        # Add delay to avoid rate limiting
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    test_name_parsing_sites()
