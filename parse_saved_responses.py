#!/usr/bin/env python3
"""Parse saved HTML responses without printing problematic characters"""

from bs4 import BeautifulSoup
from scraper import _extract_company_name, _extract_address, _extract_person_name
import os


def parse_response(filename):
    """Parse HTML file and extract information"""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'lxml')
        
        company_name = _extract_company_name(soup)
        page_text = soup.get_text(" ", strip=True)
        address = _extract_address(page_text)
        officer = _extract_person_name(page_text)
        
        print(f"\n{'='*50}")
        print(f"File: {filename}")
        print(f"{'='*50}")
        print(f"Company Name: '{company_name}'")
        print(f"Address: '{address}'")
        print(f"Officer: '{officer}'")
        
        # Try to extract from meta tags
        print()
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name:
            print(f"og:site_name: '{og_site_name.get('content', '')}'")
            
        og_title = soup.find('meta', property='og:title')
        if og_title:
            print(f"og:title: '{og_title.get('content', '')}'")
            
        title_tag = soup.find('title')
        if title_tag:
            print(f"Title: '{title_tag.string.strip()}'")
            
    except Exception as e:
        print(f"\nError parsing {filename}: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    files = [
        "arts1_response.html",
        "onyxcomms_response.html", 
        "verulam_response.html",
        "sunrise_response.html"
    ]
    
    for filename in files:
        parse_response(filename)
