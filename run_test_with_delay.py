#!/usr/bin/env python3
import time
import subprocess

def run_test():
    print("Waiting for Flask server to start...")
    time.sleep(5)
    
    print("\nRunning test...")
    result = subprocess.run(['python', 'test_simple_scrape.py'], capture_output=True, text=True)
    
    print("\n=== Test Output ===")
    print(result.stdout)
    
    if result.stderr:
        print("\n=== Errors ===")
        print(result.stderr)

if __name__ == "__main__":
    run_test()
