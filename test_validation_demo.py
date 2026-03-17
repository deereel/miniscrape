#!/usr/bin/env python3
"""Demonstrate Pydantic validation"""

from schemas import ScrapingResult, ScrapingRequest, BatchScrapingRequest
from datetime import datetime

def test_scraping_result_validation():
    """Test ScrapingResult model validation"""
    print("=== ScrapingResult Validation ===")
    
    # Valid data
    valid_data = {
        "company_name": "Acuity Training Limited",
        "address": "130 Wood Street, London, EC2V 2AL",
        "officer": "David Pugh",
        "source": "Website",
        "registered_name": "Acuity Training Limited",
        "website_url": "https://acuitytraining.co.uk",
        "scrape_timestamp": datetime.now()
    }
    
    try:
        result = ScrapingResult(**valid_data)
        print("OK: Valid data passed validation")
        print(f"  Company Name: {result.company_name}")
        print(f"  Address: {result.address}")
        print(f"  Officer: {result.officer}")
        print(f"  Source: {result.source}")
        print(f"  Registration: {result.registered_name}")
        print(f"  Website: {result.website_url}")
        print(f"  Timestamp: {result.scrape_timestamp}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Invalid data (missing company name)
    invalid_data = {
        "address": "130 Wood Street, London, EC2V 2AL",
        "officer": "David Pugh",
        "source": "Website"
    }
    
    try:
        result = ScrapingResult(**invalid_data)
        print("ERROR: Should have failed validation")
    except Exception as e:
        print("OK: Invalid data correctly failed validation")
        print(f"  Error: {e}")
    
    print()

def test_scraping_request_validation():
    """Test ScrapingRequest model validation"""
    print("=== ScrapingRequest Validation ===")
    
    # Valid request
    valid_request = {
        "url": "https://acuitytraining.co.uk",
        "scrape_company_name": True,
        "scrape_address": True,
        "scrape_officer": True
    }
    
    try:
        request = ScrapingRequest(**valid_request)
        print("OK: Valid request passed validation")
        print(f"  URL: {request.url}")
        print(f"  Scrape Name: {request.scrape_company_name}")
        print(f"  Scrape Address: {request.scrape_address}")
        print(f"  Scrape Officer: {request.scrape_officer}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Invalid URL (missing protocol)
    invalid_url = {
        "url": "acuitytraining.co.uk"
    }
    
    try:
        request = ScrapingRequest(**invalid_url)
        print("ERROR: Should have failed validation")
    except Exception as e:
        print("OK: Invalid URL correctly failed validation")
        print(f"  Error: {e}")
    
    print()

def test_batch_request_validation():
    """Test BatchScrapingRequest model validation"""
    print("=== BatchScrapingRequest Validation ===")
    
    # Valid batch
    valid_batch = {
        "urls": ["https://acuitytraining.co.uk", "https://arts1.co.uk"],
        "scrape_company_name": True,
        "scrape_address": True,
        "scrape_officer": True
    }
    
    try:
        batch = BatchScrapingRequest(**valid_batch)
        print("OK: Valid batch passed validation")
        print(f"  Number of URLs: {len(batch.urls)}")
        print(f"  URLs: {[str(u) for u in batch.urls]}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Empty list of URLs
    empty_batch = {
        "urls": [],
        "scrape_company_name": True,
        "scrape_address": True,
        "scrape_officer": True
    }
    
    try:
        batch = BatchScrapingRequest(**empty_batch)
        print("ERROR: Should have failed validation")
    except Exception as e:
        print("OK: Empty batch correctly failed validation")
        print(f"  Error: {e}")
    
    print()

if __name__ == "__main__":
    print("Pydantic Validation Demo")
    print("=" * 50)
    test_scraping_result_validation()
    test_scraping_request_validation()
    test_batch_request_validation()
    print("=" * 50)
    print("All validation tests completed!")
