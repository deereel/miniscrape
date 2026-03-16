#!/usr/bin/env python3
"""Test the main.py file directly with test inputs (no cleanup)"""

import subprocess
import sys


def test_main():
    """Test the main application with sample inputs"""
    
    print("=" * 50)
    print("Testing main.py application")
    print("=" * 50)
    
    # Create a temporary input file with test URLs
    test_urls = [
        "https://www.arts1.co.uk",
        "https://www.onyxcomms.com", 
        "https://www.verulamwebdesign.co.uk",
        "https://www.sunrisesoftware.com"
    ]
    
    try:
        from main import run_queries
        run_queries(test_urls)
        
        print("\nSuccess! Results saved to results.xlsx")
        
        # Verify the results file
        import pandas as pd
        df = pd.read_excel('results.xlsx')
        print(f"\nResults file contains {len(df)} rows")
        print("\nFirst 5 rows:")
        print(df.head())
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        print(traceback.format_exc())
        
    print()
    print("=" * 50)
    print("Testing completed!")
    print("=" * 50)


if __name__ == "__main__":
    test_main()
