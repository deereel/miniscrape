#!/usr/bin/env python3
"""
AI Agents for MiniScrape
These agents provide AI-assisted extraction for tasks where traditional scraping struggles:
- Company name identification
- Address extraction
- Officer name extraction
- Source ranking
- Page classification
- Deduplication
"""

import re
import spacy
from nameparser import HumanName

# Load spaCy model (lazy loading)
_nlp = None

def load_spacy_model():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Warning: Failed to load spaCy model: {e}")
            _nlp = False
    return _nlp


class AIAddressExtractionAgent:
    """AI agent for extracting addresses using NER (Named Entity Recognition)"""
    
    @staticmethod
    def extract_address(text: str) -> str:
        """Extract address from text using spaCy NER and postcode-based extraction"""
        
        # First, try postcode-based extraction (more reliable for UK addresses)
        postcode_based = AIAddressExtractionAgent._extract_postcode_based(text)
        if postcode_based:
            return postcode_based
            
        # Fallback to NER if no postcode found
        nlp = load_spacy_model()
        if nlp is False:
            return ""
            
        try:
            doc = nlp(text)
            
            # Look for GPE (Geopolitical Entity) and LOC (Location) entities
            address_parts = []
            seen = set()
            
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC", "FAC"]:
                    part = ent.text.strip()
                    if len(part) > 2 and part not in seen:
                        # Skip duplicates and short parts
                        lower_part = part.lower()
                        if lower_part not in ["ai", "uk", "us", "dc"] and not lower_part.startswith("contact"):
                            address_parts.append(part)
                            seen.add(part)
            
            # If we found address parts, try to find postcode
            if address_parts:
                postcode = AIAddressExtractionAgent._extract_postcode(text)
                if postcode:
                    address_parts.append(postcode)
                
                return ", ".join(address_parts)
            
            return ""
            
        except Exception as e:
            print(f"Address extraction error: {e}")
            return ""
    
    @staticmethod
    def _extract_postcode(text: str) -> str:
        """Extract UK postcode using regex"""
        postcode_pattern = r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}"
        match = re.search(postcode_pattern, text.upper())
        return match.group(0) if match else ""
    
    @staticmethod
    def _extract_postcode_based(text: str) -> str:
        """Extract address based on postcode location"""
        postcode = AIAddressExtractionAgent._extract_postcode(text)
        if postcode:
            # Look for address lines around the postcode
            idx = text.upper().find(postcode)
            if idx != -1:
                # Look 200 characters before and 50 after
                start = max(0, idx - 200)
                end = min(len(text), idx + 50)
                snippet = text[start:end]
                
                # Clean up the snippet
                snippet = re.sub(r"\s+", " ", snippet)
                snippet = re.sub(r"\n|\r", " ", snippet)
                
                # Try to find the start of the address by looking for common address prefixes
                prefixes = ["address", "contact us", "location", "find us"]
                best_start = 0
                for prefix in prefixes:
                    prefix_idx = snippet.lower().find(prefix)
                    if prefix_idx != -1:
                        best_start = prefix_idx + len(prefix)
                        break
                
                snippet = snippet[best_start:].strip()
                
                # Remove any leftover prefix characters (like colons or newlines)
                snippet = re.sub(r"^[:\s]+", "", snippet)
                
                # Find the position of the postcode in the snippet to ensure we include it
                snippet_postcode_idx = snippet.upper().find(postcode)
                if snippet_postcode_idx != -1:
                    # Include up to the postcode and a little after
                    snippet = snippet[:snippet_postcode_idx + len(postcode)].strip()
                
                # Clean up any remaining unwanted characters
                snippet = re.sub(r"\s+", " ", snippet)
                
                # Remove any email or phone number prefixes
                snippet = re.sub(r"^.*?Address\s*", "", snippet, flags=re.IGNORECASE)
                
                return snippet.strip()
        
        return ""


class AINameParserAgent:
    """AI agent for parsing person names using nameparser library"""
    
    @staticmethod
    def parse_name(name: str):
        """Parse name into structured components"""
        try:
            parsed = HumanName(name)
            return {
                "first": parsed.first,
                "middle": parsed.middle,
                "last": parsed.last,
                "title": parsed.title,
                "suffix": parsed.suffix
            }
        except Exception as e:
            print(f"Name parsing error: {e}")
            return None


class AISourceRankingAgent:
    """AI agent for ranking sources by reliability"""
    
    SOURCE_RELIABILITY = {
        "Website": 95,
        "Companies House": 90,
        "LinkedIn": 85,
        "Google snippet": 60,
        "DuckDuckGo": 55
    }
    
    @staticmethod
    def rank_sources(sources):
        """Rank sources by reliability score"""
        return sorted(
            sources,
            key=lambda x: AISourceRankingAgent.SOURCE_RELIABILITY.get(x.get("source", ""), 0),
            reverse=True
        )
    
    @staticmethod
    def get_best_source(sources):
        """Get the most reliable source"""
        ranked = AISourceRankingAgent.rank_sources(sources)
        return ranked[0] if ranked else None


