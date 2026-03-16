#!/usr/bin/env python3
"""Test specific websites with enhanced debugging and manual data extraction"""

import requests
from bs4 import BeautifulSoup
from scraper import HEADERS


def scrape_site_specific(url, site_name):
    """Attempt to scrape specific site with enhanced methods"""
    print(f"\n{'='*50}")
    print(f"Scraping: {url} ({site_name})")
    print(f"{'='*50}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Try to get encoding correctly
        try:
            content = response.content.decode('utf-8')
        except:
            try:
                content = response.content.decode('latin-1')
            except:
                content = response.content.decode('utf-8', errors='replace')
        
        soup = BeautifulSoup(content, 'lxml')
        
        # Find all links that might point to contact or about pages
        print("\n[Links]")
        important_links = []
        for tag in ['contact', 'about', 'about-us', 'team', 'our-team', 'people', 'staff']:
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                if any(keyword in href for keyword in [tag, 'about', 'contact', 'team', 'people']):
                    if href not in important_links:
                        important_links.append(href)
                        print(f"  {link.get_text(strip=True)} -> {href}")
        
        # Extract all text from body for analysis
        body_text = soup.find('body').get_text(" ", strip=True) if soup.find('body') else ""
        
        print("\n[Text Snippets]")
        print("-" * 20)
        
        # Look for patterns like company name, address, director, manager
        patterns = ['limited', 'ltd', 'inc', 'llc', 'director', 'manager', 'founder',
                   'street', 'road', 'avenue', 'building', 'suite', 'floor']
        
        for pattern in patterns:
            matches = [i for i in range(len(body_text)) if body_text.lower().find(pattern, i) != -1]
            if matches:
                start = max(0, matches[0] - 20)
                end = min(len(body_text), matches[0] + 50)
                snippet = repr(body_text[start:end])
                print(f"  {pattern}: {snippet}")
        
        # Look for h1-h3 tags
        print("\n[Headings]")
        for tag in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if len(text) > 1 and len(text) < 100:
                    print(f"  {tag}: '{text}'")
        
        return content
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return None


if __name__ == "__main__":
    sites = [
        ("https://www.arts1.co.uk", "Arts1"),
        ("https://www.onyxcomms.com", "Onyx Comms"),
        ("https://www.verulamwebdesign.co.uk", "Verulam Web Design"),
        ("https://www.sunrisesoftware.com", "Sunrise Software")
    ]
    
    responses = []
    for url, site_name in sites:
        content = scrape_site_specific(url, site_name)
        if content:
            with open(f"{site_name.lower().replace(' ', '_')}_analysis.html", 'w', encoding='utf-8', errors='replace') as f:
                f.write(content)
            responses.append(content)
    
    print("\n" + "="*50)
    print("Scraping completed!")
    print("="*50)
