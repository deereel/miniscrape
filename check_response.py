#!/usr/bin/env python3
"""Check the actual HTML response to see what's being received"""

import requests
from scraper import HEADERS


def check_response(url):
    """Print raw response for debugging"""
    print(f"\n{'='*50}")
    print(f"Checking: {url}")
    print(f"{'='*50}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Content Length: {len(response.text)} bytes")
        print()
        
        # Print first 500 characters with encoding handling
        print("First 500 characters of response:")
        print("-" * 50)
        content = response.content.decode('utf-8', errors='replace')
        print(content[:500])
        print("-" * 50)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_response("https://www.arts1.co.uk")
    check_response("https://www.onyxcomms.com")
    check_response("https://www.verulamwebdesign.co.uk")
    check_response("https://www.sunrisesoftware.com")
