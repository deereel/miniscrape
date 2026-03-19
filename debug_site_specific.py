#!/usr/bin/env python3
"""Debug script to examine specific sites for scraping issues"""

import requests
from bs4 import BeautifulSoup
from fast_scraper import HEADERS
import warnings
warnings.filterwarnings("ignore")

# Sites to debug
test_sites = [
    "https://www.blossomhouseschool.co.uk",
    "https://www.ballyhoo-pr.co.uk", 
    "https://www.argolin.com",
    "https://www.beckprosper.com"
]

for url in test_sites:
    print(f"\n{'='*80}")
    print(f"Debugging: {url}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Get company name candidates
        print("\nCompany Name Candidates:")
        print("--------------------------")
        
        # Open Graph
        og_site_name = soup.find("meta", property="og:site_name")
        if og_site_name and og_site_name.get('content'):
            print(f"  Open Graph Site Name: '{og_site_name['content']}'")
        
        # Open Graph Title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get('content'):
            print(f"  Open Graph Title: '{og_title['content']}'")
        
        # Twitter Card
        twitter_title = soup.find("meta", property="twitter:title") or soup.find("meta", attrs={"name": "twitter:title"})
        if twitter_title and twitter_title.get('content'):
            print(f"  Twitter Title: '{twitter_title['content']}'")
        
        # Title tag
        title_tag = soup.find("title")
        if title_tag:
            print(f"  Title Tag: '{title_tag.get_text(strip=True)}'")
        
        # H1 tags
        h1_tags = soup.find_all("h1")
        if h1_tags:
            for i, h1 in enumerate(h1_tags):
                text = h1.get_text(strip=True)
                if text:
                    print(f"  H1[{i}]: '{text}'")
        
        # Look for company name in common places
        print("\nLooking for Company Name in Text:")
        print("----------------------------------")
        body_text = soup.get_text()
        
        # Look for common company suffixes
        company_suffixes = ["Limited", "Ltd", "PLC", "LLC", "Incorporated", "Inc"]
        found = False
        for suffix in company_suffixes:
            if suffix in body_text:
                idx = body_text.find(suffix)
                start = max(0, idx - 50)
                end = min(len(body_text), idx + 10)
                snippet = body_text[start:end].strip()
                print(f"  Found '{suffix}' in: '{snippet}'")
                found = True
        
        if not found:
            print("  No company suffix found in text")
        
        # Look for address
        print("\nLooking for Address:")
        print("---------------------")
        
        # Look for common address patterns
        import re
        # UK postcodes
        postcode_matches = list(re.finditer(r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}", body_text))
        if postcode_matches:
            for match in postcode_matches:
                idx = match.start()
                start = max(0, idx - 100)
                end = min(len(body_text), idx + 50)
                snippet = body_text[start:end].strip()
                print(f"  Postcode '{match.group(0)}' found in: '{snippet}'")
        
        # UK addresses without postcode
        address_patterns = [
            r"[\d]{1,4}\s+[A-Za-z\s]{2,50}(?:Street|Road|Rd|St|Avenue|Ave|Drive|Dr|Court|Crescent|Close)",
            r"[A-Z][a-zA-Z\s]+(?:County|City|Town|Village)"
        ]
        
        for pattern in address_patterns:
            matches = list(re.finditer(pattern, body_text))
            if matches:
                for match in matches[:3]:  # Show first 3
                    print(f"  Address pattern '{match.group(0)}' found")
        
        # Look for officers
        print("\nLooking for Officers:")
        print("----------------------")
        
        officer_roles = ["CEO", "Managing Director", "Founder", "Owner", "Director"]
        for role in officer_roles:
            role_pattern = re.compile(rf"{role}\s*[:\s]+([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']+){1,2})", re.IGNORECASE)
            matches = list(role_pattern.finditer(body_text))
            if matches:
                for match in matches:
                    print(f"  {role}: '{match.group(1)}'")
        
        # Write HTML to debug file
        filename = url.split('//')[-1].replace('/', '_').replace('.', '_') + '.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        print(traceback.format_exc())
