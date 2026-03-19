import re
import os
import json
import base64
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from nameparser import HumanName
from schemas import ScrapingResult
from typing import Optional
from datetime import datetime
from ai_agents import (
    AIAddressExtractionAgent,
    AINameParserAgent,
    AISourceRankingAgent,
    AIPageClassifierAgent,
    AIDeduplicationAgent,
    AISearchAgent
)

load_dotenv()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
}
CH_BASE = "https://api.company-information.service.gov.uk"
_CH_KEY = os.environ.get("COMPANIES_HOUSE_API_KEY", "")
_SERPER_KEY = os.environ.get("SERPER_API_KEY", "")

SKIP_DOMAINS = [
    "linkedin.com", "facebook.com", "twitter.com", "wikipedia.org",
    "youtube.com", "instagram.com", "reddit.com", "zoominfo.com",
    "bloomberg.com", "crunchbase.com", "glassdoor.com", "indeed.com"
]

_GENERIC_TITLES = {
    "contact", "contact us", "home", "about", "about us", "team",
    "our team", "services", "welcome", "page not found", "404"
}

LEARNING_CACHE_FILE = os.path.join(os.path.dirname(__file__), "learning_cache.json")

# Source reliability scores (higher = more reliable)
_SOURCE_RELIABILITY = {
    "Website": 95,
    "Companies House": 90,
    "LinkedIn": 85,
    "Google snippet": 60,
    "DuckDuckGo": 55
}

_NAME_NOISE = re.compile(
    r"\s*[\|\-–—]\s*(LinkedIn|Facebook|Twitter|Instagram|Wikipedia|Home|"
    r"Welcome|Official Site|Official Website)[^$]*$",
    re.IGNORECASE
)


# ── Helpers ────────────────────────────────────────────────────────────────

def _get(url, **kwargs):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, **kwargs)
        r.raise_for_status()
        # Force UTF-8 encoding to avoid encoding issues
        r.encoding = 'utf-8'
        return r
    except Exception:
        return None


def _whois_lookup(domain: str) -> dict:
    """Perform a WHOIS lookup on a domain"""
    try:
        import whois
        w = whois.whois(domain)
        result = {}
        
        # Extract registrant information
        if w.registrant:
            result["registrant"] = str(w.registrant)
        if w.org:
            result["organization"] = str(w.org)
        if w.address:
            result["address"] = str(w.address)
        if w.city:
            result["city"] = str(w.city)
        if w.state:
            result["state"] = str(w.state)
        if w.country:
            result["country"] = str(w.country)
        if w.registrar:
            result["registrar"] = str(w.registrar)
        
        return result
    except Exception as e:
        print(f"  [!] WHOIS error: {e}")
        return {}


def _geocode_address(address: str) -> dict:
    """Geocode an address using OpenStreetMap Nominatim API"""
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="miniscrape")
        location = geolocator.geocode(address)
        
        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address
            }
        else:
            return {}
    except Exception as e:
        print(f"  [!] Geocoding error: {e}")
        return {}


def _needs(result: dict) -> tuple[bool, bool, bool]:
    """Return (needs_name, needs_address, needs_officer)."""
    return (
        not result.get("company_name"),
        not result.get("address"),
        not result.get("officer"),
    )


def _done(result: dict) -> bool:
    return all([result.get("company_name"), result.get("address"), result.get("officer")])


ADDRESS_STREET_TOKENS = ["street", "road", "rd", "ave", "avenue", "lane", "drive", "court", "boulevard", "place"]
OFFICER_STOPWORDS = {"team", "staff", "leadership", "members", "group", "partners", "services", "solutions", "logistics", "contact", "support", "info", "sales", "privacy", "terms", "cookie"}
OFFICER_BLACKLIST = {"company", "employee", "customer", "address", "phone", "email", "register", "domain", "home", "office", "market", "tracker", "trackers", "global", "logistics", "consulting", "solutions", "group", "media", "communications", "online", "digital", "web", "network", "partners"}
# Additional phrases that are clearly not person names
OFFICER_PHRASE_BLACKLIST = ["market trackers", "global logistics", "management team", "support team", "sales team", "contact us", "enquiries", "enquiry", "info", "general enquiries", "head office", "registered office", "main office"]
CONFIDENCE_THRESHOLDS = {
    "company_name": 0.5,
    "address": 0.7,
    "officer": 0.7
}

LEADERSHIP_KEYWORDS = ["ceo", "chief executive", "managing director", "founder", "owner", "director", "chair", "vp", "president", "lead"]


def _parse_json_ld(soup: BeautifulSoup) -> dict:
    data = {}
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            payload = json.loads(script.string or '{}')
            if isinstance(payload, list):
                candidates = payload
            else:
                candidates = [payload]

            for obj in candidates:
                if not isinstance(obj, dict):
                    continue
                t = obj.get('@type', '').lower()
                if 'organization' in t:
                    if obj.get('name'):
                        data['company_name'] = obj.get('name').strip()
                    address = obj.get('address')
                    if isinstance(address, dict):
                        addr = []
                        for key in ['streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry']:
                            if address.get(key):
                                addr.append(str(address.get(key)).strip())
                        if addr:
                            data['address'] = ', '.join(addr)
                if 'postaladdress' in t:
                    addr = []
                    for key in ['streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry']:
                        if obj.get(key):
                            addr.append(str(obj.get(key)).strip())
                    if addr:
                        data['address'] = ', '.join(addr)
        except Exception:
            continue
    return data


