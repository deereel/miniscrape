#!/usr/bin/env python3
from scraper import scrape
import time
import sys

def debug_scrape():
    url = 'https://acuitytraining.co.uk'
    print(f'Testing: {url}', file=sys.stderr)
    start_time = time.time()
    
    try:
        result = scrape(url)
        end_time = time.time()
        print(f'Scraping took: {end_time - start_time:.2f} seconds', file=sys.stderr)
        print(f'Result: {result}', file=sys.stderr)
        
        # Check for errors
        if not result.get('company_name') or 'ERROR' in result.get('company_name', ''):
            print('❌ Company name not found or contains error', file=sys.stderr)
        
        if not result.get('address'):
            print('❌ Address not found', file=sys.stderr)
            
        if not result.get('officer'):
            print('❌ Officer not found', file=sys.stderr)
            
        print('✅ Scraping completed', file=sys.stderr)
        
    except Exception as e:
        print(f'❌ Error: {e}', file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)

if __name__ == '__main__':
    debug_scrape()
