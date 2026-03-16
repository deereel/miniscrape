#!/usr/bin/env python3
"""Selenium-based scraper for JavaScript-rendered pages"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup


def get_js_rendered_content(url, timeout=10, headless=True):
    """
    Get JavaScript-rendered content from a URL using Selenium.
    
    Returns:
        BeautifulSoup object of the rendered HTML, or None on failure
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        
        # Wait for JavaScript to load
        time.sleep(3)
        
        # Scroll to bottom to trigger any lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        html = driver.page_source
        driver.quit()
        
        return BeautifulSoup(html, 'lxml')
        
    except Exception as e:
        print(f"  Selenium error for {url}: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        return None


def scrape_with_selenium(url):
    """
    Scrape company information from a JavaScript-rendered website using Selenium.
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
    
    # Check if we got basic info, if not, try other pages
    subpages = ["/about", "/about-us", "/contact", "/contact-us", "/team", "/our-team", "/leadership"]
    
    for subpage in subpages:
        if result["company_name"] and result["address"] and result["officer"]:
            break
            
        subpage_url = url.rstrip('/') + subpage
        sub_soup = get_js_rendered_content(subpage_url, timeout=8)
        if sub_soup:
            if not result["company_name"]:
                result["company_name"] = _extract_company_name(sub_soup)
                
            if not result["address"]:
                text = sub_soup.get_text(" ", strip=True)
                result["address"] = _extract_address(text)
                
            if not result["officer"]:
                text = sub_soup.get_text(" ", strip=True)
                result["officer"] = _extract_person_name(text)
                
            if not result["registered_name"]:
                result["registered_name"] = _extract_registered_name(sub_soup)
                
    return result


if __name__ == "__main__":
    # Test the Selenium scraper
    test_urls = [
        "https://www.arts1.co.uk",
        "https://www.onyxcomms.com",
        "https://www.verulamwebdesign.co.uk",
        "https://www.sunrisesoftware.com"
    ]
    
    for url in test_urls:
        print(f"\n{'='*50}")
        print(f"Testing: {url}")
        print(f"{'='*50}")
        
        try:
            result = scrape_with_selenium(url)
            print(f"Company Name: '{result['company_name']}'")
            print(f"Address: '{result['address']}'")
            print(f"Officer: '{result['officer']}'")
            print(f"Registered Name: '{result['registered_name']}'")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            print(traceback.format_exc())
