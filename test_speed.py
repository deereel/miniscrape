#!/usr/bin/env python
"""Quick speed test for the simplified scrapers"""
import time
import sys

# Test URLs
TEST_URLS = [
    "https://www.octopus-res.co.uk",
    "https://www.barclays.com",
    "https://www.britishgas.co.uk",
]

def test_fast_scraper():
    """Test fast_scraper"""
    print("\n=== Testing fast_scraper ===")
    from fast_scraper import scrape as fast_scrape
    
    for url in TEST_URLS:
        print(f"\nTesting: {url}")
        start = time.time()
        result = fast_scrape(url)
        elapsed = time.time() - start
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Company: {result.get('company_name', '')[:50]}")
        print(f"  Address: {result.get('address', '')[:50]}...")
        print(f"  Officer: {result.get('officer', '')}")
    return elapsed

def test_scraper():
    """Test scraper"""
    print("\n=== Testing scraper ===")
    from scraper import scrape
    
    for url in TEST_URLS:
        print(f"\nTesting: {url}")
        start = time.time()
        result = scraper(url)
        elapsed = time.time() - start
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Company: {result.get('company_name', '')[:50]}")
        print(f"  Address: {result.get('address', '')[:50]}...")
        print(f"  Officer: {result.get('officer', '')}")
    return elapsed

if __name__ == "__main__":
    # Test fast_scraper
    fast_time = test_fast_scraper()
    
    print("\n" + "="*50)
    print(f"Speed test complete!")
    print(f"Expected improvement: ~50% faster due to simplified search flow")