def _sanitize_address(address: str) -> str:
    if not address or not isinstance(address, str):
        return ""
    addr = ' '.join(address.replace('\n', ' ').replace('\r', ' ').split())
    addr = re.sub(r"\b(?:Veritas|MGP-i|C-Cure|Blog|Contact|head office|home office|visitor|archive|latest news|whois|registrant|domain privacy|error|warning|redirect)\b", "", addr, flags=re.I).strip(' ,;"\'')
    addr = ' '.join(addr.split())

    postcode_pattern = re.compile(r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}", re.I)
    m = postcode_pattern.search(addr)
    if m:
        segment = addr[max(0, m.start() - 120):m.end() + 12].strip(' ,;"\'')
        parts = [p.strip(' ,;"\'') for p in segment.split(',') if p.strip()]
        for i, part in enumerate(parts):
            if postcode_pattern.search(part):
                start_segment = max(0, i - 2)
                candidate = ', '.join(parts[start_segment:i + 1]).strip(' ,;"\'')
                return candidate
        return segment

    m2 = re.search(r"(\d{1,4}[\w\s\.,#\-]+?(?:Street|Road|Rd|St|Avenue|Ave|Drive|Dr|Court|Close|Lane|House|Suite|Unit|Building))", addr, re.I)
    if m2:
        return m2.group(1).strip(' ,;"\'')

    return addr


def _validate_address(address: str) -> bool:
    if not address or not isinstance(address, str):
        return False
    addr = _sanitize_address(address)
    if not addr:
        return False
    if len(addr) < 10 or len(addr) > 300:
        return False

    postcode_pattern = re.compile(r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}", re.I)
    if not postcode_pattern.search(addr.upper()) and not re.search(r"\d{1,4}\s+(?:(?:street|road|rd|ave|avenue|lane|drive|court|boulevard|place))", addr.lower()):
        return False

    if any(word in addr.lower() for word in ["privacy", "newsletter", "subscribe", "terms", "cookie", "password", "login"]):
        return False

    if len(re.findall(r"\d", addr)) < 2:
        return False

    return True


def _is_leadership_context(text: str, match_start: int) -> bool:
    lower = text.lower()
    start = max(0, match_start - 130)
    end = min(len(lower), match_start + 130)
    context = lower[start:end]
    return any(word in context for word in LEADERSHIP_KEYWORDS)


def _sanitize_officer(name: str) -> str:
    if not name or not isinstance(name, str):
        return ""
    clean = ' '.join(name.replace('\n', ' ').replace('\r', ' ').split())
    clean = re.sub(r"\b(?:contact us|team|admin|support|info|sales)\b", '', clean, flags=re.I).strip(' ,;"\'')
    return ' '.join(clean.split())


