#!/usr/bin/env python3
"""Fast Selenium-based scraper for JavaScript-rendered pages - optimized for speed"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup


def get_js_rendered_content(url, timeout=8, headless=True):
    """
    Get JavaScript-rendered content from a URL using Selenium.
    OPTIMIZED for speed - reduced timeouts and faster page loads.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')
    # Faster page loads
    chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Speed up networking
    prefs = {
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_settings.popups': 0,
        'download.prompt_for_download': False,
    }
    chrome_options.add_experimental_option('prefs', prefs)

    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        driver.set_page_load_timeout(timeout)
        driver.get(url)

        # Minimal wait for DOM ready only (not full load)
        WebDriverWait(driver, min(timeout, 5)).until(
            lambda d: d.execute_script('return document.readyState') in ['complete', 'interactive']
        )
        
        # Small delay for initial JS render
        time.sleep(0.5)

        html = driver.page_source
        return BeautifulSoup(html, 'lxml')

    except Exception as e:
        # Don't print error for timeout - too noisy
        if 'timeout' not in str(e).lower():
            print(f"  Selenium error for {url}: {e}")
        return None

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def scrape_with_selenium(url):
    """
    Scrape company information from a JavaScript-rendered website using Selenium.
    OPTIMIZED: Only fetches homepage, skips slow subpage fetching.
    """
    soup = get_js_rendered_content(url, timeout=8)
    if not soup:
        return {"company_name": "", "address": "", "officer": "", "registered_name": "", "source": url}
    
    from scraper import _extract_company_name, _extract_address, _extract_person_name, _extract_registered_name
    
    # Extract from main page only - much faster
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
