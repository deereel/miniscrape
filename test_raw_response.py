#!/usr/bin/env python3
"""Test raw response from problematic websites"""

import requests
import sys

# Set default encoding
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
}

urls = [
    "https://heritagelincolnshire.org",
    "https://leadingresolutions.com",
    "https://pbdesign.co.uk",
    "https://icon-eng.co.uk",
    "https://princethorpe.co.uk",
    "https://adkinsresearchgroup.com",
    "https://glinwellplc.com",
    "https://akitasystems.co.uk"
]

for url in urls:
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print('='*60)
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Headers: {dict(r.headers)}")
        
        if 'content-type' in r.headers:
            print(f"Content-Type: {r.headers['content-type']}")
        
        if 'content-encoding' in r.headers:
            print(f"Content-Encoding: {r.headers['content-encoding']}")
        
        # Try to decode with different encodings
        print("\n=== Decoding Attempts ===")
        
        # Try UTF-8
        try:
            content = r.text
            print(f"UTF-8: Success ({len(content)} chars)")
            print(f"Sample: {repr(content[:500])}")
        except Exception as e:
            print(f"UTF-8: Error - {e}")
        
        # Try Latin-1
        try:
            content = r.content.decode('latin-1')
            print(f"Latin-1: Success ({len(content)} chars)")
            print(f"Sample: {repr(content[:500])}")
        except Exception as e:
            print(f"Latin-1: Error - {e}")
        
        # Try CP1252
        try:
            content = r.content.decode('cp1252')
            print(f"CP1252: Success ({len(content)} chars)")
            print(f"Sample: {repr(content[:500])}")
        except Exception as e:
            print(f"CP1252: Error - {e}")
            
    except Exception as e:
        print(f"Error: {e}")
