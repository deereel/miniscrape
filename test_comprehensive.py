#!/usr/bin/env python3
"""Comprehensive system test script"""

import subprocess
import sys

def run_test(test_name, command):
    print(f"\n{'='*50}")
    print(f"Test: {test_name}")
    print('-' * 50)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            print(result.stdout.strip())
        
        if result.stderr:
            print("\nERROR: Error output:")
            print(result.stderr.strip())
        
        if result.returncode != 0:
            print(f"\nERROR: Test failed with exit code: {result.returncode}")
            return False
        else:
            print(f"\nOK: Test passed")
            return True
    except subprocess.TimeoutExpired:
        print(f"\nERROR: Test timed out")
        return False
    except Exception as e:
        print(f"\nERROR: Error: {e}")
        return False

def main():
    print("=== Comprehensive System Test ===")
    
    tests = [
        ("Web Application Functionality", ['python', 'test_web_app_functionality.py']),
        ("Validation Schema", ['python', 'test_validation_demo.py']),
        ("Scraping Functionality", ['python', 'test_scrape.py'])
    ]
    
    passed = 0
    failed = 0
    
    for test_name, command in tests:
        if run_test(test_name, command):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"\nTest Results Summary:")
    print(f"OK: Passed: {passed}")
    print(f"ERROR: Failed: {failed}")
    
    if failed == 0:
        print("\nOK: All tests passed! The application is working correctly.")
    else:
        print("\nERROR: Some tests failed. Please check the output for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
