#!/usr/bin/env python3
"""Test the manual override for acuitytraining.co.uk"""

from scraper import scrape

# Test with various formats of the URL
test_urls = [
    "https://acuitytraining.co.uk",
    "http://acuitytraining.co.uk",
    "acuitytraining.co.uk",
    "www.acuitytraining.co.uk",
]

for url in test_urls:
    print(f"\nTesting URL: {url}")
    result = scrape(url)
    print(f"  Company name: {result.get('company_name')}")
    print(f"  Address: {result.get('address')}")
    print(f"  Officer: {result.get('officer')}")
    print(f"  Source: {result.get('source')}")
