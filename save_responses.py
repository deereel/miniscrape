#!/usr/bin/env python3
"""Save responses to files for manual inspection"""

import requests
from scraper import HEADERS


def save_response(url, filename):
    """Save URL response to file"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Write to file with UTF-8 encoding
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.content.decode('utf-8', errors='replace'))
            
        print(f"Saved response from {url} to {filename}")
        
    except Exception as e:
        print(f"Error saving {url}: {e}")


if __name__ == "__main__":
    sites = [
        ("https://www.arts1.co.uk", "arts1_response.html"),
        ("https://www.onyxcomms.com", "onyxcomms_response.html"),
        ("https://www.verulamwebdesign.co.uk", "verulam_response.html"),
        ("https://www.sunrisesoftware.com", "sunrise_response.html")
    ]
    
    for url, filename in sites:
        save_response(url, filename)
    
    print("\nAll responses saved successfully!")
