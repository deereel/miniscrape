#!/usr/bin/env python3
"""Test raw requests without BS4 parsing"""

import requests
import sys
from scraper import HEADERS


def test_raw_request(url):
    """Test raw request with detailed debugging"""
    print(f"\n{'='*50}")
    print(f"Testing: {url}")
    print(f"{'='*50}")
    
    try:
        # Test request
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Content Length: {len(response.content)} bytes")
        print(f"Encoding: {response.encoding}")
        
        # Try to decode and print a small part
        print()
        print("First 200 bytes:")
        print("-" * 50)
        # Skip print to avoid encoding issues
        print("[Binary data - not printed to avoid encoding errors]")
        
        return response.content
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return None


if __name__ == "__main__":
    sites = [
        "https://www.arts1.co.uk",
        "https://www.onyxcomms.com", 
        "https://www.verulamwebdesign.co.uk",
        "https://www.sunrisesoftware.com"
    ]
    
    for url in sites:
        content = test_raw_request(url)
        if content:
            # Write to file
            filename = url.replace('https://www.', '').replace('.', '_') + '_raw.bin'
            with open(filename, 'wb') as f:
                f.write(content)
            print(f"\n✅ Saved to {filename}")
    
    print("\n" + "="*50)
    print("Testing completed!")
    print("="*50)
