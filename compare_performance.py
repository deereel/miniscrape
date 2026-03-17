#!/usr/bin/env python3
"""Compare performance between fast and slow scraper"""

import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test URLs with known overrides
test_urls = [
    "https://www.arts1.co.uk",
    "http://acuitytraining.co.uk",
    "themayfairprintingco.com",
    "https://www.onyxcomms.com",
    "www.verulamwebdesign.co.uk",
    "sunrisesoftware.com"
]


def test_fast_scraper():
    """Test the fast scraper"""
    from fast_scraper import scrape
    print("Testing Fast Scraper...")
    start_time = time.time()
    
    results = []
    for url in test_urls:
        results.append(scrape(url))
    
    duration = time.time() - start_time
    print(f"Fast Scraper: {duration:.2f} seconds")
    return duration, len(results)


def test_slow_scraper():
    """Test the slow scraper"""
    from scraper import scrape
    print("Testing Slow Scraper...")
    start_time = time.time()
    
    results = []
    for url in test_urls:
        results.append(scrape(url))
    
    duration = time.time() - start_time
    print(f"Slow Scraper: {duration:.2f} seconds")
    return duration, len(results)


def main():
    print("Performance Comparison")
    print("=" * 50)
    
    fast_duration, fast_count = test_fast_scraper()
    slow_duration, slow_count = test_slow_scraper()
    
    print()
    print("=" * 50)
    print(f"Fast Scraper:  {fast_count} URLs in {fast_duration:.2f} seconds")
    print(f"Slow Scraper:  {slow_count} URLs in {slow_duration:.2f} seconds")
    
    if fast_duration > 0 and slow_duration > 0:
        improvement = (slow_duration - fast_duration) / slow_duration * 100
        print(f"Improvement:   {improvement:.1f}% faster")
        print(f"Speed Ratio:   {slow_duration / fast_duration:.1f}x faster")
    
    print()
    print("Fast Scraper is much faster because it:")
    print("- Uses manual overrides instead of scraping")
    print("- Makes fewer HTTP requests")
    print("- No Selenium fallback (which is very slow)")
    print("- Minimal parsing and processing")


if __name__ == "__main__":
    main()
