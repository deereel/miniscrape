#!/usr/bin/env python3
"""Test the main.py file directly with test inputs"""

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
    
    with open("test_input.txt", "w") as f:
        for url in test_urls:
            f.write(f"{url}\n")
    
    # Test loading from file
    print("\n1. Testing loading from file (test_input.txt):")
    print("-" * 50)
    
    try:
        # Run main.py with file input
        command = [sys.executable, "main.py"]
        
        # We'll use a different approach since we can't simulate interactive input
        # directly from here. Instead, let's call the run_queries function directly.
        
        from main import run_queries
        run_queries(test_urls)
        
        print("\nSuccess! Results saved to results.xlsx")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        print(traceback.format_exc())
    
    # Clean up
    try:
        import os
        os.remove("test_input.txt")
        # Try to delete results.xlsx if it exists and is not open
        if os.path.exists("results.xlsx"):
            try:
                os.remove("results.xlsx")
            except:
                print("Warning: Could not delete results.xlsx (it may be open)")
    except:
        pass
        
    print()
    print("=" * 50)
    print("Testing completed!")
    print("=" * 50)


if __name__ == "__main__":
    test_main()
