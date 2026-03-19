#!/usr/bin/env python3
"""Debug script to check AI address extraction"""

from fast_scraper import _get, HEADERS
from ai_agents import AIAddressExtractionAgent
import warnings
warnings.filterwarnings("ignore")

# Sites to test
test_sites = [
    "https://www.blossomhouseschool.co.uk",
    "https://www.ballyhoo-pr.co.uk", 
    "https://www.argolin.com",
    "https://www.beckprosper.com"
]

print("=" * 80)
print("AI Address Extraction Debug")
print("=" * 80)
print()

for url in test_sites:
    print(f"{'='*60}")
    print(f"Site: {url}")
    print(f"{'='*60}")
    
    try:
        response = _get(url)
        if response:
            # Extract text for AI
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            for tag in soup(["script", "style"]):
                tag.decompose()
            text = soup.get_text(" ", strip=True)
            
            # Limit text size for testing
            if len(text) > 3000:
                text = text[:3000]
            
            print(f"\nText length: {len(text)} characters")
            print(f"\nFirst 500 characters:")
            print(text[:500])
            print("\n" + "-"*50)
            
            # Test AI address extraction
            print("AI Address Extraction Result:")
            try:
                address = AIAddressExtractionAgent.extract_address(text)
                if address:
                    print(f"  '{address}'")
                else:
                    print("  No address extracted")
            except Exception as e:
                print(f"  Error: {e}")
                import traceback
                print(traceback.format_exc())
            
            # Try regex extraction directly
            print("\nRegex Extraction (without AI):")
            import re
            uk_postcode = re.search(r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}", text)
            if uk_postcode:
                print(f"  Postcode found: '{uk_postcode.group(0)}'")
                snippet = text[max(0, uk_postcode.start() - 200):uk_postcode.end()]
                snippet = re.sub(r"\s+", " ", snippet)
                print(f"  Snippet: '{snippet}'")
            else:
                print("  No postcode found")
                
            print()
            
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        print()

print("=" * 80)
print("Debug Completed")
print("=" * 80)
