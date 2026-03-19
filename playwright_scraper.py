#!/usr/bin/env python3
"""
Fast Playwright-based scraper for JavaScript-rendered pages
Much faster than Selenium - typically 2-3x quicker
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')


def get_js_rendered_content(url, timeout=15000):
    """
    Get JavaScript-rendered content from a URL using Playwright.
    
    Args:
        url: The URL to fetch
        timeout: Page load timeout in milliseconds (default 15s)
    
    Returns:
        BeautifulSoup object of the rendered HTML, or None on failure
    """
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-extensions',
                    '--disable-logging',
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            page.set_default_timeout(timeout)
            
            # Wait for network idle after load (but don't wait forever)
            page.goto(url, wait_until='networkidle', timeout=timeout)
            
            # Small wait for any remaining JS
            page.wait_for_timeout(500)
            
            html = page.content()
            browser.close()
            
            return BeautifulSoup(html, 'lxml')
            
        except Exception as e:
            try:
                browser.close()
            except:
                pass
            if 'timeout' not in str(e).lower():
                print(f"  Playwright error for {url}: {e}")
            return None


def scrape_with_playwright(url):
    """
    Scrape company information from a JavaScript-rendered website using Playwright.
    """
    soup = get_js_rendered_content(url)
    if not soup:
        return {"company_name": "", "address": "", "officer": "", "registered_name": "", "source": url}
    
    from scraper import _extract_company_name, _extract_address, _extract_person_name, _extract_registered_name
    
    result = {
        "company_name": _extract_company_name(soup),
        "address": "",
        "officer": "",
        "registered_name": _extract_registered_name(soup),
        "source": url
    }
    
    # Get address/officer from main page text
    if not result["address"] or not result["officer"]:
        text = soup.get_text(" ", strip=True)
        if not result["address"]:
            result["address"] = _extract_address(text)
        if not result["officer"]:
            result["officer"] = _extract_person_name(text)
            
    return result


if __name__ == "__main__":
    # Test the Playwright scraper
    import time
    
    test_urls = [
        "https://www.arts1.co.uk",
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        
        start = time.time()
        try:
            result = scrape_with_playwright(url)
            elapsed = time.time() - start
            print(f"Time: {elapsed:.1f}s")
            print(f"Company Name: '{result['company_name']}'")
            addr = result['address']
            print(f"Address: '{addr[:80]}...'" if len(addr) > 80 else f"Address: '{addr}'")
            print(f"Officer: '{result['officer']}'")
            print(f"Registered Name: '{result['registered_name']}'")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
