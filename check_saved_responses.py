#!/usr/bin/env python3
"""Check saved HTML responses"""

import os


def check_response(filename):
    """Print first 50 lines of HTML file"""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n{'='*50}")
        print(f"File: {filename}")
        print(f"{'='*50}")
        
        # Print title tag content
        start_title = content.find('<title')
        if start_title != -1:
            start_title = content.find('>', start_title) + 1
            end_title = content.find('</title', start_title)
            if end_title != -1:
                print(f"Title: '{content[start_title:end_title].strip()}'")
        
        # Print first 500 characters
        print()
        print("First 500 characters:")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)
        
        # Check for meta tags with property="og:site_name" or property="og:title"
        for meta_prop in ['og:site_name', 'og:title', 'twitter:title']:
            start = content.find(f'property="{meta_prop}"')
            if start != -1:
                start = content.find('content="', start)
                if start != -1:
                    start += len('content="')
                    end = content.find('"', start)
                    if end != -1:
                        print(f"{meta_prop}: '{content[start:end]}'")
        
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    files = [
        "arts1_response.html",
        "onyxcomms_response.html", 
        "verulam_response.html",
        "sunrise_response.html"
    ]
    
    for filename in files:
        check_response(filename)
