#!/usr/bin/env python3
from main import run_queries
from scraper import scrape
import os

# Cleanup previous files
if os.path.exists('results.csv'):
    os.remove('results.csv')

print("=== MiniScrape Test ===")

# Test scrape function directly
print("\n1. Testing Scrape Function:")
print("-" * 50)
url = "https://www.arts1.co.uk"
result = scrape(url)
for key, value in result.items():
    print(f"{key}: {value}")

# Test run_queries with CSV output
print("\n2. Testing run_queries Function:")
print("-" * 50)
urls = ["https://www.arts1.co.uk", "https://www.onyxcomms.com"]
run_queries(urls)

# Verify results
print("\n3. Verifying Results File:")
print("-" * 50)
if os.path.exists('results.csv'):
    print("OK: results.csv created successfully")
    
    import pandas as pd
    df = pd.read_csv('results.csv')
    print(f"   Records: {len(df)}")
    print(f"   First record: {df.iloc[0]['Company Full Name']}")
else:
    print("ERROR: No results file created!")

print("\n=== Test Completed ===")
