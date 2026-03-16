#!/usr/bin/env python3
"""Debug the website scraper to see why it's not finding data"""

import requests
from bs4 import BeautifulSoup
from scraper import HEADERS, _extract_company_name, _extract_address, _extract_person_name


def debug_site(url):
    """Debug individual site scraping"""
    print(f"\n{'='*50}")
    print(f"Debugging: {url}")
    print(f"{'='*50}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Print title for debugging
        print(f"Title: {soup.title.string.strip() if soup.title else 'No title'}")
        
        # Extract and print meta tags
        print(f"\nMeta Tags:")
        for tag in soup.find_all('meta', {'property': True}):
            print(f"  {tag['property']}: {tag.get('content', 'No content')}")
        
        # Test company name extraction
        company_name = _extract_company_name(soup)
        print(f"\nExtracted Company Name: '{company_name}'")
        
        # Test address extraction
        page_text = soup.get_text(" ", strip=True)
        print(f"\nPage Text Length: {len(page_text)} characters")
        address = _extract_address(page_text)
        print(f"Extracted Address: '{address}'")
        
        # Test person name extraction
        officer = _extract_person_name(page_text)
        print(f"Extracted Officer: '{officer}'")
        
        # Print footer text
        print(f"\nFooter:")
        footer = soup.find('footer')
        if footer:
            print(footer.get_text(" ", strip=True)[:200])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    debug_site("https://www.arts1.co.uk")
    debug_site("https://www.onyxcomms.com")
    debug_site("https://www.verulamwebdesign.co.uk")
    debug_site("https://www.sunrisesoftware.com")
