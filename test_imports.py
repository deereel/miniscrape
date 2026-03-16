#!/usr/bin/env python3
"""Test script to verify all imports are working"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== MiniScrape Import Test ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Test scraper module
try:
    import scraper
    print("OK: scraper module imported")
    from scraper import scrape
    print("OK: scrape function available")
except Exception as e:
    print(f"ERROR: scraper module: {e}")
    import traceback
    print(traceback.format_exc())

# Test site_overrides
try:
    import site_overrides
    print("OK: site_overrides module imported")
    from site_overrides import SITE_OVERRIDES
    print(f"OK: SITE_OVERRIDES: {len(SITE_OVERRIDES)} entries")
except Exception as e:
    print(f"ERROR: site_overrides: {e}")
    import traceback
    print(traceback.format_exc())

# Test selenium_scraper
try:
    import selenium_scraper
    print("OK: selenium_scraper module imported")
except Exception as e:
    print(f"ERROR: selenium_scraper: {e}")
    import traceback
    print(traceback.format_exc())

# Test main module
try:
    import main
    print("OK: main module imported")
    from main import load_queries, run_queries, main
    print("OK: main functions available")
except Exception as e:
    print(f"ERROR: main module: {e}")
    import traceback
    print(traceback.format_exc())

# Test pandas
try:
    import pandas as pd
    print("OK: pandas module imported")
except Exception as e:
    print(f"ERROR: pandas: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== All imports tested ===")
