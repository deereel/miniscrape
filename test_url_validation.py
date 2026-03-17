#!/usr/bin/env python3
"""Test URL validation improvements"""

from scraper import scrape

# Test URLs without protocols
test_urls = [
    "amazon.co.uk",
    "www.google.com",
    "stackoverflow.com",
    "github.io",
    "bbc.co.uk/news",
    "example.org/about-us",
    "twitter.com"
]

print("Testing URL validation:")
print("-" * 50)

for url in test_urls:
    print(f"\nTesting: {url}")
    result = scrape(url)
    print(f"  Is URL: {'Yes' if result.get('source') else 'No'}")
    print(f"  Company name: {result.get('company_name')}")
    print(f"  Source: {result.get('source')}")