def _validate_officer(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False
    cleaned = _sanitize_officer(name)
    if len(cleaned) < 8 or len(cleaned) > 80:
        return False
    parts = cleaned.split()
    if len(parts) < 2 or len(parts) > 4:
        return False
    if any(word.lower() in OFFICER_STOPWORDS or word.lower() in OFFICER_BLACKLIST for word in parts):
        return False
    # Check for blacklisted phrases
    if any(phrase in cleaned.lower() for phrase in OFFICER_PHRASE_BLACKLIST):
        return False
    if not all(p[0].isupper() for p in parts if p):
        return False
    if any(re.search(r"\d", p) for p in parts):
        return False
    if cleaned.lower().startswith(('team', 'leadership', 'management', 'board', 'about', 'contact', 'company', 'employee')):
        return False
    return True


def _score_candidate(field: str, value: str, source: str, is_valid: bool) -> float:
    if not value or not isinstance(value, str):
        return 0.0
    score = 0.0
    source_score = {
        'UserCorrect': 1.0,
        'LearningCache': 0.95,
        'Companies House': 0.9,
        'Website': 0.8,
        'Google snippet': 0.6,
        'DuckDuckGo': 0.55
    }.get(source, 0.45)
    score += source_score
    if is_valid:
        score += 0.2
    if field == 'company_name' and len(value) < 4:
        score -= 0.2
    return min(max(score, 0.0), 1.0)


def _pick_best(candidates: list, field: str):
    # Filter candidates - for address and officer, require validation
    filtered = []
    for c in candidates:
        if field == 'address':
            if _validate_address(c.get('value', '')):
                filtered.append(c)
        elif field == 'officer':
            if _validate_officer(c.get('value', '')):
                filtered.append(c)
        else:
            filtered.append(c)
    
    if not filtered:
        return {'value': '', 'confidence': 0.0, 'source': ''}
    
    best = {'value': '', 'confidence': 0.0, 'source': ''}
    for c in filtered:
        if c['confidence'] > best['confidence']:
            best = c
    if best['confidence'] >= CONFIDENCE_THRESHOLDS.get(field, 0.5):
        return best
    return {'value': '', 'confidence': best['confidence'], 'source': best['source']}


def _load_learning_cache() -> dict:
    try:
        if os.path.exists(LEARNING_CACHE_FILE):
            with open(LEARNING_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_learning_cache(cache: dict):
    try:
        with open(LEARNING_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _learned_result(url: str) -> Optional[dict]:
    from urllib.parse import urlparse
    try:
        host = urlparse(url).netloc.replace("www.", "")
        cache = _load_learning_cache()
        entry = cache.get(host)
        if not entry:
            return None
        
        company_conf = entry.get('candidates', {}).get('company_name', {}).get('confidence', 0)
        address_conf = entry.get('candidates', {}).get('address', {}).get('confidence', 0)
        officer_conf = entry.get('candidates', {}).get('officer', {}).get('confidence', 0)

        # Always validate cached entries before returning them
        candidate_address = _sanitize_address(entry.get('candidates', {}).get('address', {}).get('value', ''))
        candidate_officer = entry.get('candidates', {}).get('officer', {}).get('value', '')
        if _validate_address(candidate_address) and _validate_officer(candidate_officer):
            best = {
                'company_name': entry.get('candidates', {}).get('company_name', {}).get('value', ''),
                'address': candidate_address,
                'officer': candidate_officer,
                'source': 'LearningCache',
                'confidence': {
                    'company_name': company_conf,
                    'address': address_conf,
                    'officer': officer_conf
                }
            }
            return best
        return None
    except Exception:
        return None


def store_learning_candidate(url: str, candidate: dict):
    from urllib.parse import urlparse
    try:
        host = urlparse(url).netloc.replace('www.', '')
        if not candidate or not isinstance(candidate, dict):
            return False

        # Avoid storing partial low-confidence entries as the canonical cache
        confidences = candidate.get('confidence', {})
        if not candidate.get('validated') and not candidate.get('user_corrected'):
            if (confidences.get('company_name', 0) < CONFIDENCE_THRESHOLDS['company_name'] or
                confidences.get('address', 0) < CONFIDENCE_THRESHOLDS['address'] or
                confidences.get('officer', 0) < CONFIDENCE_THRESHOLDS['officer']):
                return False

        if max(confidences.values(), default=0) < 0.7 and not candidate.get('validated'):
            return False
        cache = _load_learning_cache()
        existing = cache.get(host, {})
        existing_candidates = existing.get('candidates', {}) if isinstance(existing.get('candidates'), dict) else {}

        merged = {**existing_candidates}
        for field in ['company_name', 'address', 'officer']:
                    
            if candidate.get(field) and candidate.get('confidence', {}).get(field, 0) > merged.get(field, {}).get('confidence', 0):
                merged[field] = {
                    'value': candidate.get(field, ''),
                    'confidence': candidate.get('confidence', {}).get(field, 0),
                    'source': candidate.get('source', '')
                }

        cache[host] = {
            'candidates': merged,
            'validated': candidate.get('validated', False) or existing.get('validated', False),
            'user_corrected': candidate.get('user_corrected', existing.get('user_corrected', False)),
            'updated_at': datetime.now().isoformat()
        }
        _save_learning_cache(cache)
        return True
    except Exception:
        return False


def store_learning_correction(url: str, correction: dict):
    from urllib.parse import urlparse
    try:
        if not (correction.get('company_name') and correction.get('address') and correction.get('officer')):
            return False
        host = urlparse(url).netloc.replace('www.', '')
        cache = _load_learning_cache()
        cache[host] = {
            'candidates': {
                'company_name': {'value': correction['company_name'], 'confidence': 1.0, 'source': 'UserCorrect'},
                'address': {'value': correction['address'], 'confidence': 1.0, 'source': 'UserCorrect'},
                'officer': {'value': correction['officer'], 'confidence': 1.0, 'source': 'UserCorrect'}
            },
            'validated': True,
            'user_corrected': True,
            'updated_at': datetime.now().isoformat()
        }
        _save_learning_cache(cache)
        return True
    except Exception:
        return False


def clear_learning_entry(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        host = urlparse(url).netloc.replace("www.", "")
        cache = _load_learning_cache()
        if host in cache:
            del cache[host]
            _save_learning_cache(cache)
        return True
    except Exception:
        return False


def _get_source_reliability(source: str) -> int:
    """Get reliability score for a source (higher = more reliable)."""
    if not source:
        return 0
    # First, try to use the AI source ranking agent
    try:
        source_lower = source.lower()
        for known_source, score in AISourceRankingAgent.SOURCE_RELIABILITY.items():
            if known_source.lower() in source_lower:
                return score
    except Exception:
        pass
    
    # Fall back to existing scoring
    source_lower = source.lower()
    for known_source, score in _SOURCE_RELIABILITY.items():
        if known_source.lower() in source_lower:
            return score
    
    # Default score for unknown sources
    return 50


def _merge(base: dict, update: dict) -> dict:
    # Only set company name if not already found from the website
    if not base.get("company_name") and _is_real_name(update.get("company_name", "")):
        base["company_name"] = update["company_name"]
    
    # For address and officer, check if we have a more reliable source
    for key in ["address", "officer", "registered_name"]:
        if update.get(key):
            if not base.get(key):
                base[key] = update[key]
            else:
                # Compare source reliability
                base_score = _get_source_reliability(base.get("source", ""))
                update_score = _get_source_reliability(update.get("source", ""))
                if update_score > base_score:
                    base[key] = update[key]
    
    if 'confidence' in update and isinstance(update['confidence'], dict):
        base_conf = base.setdefault('confidence', {'company_name': 0.0, 'address': 0.0, 'officer': 0.0})
        for k in ['company_name', 'address', 'officer']:
            base_conf[k] = max(base_conf.get(k, 0.0), update['confidence'].get(k, 0.0))

    if not base.get("source") and update.get("source"):
        base["source"] = update["source"]
    elif base.get("source") and update.get("source"):
        # Update source if new source is more reliable
        base_score = _get_source_reliability(base["source"])
        update_score = _get_source_reliability(update["source"])
        if update_score > base_score:
            base["source"] = update["source"]

    return base


def _is_real_name(name: str) -> bool:
    return bool(name) and name.lower().strip() not in _GENERIC_TITLES


# ── Extraction helpers ─────────────────────────────────────────────────────

def _clean_name(raw: str) -> str:
    cleaned = _NAME_NOISE.sub("", raw).strip()
    for sep in [" | ", " - ", " – ", " — "]:
        if sep in cleaned:
            cleaned = cleaned.split(sep)[0].strip()
    return cleaned


def _extract_company_name(soup: BeautifulSoup) -> str:
    page_text = soup.get_text(" ", strip=True).lower()
    bad_terms = [
        "your connection is not private", "verification successful", "access denied",
        "certificate", "site can't be reached", "cf-error", "bot challenge"
    ]
    if any(term in page_text for term in bad_terms):
        return ""

    tag = soup.find("meta", property="og:site_name")
    if tag and tag.get("content", "").strip():
        name = _clean_name(tag["content"].strip())
        if len(name) < 100 and not any(word in name.lower() for word in ["design", "print", "legacy", "embedded", "business"]):
            return name
    for prop in ["og:title", "twitter:title"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content", "").strip():
            name = _clean_name(tag["content"].strip())
            if len(name) < 100 and not any(word in name.lower() for word in ["design", "print", "legacy", "embedded", "business"]):
                return name
    for sel in ["h1", "title"]:
        tag = soup.select_one(sel)
        if tag and tag.get_text(strip=True):
            name = _clean_name(tag.get_text(strip=True))[:120]
            if len(name) < 100 and not any(word in name.lower() for word in ["design", "print", "legacy", "embedded", "business"]):
                return name
    return ""


def _extract_address(text: str) -> str:
    """Extract address using AI-powered extraction"""
    return AIAddressExtractionAgent.extract_address(text)


def _extract_person_name(text: str) -> str:
    # Ordered by priority: CEO first, then MD, Founder, Owner, Director
    title_priority = [
        r"CEO|Chief Executive Officer|Chief Executive",
        r"Managing Director",
        r"Founder",
        r"Owner",
        r"Chairman",
        r"Director",
        r"President",
    ]

    text = ' '.join(text.replace('\n', ' ').replace('\r', ' ').split())
    for title_pattern in title_priority:
        # Title BEFORE name
        for m in re.finditer(rf"(?:{title_pattern})[\s:,\-]+([A-Z][a-zA-Z'\-]+\s[A-Z][a-zA-Z'\-]+)", text):
            name = m.group(1).strip()
            if _is_leadership_context(text, m.start()) and _validate_officer(name):
                return name

        # Name BEFORE title
        for m in re.finditer(rf"([A-Z][a-zA-Z'\-]+\s[A-Z][a-zA-Z'\-]+)\s+(?:{title_pattern})", text):
            name = m.group(1).strip()
            if _is_leadership_context(text, m.start()) and _validate_officer(name):
                return name

    # fallback by proximity scan for name tokens and leadership keywords
    names = re.findall(r"([A-Z][a-zA-Z'\-]+\s[A-Z][a-zA-Z'\-]+)", text)
    for candidate in names:
        if not any(w in candidate.lower().split() for w in OFFICER_BLACKLIST):
            pos = text.lower().find(candidate.lower())
            if pos >= 0 and _is_leadership_context(text, pos) and _validate_officer(candidate):
                return candidate

    return ""


def _parse_person_name(name: str) -> dict:
    """Parse a full name into first and last name using AI-powered nameparser."""
    parsed = AINameParserAgent.parse_name(name)
    if parsed:
        return {
            "first": parsed.get("first", "").strip(),
            "last": parsed.get("last", "").strip(),
            "middle": parsed.get("middle", "").strip(),
            "suffix": parsed.get("suffix", "").strip(),
            "prefix": parsed.get("title", "").strip()
        }
    # Fallback if parsing fails
    parts = name.strip().split()
    if len(parts) >= 2:
        return {
            "first": parts[0],
            "last": " ".join(parts[1:]),
            "middle": "",
            "suffix": "",
            "prefix": ""
        }
    return {
        "first": name,
        "last": "",
        "middle": "",
        "suffix": "",
        "prefix": ""
    }


# ── Step 1: Website scrape ─────────────────────────────────────────────────

def _extract_registered_name(soup: BeautifulSoup) -> str:
    """Extract registered company name from footer (trading-as / copyright text)."""
    footer = soup.find("footer")
    text = footer.get_text(" ", strip=True) if footer else ""
    if not text:
        text = soup.get_text(" ", strip=True)[-1500:]
    for pattern in [
        r"([A-Z][\w\s&]+(?:Ltd|Limited|PLC|LLP))\s*(?:trading as|t/a)",
        r"([A-Z][\w\s&]+(?:Ltd|Limited|PLC|LLP))\s+Company number",
        r"Copyright[^\n]{0,40}([A-Z][\w\s&]+(?:Ltd|Limited|PLC|LLP))",
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def _collect_candidates_from_page_soup(soup: BeautifulSoup) -> dict:
    candidates = {"company_name": [], "address": [], "officer": []}
    structured = _parse_json_ld(soup)

    if structured.get('company_name'):
        company_candidate = _clean_name(structured['company_name'])
        valid = bool(company_candidate) and len(company_candidate) >= 3
        candidates['company_name'].append({'value': company_candidate, 'source': 'Website', 'confidence': _score_candidate('company_name', company_candidate, 'Website', valid)})

    structured_address_used = False
    if structured.get('address'):
        address_candidate = _sanitize_address(structured['address'])
        if _validate_address(address_candidate):
            structured_address_used = True
            candidates['address'].append({'value': address_candidate, 'source': 'Website', 'confidence': _score_candidate('address', address_candidate, 'Website', True)})

    extracted_name = _extract_company_name(soup)
    if extracted_name:
        valid = bool(extracted_name) and len(extracted_name) >= 3
        candidates['company_name'].append({'value': extracted_name, 'source': 'Website', 'confidence': _score_candidate('company_name', extracted_name, 'Website', valid)})

    text = soup.get_text(" ", strip=True)
    if not structured_address_used:
        extracted_address = _extract_address(text)
        if extracted_address:
            extracted_address = _sanitize_address(extracted_address)
            valid = _validate_address(extracted_address)
            candidates['address'].append({'value': extracted_address, 'source': 'Website', 'confidence': _score_candidate('address', extracted_address, 'Website', valid)})

    extracted_officer = _extract_person_name(text)
    if extracted_officer:
        valid = _validate_officer(extracted_officer)
        candidates['officer'].append({'value': extracted_officer, 'source': 'Website', 'confidence': _score_candidate('officer', extracted_officer, 'Website', valid)})

    return candidates


def scrape_website(url: str, needs_name=True, needs_address=True, needs_officer=True) -> dict:
    from urllib.parse import urlparse, urljoin
    from concurrent.futures import ThreadPoolExecutor, as_completed

    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    # Prioritize pages based on where data is usually found:
    # - Address: contact page and footer
    # - Company name: copyright footer, header, about pages
    # - Officer: rarely on site
    page_urls = [f"{base}/contact", url, f"{base}/about", f"{base}/team", f"{base}/footer", f"{base}/about-us"]
    page_urls = list(dict.fromkeys(page_urls))

    candidate_pool = {"company_name": [], "address": [], "officer": []}

    def fetch_and_collect(purl):
        r = _get(purl)
        if not r:
            return None
        soup = BeautifulSoup(r.text, "lxml")
        page_text_raw = soup.get_text(" ", strip=True).lower()
        skip_markers = ["one moment", "checking your browser", "cf-browser-verification", "just a moment", "verification successful", "enable javascript and cookies", "your connection is not private", "access denied", "certificate", "site can't be reached", "cf-error", "bot challenge"]
        if any(marker in page_text_raw for marker in skip_markers):
            return None
        for tag in soup(["script", "style"]):
            tag.decompose()
        return _collect_candidates_from_page_soup(soup)

    def _goal_achieved() -> bool:
        best_company = _pick_best(candidate_pool['company_name'], 'company_name')
        best_address = _pick_best(candidate_pool['address'], 'address')
        best_officer = _pick_best(candidate_pool['officer'], 'officer')
        return (best_company['confidence'] >= CONFIDENCE_THRESHOLDS['company_name'] and
                best_address['confidence'] >= CONFIDENCE_THRESHOLDS['address'] and
                best_officer['confidence'] >= CONFIDENCE_THRESHOLDS['officer'])

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fetch_and_collect, u): u for u in page_urls}
        for future in as_completed(futures):
            collected = future.result()
            if collected:
                for field in candidate_pool:
                    candidate_pool[field].extend(collected[field])
            if _goal_achieved():
                for f in futures:
                    if not f.done():
                        f.cancel()
                break

    best_company = _pick_best(candidate_pool['company_name'], 'company_name')
    best_address = _pick_best(candidate_pool['address'], 'address')
    best_officer = _pick_best(candidate_pool['officer'], 'officer')

    result = {
        'company_name': best_company['value'],
        'address': best_address['value'],
        'officer': best_officer['value'],
        'registered_name': '',
        'source': best_company['source'] or best_address['source'] or best_officer['source'] or 'Website',
        'confidence': {
            'company_name': best_company['confidence'],
            'address': best_address['confidence'],
            'officer': best_officer['confidence']
        }
    }

    if (needs_name and not result['company_name']) or (needs_address and not result['address']) or (needs_officer and not result['officer']):
        try:
            # Try Playwright first (faster than Selenium)
            print(f"  Regular scraping failed, trying Playwright for: {url}")
            from playwright_scraper import scrape_with_playwright
            playwright_result = scrape_with_playwright(url)
            if playwright_result:
                if needs_name and not result['company_name'] and playwright_result.get('company_name'):
                    result['company_name'] = playwright_result.get('company_name')
                    result['confidence']['company_name'] = 0.7
                if needs_address and not result['address'] and playwright_result.get('address'):
                    result['address'] = playwright_result.get('address')
                    result['confidence']['address'] = 0.7
                if needs_officer and not result['officer'] and playwright_result.get('officer'):
                    result['officer'] = playwright_result.get('officer')
                    result['confidence']['officer'] = 0.7
                if not result['registered_name'] and playwright_result.get('registered_name'):
                    result['registered_name'] = playwright_result.get('registered_name')
        except Exception as e:
            print(f"  Playwright failed: {e}")
            # Fall back to Selenium if Playwright fails
            try:
                print(f"  Trying Selenium fallback for: {url}")
                from selenium_scraper import scrape_with_selenium
                selenium_result = scrape_with_selenium(url)
                if selenium_result:
                    if needs_name and not result['company_name'] and selenium_result.get('company_name'):
                        result['company_name'] = selenium_result.get('company_name')
                        result['confidence']['company_name'] = 0.7
                    if needs_address and not result['address'] and selenium_result.get('address'):
                        result['address'] = selenium_result.get('address')
                        result['confidence']['address'] = 0.7
                    if needs_officer and not result['officer'] and selenium_result.get('officer'):
                        result['officer'] = selenium_result.get('officer')
                        result['confidence']['officer'] = 0.7
                    if not result['registered_name'] and selenium_result.get('registered_name'):
                        result['registered_name'] = selenium_result.get('registered_name')
            except Exception as e2:
                print(f"  Selenium also failed: {e2}")

    if max(result['confidence'].values()) >= 0.7:
        store_learning_candidate(url, {
            'company_name': result['company_name'],
            'address': result['address'],
            'officer': result['officer'],
            'source': result['source'],
            'confidence': result['confidence'],
            'validated': all(result['confidence'][k] >= CONFIDENCE_THRESHOLDS[k] for k in CONFIDENCE_THRESHOLDS)
        })

    return result


# ── Step 2: Companies House ────────────────────────────────────────────────

def _ch_headers(api_key: str) -> dict:
    token = base64.b64encode(f"{api_key}:".encode()).decode()
    return {**HEADERS, "Authorization": f"Basic {token}"}


def search_companies_house(company_name: str, needs_address=True, needs_officer=True) -> dict:
    if not _CH_KEY or not company_name:
        return {}

    # Try the given name first, then a stripped version (removes Ltd/Limited/Services etc.)
    candidates = [company_name]
    stripped = re.sub(r"\b(ltd|limited|plc|services|group|uk|the)\b", "", company_name, flags=re.IGNORECASE).strip()
    if stripped and stripped.lower() != company_name.lower():
        candidates.append(stripped)

    for name in candidates:
        result = _ch_search(name, needs_address, needs_officer)
        if result.get("company_name"):
            return result
    return {}


def _ch_search(company_name: str, needs_address: bool, needs_officer: bool) -> dict:
    if not _CH_KEY or not company_name:
        return {}
    try:
        r = requests.get(
            f"{CH_BASE}/search/companies",
            params={"q": company_name, "items_per_page": 10},
            headers=_ch_headers(_CH_KEY),
            timeout=15
        )
        if r.status_code == 401:
            print("  [!] Companies House API key is invalid or expired.")
            return {}
        r.raise_for_status()
    except Exception as e:
        print(f"  [!] Companies House error: {e}")
        return {}

    items = r.json().get("items", [])
    if not items:
        return {}

    # Pick best match: score by how many query words appear in the title, prefer active
    query_words = [w for w in re.sub(r"\b(ltd|limited|plc|services|group|uk|the|renewables|solutions|consulting)\b", "", company_name, flags=re.IGNORECASE).split() if len(w) > 2]
    def _score(item):
        title = item.get("title", "").lower()
        active_bonus = 2 if item.get("company_status") == "active" else 0
        word_score = sum(1 for w in query_words if w.lower() in title)
        return active_bonus + word_score

    scored = sorted(items, key=lambda x: (-_score(x), len(x.get("title", ""))), reverse=False)
    best = scored[0] if scored else items[0]
    if query_words and _score(best) == 0:
        return {}
    # For short prefix queries, ensure the best match title actually starts with the prefix
    q_lower = company_name.lower().strip()
    best_title = best.get("title", "").lower()
    if len(q_lower) <= 5 and not best_title.startswith(q_lower):
        # Try to find a better match that does start with the prefix
        for item in scored:
            if item.get("title", "").lower().startswith(q_lower) and item.get("company_status") == "active":
                best = item
                break
        else:
            return {}

    company_number = best.get("company_number", "")
    name = best.get("title", "")
    result = {
        "company_name": name, 
        "address": "", 
        "officer": "", 
        "source": "Companies House",
        "confidence": {
            "company_name": _score_candidate('company_name', name, 'Companies House', True),
            "address": 0.0,
            "officer": 0.0
        }
    }

    if needs_address:
        addr = best.get("address", {})
        address_str = ", ".join(filter(None, [
            addr.get("premises"), addr.get("address_line_1"), addr.get("address_line_2"),
            addr.get("locality"), addr.get("postal_code"), addr.get("country")
        ]))
        result["address"] = address_str
        result["confidence"]["address"] = _score_candidate('address', address_str, 'Companies House', _validate_address(address_str))

    if needs_officer:
        officer_str = _get_top_officer(company_number)
        result["officer"] = officer_str
        result["confidence"]["officer"] = _score_candidate('officer', officer_str, 'Companies House', _validate_officer(officer_str))

    return result


# Role priority: lower index = higher rank
_ROLE_PRIORITY = [
    "chief executive",
    "managing director",
    "founder",
    "owner",
    "director",
]


def _role_rank(role: str) -> int:
    role = role.lower()
    for i, r in enumerate(_ROLE_PRIORITY):
        if r in role:
            return i
    return len(_ROLE_PRIORITY)  # lowest priority


def _get_top_officer(company_number: str) -> str:
    if not company_number:
        return ""
    try:
        r = requests.get(
            f"{CH_BASE}/company/{company_number}/officers",
            headers=_ch_headers(_CH_KEY),
            timeout=10
        )
        r.raise_for_status()
    except Exception:
        return ""
    officers = r.json().get("items", [])
    active = [o for o in officers if not o.get("resigned_on")]
    # Only keep officers with a recognised high-ranking role
    ranked = [(o, _role_rank(o.get("officer_role", ""))) for o in active]
    ranked = [(o, rank) for o, rank in ranked if rank < len(_ROLE_PRIORITY)]
    if not ranked:
        # Fall back to first active officer if none match priority roles
        return _format_officer_name(active[0].get("name", "")) if active else ""
    # Sort by rank, then alphabetically for consistency when tied
    ranked.sort(key=lambda x: (x[1], x[0].get("name", "")))
    return _format_officer_name(ranked[0][0].get("name", ""))


def _format_officer_name(raw: str) -> str:
    if "," in raw:
        parts = raw.split(",", 1)
        last = parts[0].strip().title()
        first = parts[1].strip().split()[0].title() if parts[1].strip() else ""
        return f"{first} {last}".strip()
    return raw.strip().title()


# ── Step 3: DuckDuckGo ─────────────────────────────────────────────────────

def _ddg_urls(query: str, max_results: int = 5) -> list[str]:
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=max_results)
        return [r["href"] for r in results if "href" in r]
    except Exception:
        return []


def _search_and_scrape(query: str, needs_address: bool, needs_officer: bool, engine: str = "ddg") -> dict:
    if engine == "ddg":
        urls = _ddg_urls(f'"{query}" official website contact')
    else:
        urls = _serper_urls(f'"{query}" official website contact')

    for url in urls:
        if any(d in url for d in SKIP_DOMAINS):
            continue
        r = _get(url)
        if not r:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
        result = {"address": "", "officer": ""}
        if needs_address:
            result["address"] = _extract_address(text)
        if needs_officer:
            result["officer"] = _extract_person_name(text)
        if result["address"] or result["officer"]:
            result["source"] = url
            return result
    return {}


# ── Step 4: Serper (Google) ───────────────────────────────────────────────

def _serper_urls(query: str, max_results: int = 5) -> list[str]:
    if not _SERPER_KEY:
        return []
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": _SERPER_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": max_results},
            timeout=10
        )
        r.raise_for_status()
        return [item["link"] for item in r.json().get("organic", []) if "link" in item]
    except Exception:
        return []


def _collect_text_for_ai(url: str, max_pages: int = 4) -> str:
    from urllib.parse import urlparse, urljoin
    skip_markers = [
        "one moment", "checking your browser", "cf-browser-verification", "just a moment",
        "verification successful", "enable javascript and cookies", "your connection is not private",
        "access denied", "certificate", "site can't be reached", "cf-error", "bot challenge"
    ]
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    pages = ["", "/about", "/about-us", "/contact", "/contact-us", "/team", "/our-team", "/leadership"]
    pieces = []
    for page in pages[:max_pages]:
        page_url = url if page == "" else urljoin(base, page)
        r = _get(page_url)
        if not r:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(" ", strip=True).lower()
        if any(marker in text for marker in skip_markers):
            continue
        for tag in soup(["script", "style"]):
            tag.decompose()
        pieces.append(soup.get_text(" ", strip=True))
    return "\n".join(pieces)


# ── Main entry point ───────────────────────────────────────────────────────

def scrape(query: str) -> dict:
    result = {"company_name": "", "address": "", "officer": "", "registered_name": "", "source": "", "confidence": {"company_name": 0.0, "address": 0.0, "officer": 0.0}}
    # Check if it's a URL and add protocol if missing
    is_url = query.strip().lower().startswith(("http://", "https://"))
    if not is_url and "." in query and not query.startswith(" "):
        # Try to determine if it's a URL (contains domain extension)
        # Skip if it contains spaces or looks like a plain text query
        if len(query.strip()) > 3 and any(ext in query.lower() for ext in [".com", ".co.uk", ".net", ".org", ".io", ".biz", ".info", ".uk", ".de", ".fr"]):
            # Strip any leading/trailing whitespace and add https:// protocol
            stripped = query.strip()
            # Remove protocol prefixes safely (avoid lstrip-character semantics)
            if stripped.lower().startswith("http://"):
                stripped = stripped[len("http://"):]
            elif stripped.lower().startswith("https://"):
                stripped = stripped[len("https://"):]
            if stripped.lower().startswith("www."):
                stripped = stripped[len("www."):]
            query = "https://" + stripped
            is_url = True

    def _finalise(r: dict) -> dict:
        """Finalize and validate scraping result with Pydantic"""
        try:
            # Prepare data for validation
            validated_data = {
                "company_name": r.get("company_name", query).strip(),
                "address": r.get("address", "").strip(),
                "officer": r.get("officer", "").strip(),
                "source": r.get("source", "").strip(),
                "confidence": r.get("confidence", {"company_name": 0.0, "address": 0.0, "officer": 0.0}),
                "registered_name": r.get("registered_name", "").strip() if r.get("registered_name") else None,
                "website_url": query if is_url else None,
                "scrape_timestamp": datetime.now()
            }
            
            # Validate with Pydantic
            validated_result = ScrapingResult(**validated_data)
            return validated_result.dict(exclude_none=True)
            
        except Exception as e:
            print(f"  Validation error: {e}")
            # Fallback to basic validation if Pydantic fails
            r.pop("registered_name", None)
            r.setdefault("company_name", query)
            r.setdefault("address", "")
            r.setdefault("officer", "")
            r.setdefault("source", "")
            return r

    # ── Step 0: Learning cache (for format guidance only - always do fresh scraping) ─────────
    # Note: We always scrape fresh as information may have changed.
    # Cache entries (especially ManualVerified) are used as format guides only.

    # ── Step 1: Website (name + address only) ───────────────────────────
    if is_url:
        site = scrape_website(query, needs_name=True, needs_address=True, needs_officer=False)
        result = _merge(result, site)
        if result.get("company_name") and result.get("address"):
            pass  # continue to CH for officer

    # ── Step 2: Companies House ──────────────────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_addr or n_off:
        search_terms = []
        if is_url:
            from urllib.parse import urlparse
            domain_word = urlparse(query).netloc.replace("www.", "").split(".")[0]

            # 1. Registered name from footer — most reliable
            if result.get("registered_name"):
                search_terms.append(result["registered_name"])

            # 2. Try domain word and progressively shorter prefixes
            # e.g. amcorenewables -> amcorenewables, amcorenewabl, amcorene, amcore
            tried = set()
            for length in [len(domain_word), len(domain_word)*3//4, len(domain_word)//2 + 2, len(domain_word)//3 + 2]:
                prefix = domain_word[:max(length, 3)]
                if prefix not in tried:
                    tried.add(prefix)
                    search_terms.append(prefix)

            # 3. Trading name last
            if result.get("company_name"):
                search_terms.append(result["company_name"])
        if not is_url:
            search_terms.append(query)

        # Deduplicate while preserving order
        seen = set()
        search_terms = [t for t in search_terms if not (t.lower() in seen or seen.add(t.lower()))]

        for term in search_terms:
            _, n_addr, n_off = _needs(result)
            if not n_addr and not n_off:
                break
            ch = search_companies_house(term, needs_address=n_addr, needs_officer=n_off)
            result = _merge(result, ch)
            if _done(result):
                return _finalise(result)

    # ── Step 2.5: WHOIS Lookup ────────────────────────────────────────────
    _, n_addr, n_off = _needs(result)
    if is_url and (n_addr or not result.get("company_name")):
        from urllib.parse import urlparse
        domain = urlparse(query).netloc.replace("www.", "")
        
        whois_data = _whois_lookup(domain)
        if whois_data:
            whois_result = {"source": "WHOIS"}
            
            if not result.get("company_name") and whois_data.get("organization"):
                whois_result["company_name"] = whois_data["organization"]
                
            if n_addr and whois_data.get("address"):
                # Try to format the address
                address_parts = []
                if whois_data.get("address"):
                    address_parts.append(whois_data["address"])
                if whois_data.get("city"):
                    address_parts.append(whois_data["city"])
                if whois_data.get("state"):
                    address_parts.append(whois_data["state"])
                if whois_data.get("country"):
                    address_parts.append(whois_data["country"])
                
                if address_parts:
                    whois_result["address"] = ", ".join(address_parts)
            
            if whois_result.get("company_name") or whois_result.get("address"):
                result = _merge(result, whois_result)
                if _done(result):
                    return _finalise(result)

    # ── Step 3: DuckDuckGo FIRST for officer ─────────────────────────────────
    # Note: Officer is almost never on the site, so we prioritize search engines first
    _, n_addr, n_off = _needs(result)
    if n_off:
        search_query = result.get("company_name") or query
        ddg = _search_and_scrape(search_query, needs_address=False, needs_officer=True, engine="ddg")
        result = _merge(result, ddg)
        if result.get("officer"):
            print(f"  Found officer via DuckDuckGo: {result.get('officer')}")

    # ── Step 4: Companies House for officer (after DuckDuckGo) ─────────────
    _, n_addr, n_off = _needs(result)
    if n_off and result.get("company_name"):
        ch = search_companies_house(result["company_name"], needs_address=False, needs_officer=True)
        if ch.get("officer"):
            result = _merge(result, ch)
            print(f"  Found officer via Companies House: {result.get('officer')}")

    # ── Step 5: Serper for officer ─────────────────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_off:
        search_query = result.get("company_name") or query
        serper = _search_and_scrape(search_query, needs_address=False, needs_officer=True, engine="serper")
        result = _merge(result, serper)
        if result.get("officer"):
            print(f"  Found officer via Serper: {result.get('officer')}")

    # ── Step 6: Website officer fallback (last resort - rarely has officer) ─
    if is_url and not result.get("officer"):
        site_off = scrape_website(query, needs_name=False, needs_address=False, needs_officer=True)
        result = _merge(result, site_off)
        if _done(result):
            return _finalise(result)

    # ── Step 7: DuckDuckGo for remaining address ────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_addr:
        search_query = result.get("company_name") or query
        ddg = _search_and_scrape(search_query, needs_address=True, needs_officer=False, engine="ddg")
        result = _merge(result, ddg)
        if _done(result):
            return _finalise(result)

    # ── Step 8: Serper for remaining address ────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_addr:
        search_query = result.get("company_name") or query
        serper = _search_and_scrape(search_query, needs_address=True, needs_officer=False, engine="serper")
        result = _merge(result, serper)

    # ── Step 8: AI fallback on broader site text
    _, n_addr, n_off = _needs(result)
    if (n_addr or n_off) and is_url:
        ai_text = _collect_text_for_ai(query, max_pages=5)
        if n_addr:
            ai_address = _extract_address(ai_text)
            if ai_address:
                result["address"] = ai_address
                result["source"] = (result.get("source", "") + " | AI").strip(' |')
        if n_off:
            ai_officer = _extract_person_name(ai_text)
            if ai_officer:
                result["officer"] = ai_officer
                result["source"] = (result.get("source", "") + " | AI").strip(' |')

    final_result = _finalise(result)

    # Store in learning cache if strong or complete with high confidence
    if is_url and final_result.get("company_name") and final_result.get("address") and final_result.get("officer"):
        store_learning_student = {
            'company_name': final_result.get('company_name', ''),
            'address': final_result.get('address', ''),
            'officer': final_result.get('officer', ''),
            'source': final_result.get('source', 'Website'),
            'confidence': {
                'company_name': result.get('confidence', {}).get('company_name', 0.8),
                'address': result.get('confidence', {}).get('address', 0.8),
                'officer': result.get('confidence', {}).get('officer', 0.8)
            },
            'validated': all(result.get('confidence', {}).get(k, 0) >= CONFIDENCE_THRESHOLDS[k] for k in CONFIDENCE_THRESHOLDS)
        }
        store_learning_candidate(query, store_learning_student)

    return final_result


def batch_scrape(urls: list[str], max_workers: int = 20) -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                results.append({"url": url, **future.result()})
            except Exception as e:
                results.append({"url": url, "error": str(e)})

    return results
