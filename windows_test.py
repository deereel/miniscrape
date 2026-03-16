#!/usr/bin/env python3
"""Test script that can be run from Windows batch file"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== MiniScrape Windows Test ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Test scraper
print("\n1. Testing scraper module:")
try:
    from scraper import scrape
    result = scrape('https://www.arts1.co.uk')
    print(f"   Company: {result['company_name']}")
    print(f"   Address: {result['address']}")
    print(f"   Officer: {result['officer']}")
    print(f"   Source: {result['source']}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    print(traceback.format_exc())

# Test main module
print("\n2. Testing main module:")
try:
    from main import load_queries, run_queries
    
    # Create temporary file
    temp_file = 'test_urls.txt'
    with open(temp_file, 'w') as f:
        f.write("https://www.arts1.co.uk\n")
        f.write("https://www.onyxcomms.com\n")
    
    # Load and run
    urls = load_queries(temp_file)
    print(f"   Loaded {len(urls)} URLs")
    run_queries(urls)
    
    # Verify results
    if os.path.exists('results.csv'):
        print("   OK: results.csv created")
        import pandas as pd
        df = pd.read_csv('results.csv')
        print(f"   Records: {len(df)}")
        for i, row in df.iterrows():
            print(f"   {i+1}. {row['Company Full Name']}")
    
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== Test Completed ===")
