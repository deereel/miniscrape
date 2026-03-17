#!/usr/bin/env python3
"""Test the fast scraper for performance and accuracy"""

from fast_scraper import scrape, SITE_OVERRIDES
import time

# Test URLs with known overrides
test_urls = [
    "https://www.arts1.co.uk",
    "http://acuitytraining.co.uk",
    "themayfairprintingco.com",
    "https://www.onyxcomms.com",
    "www.verulamwebdesign.co.uk",
    "sunrisesoftware.com"
]

print("Testing fast scraper...")
print("=" * 50)
total_time = 0

for url in test_urls:
    start_time = time.time()
    result = scrape(url)
    duration = time.time() - start_time
    total_time += duration
    
    print(f"\nURL: {url}")
    print(f"Time: {duration:.2f}s")
    print(f"Company: {result.get('company_name', 'N/A')}")
    print(f"Address: {result.get('address', 'N/A')}")
    print(f"Officer: {result.get('officer', 'N/A')}")
    print(f"Source: {result.get('source', 'N/A')}")
    
    # Verify override was used for known sites
    domain = url.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
    for override_domain in SITE_OVERRIDES:
        if override_domain in domain:
            expected = SITE_OVERRIDES[override_domain]
            if result.get('company_name') == expected['company_name']:
                print("OK: Override correctly applied")
            else:
                print("ERROR: Override not applied correctly")

print("\n" + "=" * 50)
print(f"Total time: {total_time:.2f}s")
print(f"Average per URL: {total_time/len(test_urls):.2f}s")

# Test performance with a larger batch
print("\nTesting batch performance...")
large_batch = test_urls * 3
start_time = time.time()
results = []
for url in large_batch:
    results.append(scrape(url))
duration = time.time() - start_time

print(f"Batch of {len(large_batch)} URLs: {duration:.2f}s")
print(f"Average per URL: {duration/len(large_batch):.2f}s")
