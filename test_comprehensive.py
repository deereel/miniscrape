#!/usr/bin/env python3
"""Comprehensive test of all scraper improvements"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import scrape
from site_overrides import SITE_OVERRIDES


def test_comprehensive():
    """Test all scraper improvements"""
    
    print("=" * 60)
    print("MINISCRAPE COMPREHENSIVE TEST")
    print("=" * 60)
    
    test_cases = [
        ("https://www.arts1.co.uk", "Arts1 School of Performance", "Rebecca Carrington"),
        ("https://www.onyxcomms.com", "Onyx Media and Communications", "Anne Griffin"),
        ("https://www.verulamwebdesign.co.uk", "Verulam Web Design", "Nigel Minchin"),
        ("https://www.sunrisesoftware.com", "Sunrise Software", "Dean Coleman")
    ]
    
    all_passed = True
    
    for url, expected_name, expected_officer in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing: {url}")
        print(f"{'='*50}")
        
        try:
            result = scrape(url)
            
            print(f"Company Name: '{result['company_name']}'")
            print(f"Address: '{result['address']}'")
            print(f"Officer: '{result['officer']}'")
            print(f"Source: '{result['source']}'")
            
            # Verify results against expected values
            if expected_name and result['company_name']:
                if expected_name.lower() in result['company_name'].lower():
                    print("OK: Company name matches expected")
                else:
                    print(f"ERROR: Company name mismatch: expected '{expected_name}', got '{result['company_name']}'")
                    all_passed = False
                    
            if expected_officer and result['officer']:
                if expected_officer.lower() in result['officer'].lower():
                    print("OK: Officer matches expected")
                else:
                    print(f"ERROR: Officer mismatch: expected '{expected_officer}', got '{result['officer']}'")
                    all_passed = False
                    
        except Exception as e:
            print(f"ERROR: Error scraping {url}: {e}")
            import traceback
            print(traceback.format_exc())
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
    print(f"{'='*60}")
    
    return all_passed


if __name__ == "__main__":
    test_comprehensive()
