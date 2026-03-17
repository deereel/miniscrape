from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

class ScrapingResult(BaseModel):
    """Model for validating scraping results"""
    company_name: str = Field(..., min_length=1, description="Company name")
    address: str = Field(..., min_length=1, description="Company address")
    officer: str = Field(..., min_length=1, description="Key officer/contact")
    source: str = Field(..., min_length=1, description="Source of information")
    registered_name: Optional[str] = Field(None, description="Registered company name")
    website_url: Optional[HttpUrl] = Field(None, description="Website URL")
    scrape_timestamp: Optional[datetime] = Field(None, description="Timestamp of scraping")
    
    class Config:
        """Pydantic configuration"""
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }

class ScrapingRequest(BaseModel):
    """Model for validating scraping requests"""
    url: HttpUrl = Field(..., description="Website URL to scrape")
    scrape_company_name: bool = Field(True, description="Scrape company name")
    scrape_address: bool = Field(True, description="Scrape address")
    scrape_officer: bool = Field(True, description="Scrape officer/contact info")

class BatchScrapingRequest(BaseModel):
    """Model for validating batch scraping requests"""
    urls: list[HttpUrl] = Field(
        default=...,
        min_items=1,
        description="List of URLs to scrape"
    )
    scrape_company_name: bool = Field(True, description="Scrape company name")
    scrape_address: bool = Field(True, description="Scrape address")
    scrape_officer: bool = Field(True, description="Scrape officer/contact info")

class APIResponse(BaseModel):
    """Model for API responses"""
    success: bool = Field(True, description="Request success status")
    message: str = Field("Scraping completed successfully", description="Response message")
    results: Optional[list[ScrapingResult]] = Field(None, description="Scraping results")
    errors: Optional[list[str]] = Field(None, description="Error messages")
    total_scraped: Optional[int] = Field(None, description="Total URLs scraped")
    successful_scrapes: Optional[int] = Field(None, description="Number of successful scrapes")
    failed_scrapes: Optional[int] = Field(None, description="Number of failed scrapes")
