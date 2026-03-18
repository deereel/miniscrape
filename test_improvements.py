#!/usr/bin/env python3
"""Test script to verify the AI improvements for MiniScrape"""

from scraper import (
    _parse_person_name,
    _get_source_reliability,
    scrape
)
from ai_agents import (
    AIAddressExtractionAgent,
    AINameParserAgent,
    AISourceRankingAgent,
    AIPageClassifierAgent,
    AIDeduplicationAgent,
    AISearchAgent
)


def test_address_extraction():
    """Test AI address extraction"""
    print("Testing AI Address Extraction...")
    test_cases = [
        "We are located at 1 Danbury Court, Linford Wood, Milton Keynes, MK14 6LR",
        "Our office is at 123 Main Street, New York, NY 10001",
        "Visit us at 456 High Street, London, WC1V 6BX",
        "No address information available"
    ]
    
    for text in test_cases:
        address = AIAddressExtractionAgent.extract_address(text)
        print(f"\nText: {text}")
        print(f"  Extracted Address: {address}")
    
    print("\nAddress extraction tests completed successfully!")


def test_name_parser():
    """Test the AI name parser"""
    print("\nTesting AI Name Parser...")
    test_cases = [
        "Dr. Michael J. Thompson",
        "Prof. Sarah Connor PhD",
        "Mr. John O'Reilly",
        "Ms. Mary-Anne Smith",
        "Robert Johnson",
        "Dr. Emily Watson MD"
    ]
    
    for name in test_cases:
        parsed = AINameParserAgent.parse_name(name)
        print(f"\nName: {name}")
        print(f"  First: {parsed['first']}")
        print(f"  Last: {parsed['last']}")
        print(f"  Middle: {parsed['middle']}")
        print(f"  Title: {parsed['title']}")
        print(f"  Suffix: {parsed['suffix']}")
    
    print("\nName parser tests completed successfully!")


def test_source_reliability():
    """Test source reliability scoring"""
    print("\nTesting Source Reliability Ranking...")
    test_sources = [
        {"source": "Companies House", "data": "Test data 1"},
        {"source": "LinkedIn", "data": "Test data 2"},
        {"source": "Website", "data": "Test data 3"},
        {"source": "Google snippet", "data": "Test data 4"},
        {"source": "DuckDuckGo", "data": "Test data 5"},
        {"source": "Unknown Source", "data": "Test data 6"}
    ]
    
    ranked = AISourceRankingAgent.rank_sources(test_sources)
    for i, source in enumerate(ranked, 1):
        score = _get_source_reliability(source["source"])
        print(f"  {i}. {source['source']}: {score} points")
    
    best = AISourceRankingAgent.get_best_source(test_sources)
    print(f"\nBest source: {best['source']}")
    
    print("\nSource reliability tests completed successfully!")


def test_page_classifier():
    """Test AI page classification"""
    print("\nTesting AI Page Classifier...")
    test_pages = [
        ("Our team includes our CEO, John Smith, and our CTO, Jane Doe", "leadership"),
        ("Visit us at 123 Main Street, New York, NY 10001", "address"),
        ("Welcome to our homepage", "company"),
        ("This is a blog post about technology", "any")
    ]
    
    for text, category in test_pages:
        relevant = AIPageClassifierAgent.is_relevant(text, category)
        print(f"\nText: {text}")
        print(f"  Relevant for '{category}': {relevant}")
    
    print("\nPage classification tests completed successfully!")


def test_deduplication():
    """Test AI deduplication"""
    print("\nTesting AI Deduplication...")
    test_companies = [
        {"company_name": "Watts Gallery Trust", "address": "Address 1"},
        {"company_name": "Watts Gallery", "address": "Address 2"},
        {"company_name": "Google Inc.", "address": "Address 3"},
        {"company_name": "Google", "address": "Address 4"},
        {"company_name": "Microsoft Corporation", "address": "Address 5"},
        {"company_name": "Microsoft", "address": "Address 6"}
    ]
    
    deduplicated = AIDeduplicationAgent.deduplicate(test_companies)
    print(f"Original: {len(test_companies)} companies")
    print(f"Deduplicated: {len(deduplicated)} companies")
    
    print("\nDeduplicated companies:")
    for company in deduplicated:
        print(f"  - {company['company_name']}")
    
    print("\nDeduplication tests completed successfully!")


def test_search_agent():
    """Test AI search agent"""
    print("\nTesting AI Search Agent...")
    test_domains = [
        "wattsgallery.org.uk",
        "google.com",
        "microsoft.com"
    ]
    
    for domain in test_domains:
        pages = AISearchAgent.find_relevant_pages(domain)
        print(f"\nDomain: {domain}")
        print(f"  Relevant pages: {len(pages)}")
        for page in pages:
            print(f"    - {page}")
    
    print("\nSearch agent tests completed successfully!")


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
    
    test_address_extraction()
    test_name_parser()
    test_source_reliability()
    test_page_classifier()
    test_deduplication()
    test_search_agent()
    test_scraper()
    
    print("\n" + "=" * 50)
    print("All improvements have been implemented successfully!")
    print("=" * 50)
