#!/usr/bin/env python3
"""Test the improved fast scraper on problematic URLs"""

from fast_scraper import scrape
import time

# URLs that were giving wrong results
problematic_urls = [
    "https://heritagelincolnshire.org",
    "https://leadingresolutions.com", 
    "https://pbdesign.co.uk",
    "https://icon-eng.co.uk",
    "https://princethorpe.co.uk",
    "https://adkinsresearchgroup.com",
    "https://glinwellplc.com",
    "https://akitasystems.co.uk"
]

print("Testing improved fast scraper on problematic URLs")
print("=" * 60)

for url in problematic_urls:
    print(f"\nTesting: {url}")
    start_time = time.time()
    result = scrape(url)
    duration = time.time() - start_time
    
    print(f"  Time: {duration:.2f}s")
    print(f"  Company: {result.get('company_name', 'N/A')}")
    address = result.get('address', 'N/A')
    if isinstance(address, str):
        # Replace non-ASCII characters with safe alternatives
        address = address.encode('ascii', 'replace').decode('ascii')
    print(f"  Address: {address}")
    print(f"  Officer: {result.get('officer', 'N/A')}")
    print(f"  Source: {result.get('source', 'N/A')}")
    
    # Check if results are reasonable
    if not result.get('company_name') or result['company_name'] == url:
        print("  WARNING: Company name may be incorrect")
    if result.get('address') and len(result['address']) > 500:
        print("  WARNING: Address may be too long")
    if len(str(result.get('officer'))) > 100:
        print("  WARNING: Officer name may be incorrect")

print("\n" + "=" * 60)
print("Test completed!")