class AIPageClassifierAgent:
    """AI agent for classifying if a page contains relevant information"""
    
    RELEVANT_PATTERNS = [
        # Address patterns
        r"address|contact|location|find us",
        # Leadership patterns
        r"about us|our team|management|leadership|executive|director|ceo|founder|owner",
        # Company info patterns
        r"company|corporate|who we are|about"
    ]
    
    @staticmethod
    def is_relevant(text: str, category: str = "any") -> bool:
        """Check if text contains relevant information for a specific category"""
        text = text.lower()
        
        if category == "address":
            patterns = [r"address|contact|location|find us"]
        elif category == "leadership":
            patterns = [r"our team|management|leadership|executive|director|ceo|founder|owner"]
        elif category == "company":
            patterns = [r"about us|who we are|company|corporate"]
        else:
            patterns = AIPageClassifierAgent.RELEVANT_PATTERNS
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False


class AIDeduplicationAgent:
    """AI agent for deduplicating company names using fuzzy matching"""
    
    @staticmethod
    def normalize_company_name(name: str) -> str:
        """Normalize company name for comparison"""
        # Remove legal suffixes
        suffixes = ["ltd", "limited", "inc", "incorporated", "corp", "corporation", "llp", "plc"]
        normalized = name.lower().strip()
        
        for suffix in suffixes:
            normalized = re.sub(r"\s*" + re.escape(suffix) + r"(\.|$)", "", normalized)
        
        # Remove extra whitespace and punctuation
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        
        return normalized
    
    @staticmethod
    def are_same_company(name1: str, name2: str) -> bool:
        """Check if two company names refer to the same company using fuzzy matching"""
        norm1 = AIDeduplicationAgent.normalize_company_name(name1)
        norm2 = AIDeduplicationAgent.normalize_company_name(name2)
        
        # If one is a substring of the other
        if len(norm1) > 0 and len(norm2) > 0:
            if norm1 in norm2 or norm2 in norm1:
                return True
            
            # Check if they share most words (ignoring order)
            words1 = set(norm1.split())
            words2 = set(norm2.split())
            
            if len(words1) > 0 and len(words2) > 0:
                overlap = len(words1.intersection(words2))
                if overlap >= min(len(words1), len(words2)) - 1:
                    return True
            
            # Fuzzy matching (70% similarity threshold)
            try:
                from rapidfuzz import fuzz
                similarity = fuzz.ratio(norm1, norm2)
                if similarity >= 70:
                    return True
            except ImportError:
                try:
                    from fuzzywuzzy import fuzz
                    similarity = fuzz.ratio(norm1, norm2)
                    if similarity >= 70:
                        return True
                except ImportError:
                    pass
        
        return False
    
    @staticmethod
    def deduplicate(companies):
        """Deduplicate a list of companies"""
        unique = []
        for company in companies:
            if not any(AIDeduplicationAgent.are_same_company(company["company_name"], existing["company_name"]) for existing in unique):
                unique.append(company)
        
        return unique


class AISearchAgent:
    """AI agent for deciding which pages to scrape"""
    
    RELEVANT_PATHS = {
        "address": ["contact", "contact-us", "location", "find-us"],
        "leadership": ["about", "about-us", "team", "management", "leadership", "executive", "who-we-are"],
        "company": ["about", "about-us", "company", "corporate", "who-we-are"]
    }
    
    @staticmethod
    def find_relevant_pages(domain: str, categories: list = ["address", "leadership"]):
        """Find relevant page URLs to scrape for specific categories"""
        base_url = f"https://{domain}"
        
        relevant_urls = [base_url]
        
        for category in categories:
            for path in AISearchAgent.RELEVANT_PATHS.get(category, []):
                relevant_urls.append(f"{base_url}/{path}")
                relevant_urls.append(f"{base_url}/{path}/")
        
        # Remove duplicates
        relevant_urls = list(set(relevant_urls))
        
        return relevant_urls


if __name__ == "__main__":
    # Test AI agents
    print("=== Testing AI Address Extraction Agent ===")
    test_text = "We are located at 1 Danbury Court, Linford Wood, Milton Keynes, MK14 6LR"
    address = AIAddressExtractionAgent.extract_address(test_text)
    print(f"Input: {test_text}")
    print(f"Output: {address}")
    
    print("\n=== Testing AI Name Parser Agent ===")
    test_name = "Dr. Michael J. Thompson"
    parsed = AINameParserAgent.parse_name(test_name)
    print(f"Input: {test_name}")
    print(f"Output: {parsed}")
    
    print("\n=== Testing AI Page Classifier Agent ===")
    test_page = "Our team includes our CEO, John Smith, and our CTO, Jane Doe"
    print(f"Leadership relevant: {AIPageClassifierAgent.is_relevant(test_page, 'leadership')}")
    
    print("\n=== Testing AI Deduplication Agent ===")
    companies = [
        {"company_name": "Watts Gallery Trust", "address": "Address 1"},
        {"company_name": "Watts Gallery", "address": "Address 2"}
    ]
    print(f"Are same company: {AIDeduplicationAgent.are_same_company('Watts Gallery Trust', 'Watts Gallery')}")
    print(f"Deduplicated: {AIDeduplicationAgent.deduplicate(companies)}")
