#!/usr/bin/env python3
"""Test script to run main.py functions directly"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import load_queries, run_queries

# Create temporary input file
temp_file = 'temp_input.txt'
with open(temp_file, 'w') as f:
    f.write("https://www.arts1.co.uk\n")
    f.write("https://www.onyxcomms.com\n")

print("=== MiniScrape Test ===")
print(f"Created temporary file: {temp_file}")

# Test load_queries
print("\n1. Testing load_queries:")
try:
    urls = load_queries(temp_file)
    print(f"   Loaded {len(urls)} URLs:")
    for url in urls:
        print(f"   - {url}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    print(traceback.format_exc())

# Test run_queries
print("\n2. Testing run_queries:")
try:
    run_queries(urls)
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    print(traceback.format_exc())

# Verify results
print("\n3. Verifying results:")
if os.path.exists('results.csv'):
    print("   OK: results.csv created")
    import pandas as pd
    df = pd.read_csv('results.csv')
    print(f"   Records: {len(df)}")
    for i, row in df.iterrows():
        print(f"   {i+1}. {row['Company Full Name']}")
else:
    print("   ERROR: No results file created")

# Cleanup
try:
    os.remove(temp_file)
    print(f"\n4. Cleanup: Removed {temp_file}")
except Exception as e:
    print(f"\n4. Cleanup error: {e}")

print("\n=== Test Completed ===")
