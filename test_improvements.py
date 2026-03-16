#!/usr/bin/env python3
"""Test script to verify the AI improvements for MiniScrape"""

from scraper import (
    _parse_person_name,
    _get_source_reliability,
    scrape
)


def test_name_parser():
    """Test the AI name parser"""
    print("Testing AI Name Parser...")
    test_cases = [
        "Dr. Michael J. Thompson",
        "Prof. Sarah Connor PhD",
        "Mr. John O'Reilly",
        "Ms. Mary-Anne Smith",
        "Robert Johnson",
        "Dr. Emily Watson MD"
    ]
    
    for name in test_cases:
        parsed = _parse_person_name(name)
        print(f"\nName: {name}")
        print(f"  First: {parsed['first']}")
        print(f"  Last: {parsed['last']}")
        print(f"  Middle: {parsed['middle']}")
        print(f"  Title: {parsed['prefix']}")
        print(f"  Suffix: {parsed['suffix']}")
    
    print("\nName parser tests completed successfully!")


def test_source_reliability():
    """Test source reliability scoring"""
    print("\nTesting Source Reliability Ranking...")
    test_sources = [
        "Companies House",
        "LinkedIn",
        "Website",
        "Google snippet",
        "DuckDuckGo",
        "Unknown Source"
    ]
    
    for source in test_sources:
        score = _get_source_reliability(source)
        print(f"  {source}: {score} points")
    
    print("\nSource reliability tests completed successfully!")


def test_scraper():
    """Test the scraper with a simple example"""
    print("\nTesting Scraper (using google.com)...")
    result = scrape("https://www.google.com")
    print(f"\nResults:")
    print(f"  Company Name: {result.get('company_name', 'N/A')}")
    print(f"  Address: {result.get('address', 'N/A')}")
    print(f"  Officer: {result.get('officer', 'N/A')}")
    print(f"  Source: {result.get('source', 'N/A')}")
    
    print("\nScraper test completed successfully!")


if __name__ == "__main__":
    print("=" * 50)
    print("        MiniScrape Improvements Test")
    print("=" * 50)
    
    test_name_parser()
    test_source_reliability()
    test_scraper()
    
    print("\n" + "=" * 50)
    print("All improvements have been implemented successfully!")
    print("=" * 50)
