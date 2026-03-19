#!/usr/bin/env python3
"""
Fast Scraper - Optimized for speed by using manual overrides and minimal HTTP calls
This is used by the web interface to provide fast scraping

Search order:
- Officer: DuckDuckGo → Companies House → Serper → Website
- Address: Website (contact/footer) → Companies House → DuckDuckGo → Serper
"""

import re
import os
import json
import base64
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

load_dotenv()

CH_BASE = "https://api.company-information.service.gov.uk"
_CH_KEY = os.environ.get("COMPANIES_HOUSE_API_KEY", "")
_SERPER_KEY = os.environ.get("SERPER_API_KEY", "")

SKIP_DOMAINS = [
    "linkedin.com", "facebook.com", "twitter.com", "wikipedia.org",
    "youtube.com", "instagram.com", "reddit.com", "zoominfo.com",
    "bloomberg.com", "crunchbase.com", "glassdoor.com", "indeed.com"
]


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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
}

LEARNING_CACHE_FILE = os.path.join(os.path.dirname(__file__), "learning_cache.json")


# ── Search helpers (DuckDuckGo, Serper, Companies House) ───────────────────

def _ddg_urls(query: str, max_results: int = 5) -> list[str]:
    """Get URLs from DuckDuckGo search"""
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=max_results)
        return [r["href"] for r in results if "href" in r]
    except Exception:
        return []


def _serper_urls(query: str, max_results: int = 5) -> list[str]:
    """Get URLs from Serper (Google) search"""
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


def _ch_headers(api_key: str) -> dict:
    """Generate headers for Companies House API"""
    token = base64.b64encode(f"{api_key}:".encode()).decode()
    return {**HEADERS, "Authorization": f"Basic {token}"}


def search_companies_house(company_name: str, needs_address: bool = True, needs_officer: bool = True) -> dict:
    """Search Companies House for company details"""
    if not _CH_KEY or not company_name:
        return {}

    # Try the given name first, then a stripped version
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
    """Execute Companies House search"""
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

    company_number = best.get("company_number", "")
    name = best.get("title", "")
    result = {"company_name": name, "address": "", "officer": "", "source": "Companies House"}

    if needs_address:
        addr = best.get("address", {})
        result["address"] = ", ".join(filter(None, [
            addr.get("premises"), addr.get("address_line_1"), addr.get("address_line_2"),
            addr.get("locality"), addr.get("postal_code"), addr.get("country")
        ]))

    if needs_officer:
        result["officer"] = _get_ch_officer(company_number)

    return result


# Role priority for Companies House officers
_CH_ROLE_PRIORITY = ["chief executive", "managing director", "founder", "owner", "director"]


def _ch_role_rank(role: str) -> int:
    """Get rank for officer role (lower = higher priority)"""
    role = role.lower()
    for i, r in enumerate(_CH_ROLE_PRIORITY):
        if r in role:
            return i
    return len(_CH_ROLE_PRIORITY)


def _get_ch_officer(company_number: str) -> str:
    """Get top officer from Companies House"""
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
    ranked = [(o, _ch_role_rank(o.get("officer_role", ""))) for o in active]
    ranked = [(o, rank) for o, rank in ranked if rank < len(_CH_ROLE_PRIORITY)]
    if not ranked:
        return _format_ch_name(active[0].get("name", "")) if active else ""
    ranked.sort(key=lambda x: (x[1], x[0].get("name", "")))
    return _format_ch_name(ranked[0][0].get("name", ""))


def _format_ch_name(raw: str) -> str:
    """Format Companies House officer name"""
    if "," in raw:
        parts = raw.split(",", 1)
        last = parts[0].strip().title()
        first = parts[1].strip().split()[0].title() if parts[1].strip() else ""
        return f"{first} {last}".strip()
    return raw.strip().title()


def _search_and_scrape(query: str, needs_address: bool, needs_officer: bool, engine: str = "ddg") -> dict:
    """Search and scrape for address/officer using DuckDuckGo or Serper"""
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

ADDRESS_STREET_TOKENS = ["street", "road", "rd", "ave", "avenue", "lane", "drive", "court", "boulevard", "place"]
OFFICER_STOPWORDS = {"team", "staff", "leadership", "members", "group", "partners", "services", "solutions", "logistics", "contact", "support", "info", "sales", "privacy", "terms", "cookie"}
OFFICER_BLACKLIST = {"company", "employee", "customer", "address", "phone", "email", "register", "domain", "home", "office", "market", "tracker", "trackers", "global", "logistics", "consulting", "solutions", "group", "media", "communications", "online", "digital", "web", "network", "partners"}
# Additional phrases that are clearly not person names
OFFICER_PHRASE_BLACKLIST = ["market trackers", "global logistics", "management team", "support team", "sales team", "contact us", "enquiries", "enquiry", "info", "general enquiries", "head office", "registered office", "main office"]
CONFIDENCE_THRESHOLDS = {
    "company_name": 0.5,
    "address": 0.7,
    "officer": 0.65
}



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


SECOND_LEVEL_TLDS = {"co.uk", "org.uk", "gov.uk", "ac.uk", "net.uk", "sch.uk", "ltd.uk", "plc.uk"}


def _get_domain_base(host: str) -> str:
    host = host.lower().strip().lstrip('www.')
    parts = host.split('.')
    if len(parts) < 2:
        return host

    tld = '.'.join(parts[-2:])
    if tld in SECOND_LEVEL_TLDS and len(parts) >= 3:
        return '.'.join(parts[-3:])
    return tld


def _find_similar_entry(host: str) -> Optional[dict]:
    cache = _load_learning_cache()
    base_host = _get_domain_base(host)
    best_entry = None
    best_score = 0.0

    for candidate_host, entry in cache.items():
        if not isinstance(entry, dict):
            continue
        if entry.get('user_corrected'):
            continue
        candidate_base = _get_domain_base(candidate_host)
        # exact base domain match or suffix match gets priority
        score = 0.0
        if candidate_base == base_host:
            score += 0.7
        elif base_host.endswith(candidate_base) or candidate_base.endswith(base_host):
            score += 0.4

        # evaluate confidence similarity
        candidate_conf = max(entry.get('candidates', {}).get('company_name', {}).get('confidence', 0),
                             entry.get('candidates', {}).get('address', {}).get('confidence', 0),
                             entry.get('candidates', {}).get('officer', {}).get('confidence', 0))
        score += candidate_conf * 0.3

        if score > best_score and candidate_conf >= 0.7:
            best_score = score
            best_entry = entry

    if best_entry:
        return {
            'company_name': best_entry.get('candidates', {}).get('company_name', {}).get('value', ''),
            'address': best_entry.get('candidates', {}).get('address', {}).get('value', ''),
            'officer': best_entry.get('candidates', {}).get('officer', {}).get('value', ''),
            'source': 'PatternMatchCache',
            'confidence': {
                'company_name': best_entry.get('candidates', {}).get('company_name', {}).get('confidence', 0),
                'address': best_entry.get('candidates', {}).get('address', {}).get('confidence', 0),
                'officer': best_entry.get('candidates', {}).get('officer', {}).get('confidence', 0)
            }
        }
    return None


def _learned_result(url: str) -> Optional[dict]:
    from urllib.parse import urlparse
    try:
        host = urlparse(url).netloc.replace('www.', '')
        cache = _load_learning_cache()
        entry = cache.get(host)
        if not entry:
            return None
        
        # Always validate cached entries before returning them
        company_conf = entry.get('candidates', {}).get('company_name', {}).get('confidence', 0)
        address_conf = entry.get('candidates', {}).get('address', {}).get('confidence', 0)
        officer_conf = entry.get('candidates', {}).get('officer', {}).get('confidence', 0)

        sanitized_address = _sanitize_address(entry.get('candidates', {}).get('address', {}).get('value', ''))
        candidate_officer = entry.get('candidates', {}).get('officer', {}).get('value', '')
        
        if _validate_address(sanitized_address) and _validate_officer(candidate_officer):
            return {
                'company_name': entry.get('candidates', {}).get('company_name', {}).get('value', ''),
                'address': sanitized_address,
                'officer': candidate_officer,
                'source': 'LearningCache',
                'confidence': {
                    'company_name': company_conf,
                    'address': address_conf,
                    'officer': officer_conf
                }
            }

        # if no direct entry, attempt pattern-based neighbor lookup
        similar = _find_similar_entry(host)
        if similar and _validate_address(similar.get('address', '')) and _validate_officer(similar.get('officer', '')):
            return similar
        return None
    except Exception:
        return None


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
                if 'postaladdress' in t and isinstance(obj, dict):
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
    # remove common non-address artifacts and time-related prefixes
    addr = re.sub(r"\b(?:Veritas|MGP-i|C-Cure|Blog|Contact|head office|home office|visitor|archive|latest news|whois|registrant|domain privacy|\d{1,2}[ap]m Address)\b", "", addr, flags=re.I).strip(' ,;"\'')
    addr = ' '.join(addr.split())

    postcode_pattern = re.compile(r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}", re.I)
    m = postcode_pattern.search(addr)

    if m:
        segment = addr[max(0, m.start() - 120):m.end() + 12].strip(' ,;"\'')
        parts = [p.strip(" ,;\'\"") for p in segment.split(',') if p.strip()]
        if parts:
            # keep at most 3 meaningful chunks ending on postcode
            for i, part in enumerate(parts):
                if postcode_pattern.search(part):
                    start_segment = max(0, i - 2)
                    candidate = ', '.join(parts[start_segment:i + 1]).strip(' ,;"\'')
                    return candidate
        return segment

    # try explicit address snippet detection
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

    postcode = re.search(r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}", addr.upper())
    if not postcode and not re.search(r"\d{1,4}\s+(?:" + "|".join(ADDRESS_STREET_TOKENS) + r")", addr.lower()):
        return False
    if any(word in addr.lower() for word in ["privacy", "newsletter", "subscribe", "terms", "cookie"]):
        return False
    return True


def _validate_officer(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False
    cleaned = name.strip()
    if len(cleaned) < 6 or len(cleaned) > 80:
        return False
    parts = cleaned.split()
    if len(parts) < 2 or len(parts) > 5:
        return False
    if any(word.lower() in OFFICER_STOPWORDS or word.lower() in OFFICER_BLACKLIST for word in parts):
        return False
    # Check for blacklisted phrases
    if any(phrase in cleaned.lower() for phrase in OFFICER_PHRASE_BLACKLIST):
        return False
    # expect proper-case pattern
    if not all(p[0].isupper() for p in parts if p):
        return False
    if any(re.search(r"\d", p) for p in parts):
        return False
    if cleaned.lower().startswith(('team', 'leadership', 'management', 'board', 'about', 'contact')):
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
        'DuckDuckGo': 0.55,
        'Unknown': 0.4
    }.get(source, 0.45)
    score += source_score
    if is_valid:
        score += 0.2
    # shorter unreliable names/address should get lower score
    if field == 'company_name' and len(value) < 4:
        score -= 0.2
    if field in ('address', 'officer') and not value.strip():
        score = 0.0
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


def store_learning_candidate(url: str, candidate: dict):
    from urllib.parse import urlparse
    try:
        host = urlparse(url).netloc.replace('www.', '')
        if not candidate or not isinstance(candidate, dict):
            return False
        # strong assurance that candidate has at least one high-confidence field
        if max(candidate.get('confidence', {}).values(), default=0) < 0.7 and not candidate.get('validated'):
            return False

        cache = _load_learning_cache()
        existing = cache.get(host, {})

        # merge with existing and favor highest confidence
        merged = existing.get('candidates', {}) if isinstance(existing.get('candidates'), dict) else {}

        if 'company_name' in candidate and candidate['confidence'].get('company_name', 0) > merged.get('company_name', {}).get('confidence', 0):
            merged['company_name'] = {
                'value': candidate.get('company_name', ''),
                'confidence': candidate.get('confidence', {}).get('company_name', 0),
                'source': candidate.get('source', ''),
            }
        if 'address' in candidate and candidate['confidence'].get('address', 0) > merged.get('address', {}).get('confidence', 0):
            merged['address'] = {
                'value': candidate.get('address', ''),
                'confidence': candidate.get('confidence', {}).get('address', 0),
                'source': candidate.get('source', ''),
            }
        if 'officer' in candidate and candidate['confidence'].get('officer', 0) > merged.get('officer', {}).get('confidence', 0):
            merged['officer'] = {
                'value': candidate.get('officer', ''),
                'confidence': candidate.get('confidence', {}).get('officer', 0),
                'source': candidate.get('source', ''),
            }

        # keep validated and user-corrected highest priority
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
        host = urlparse(url).netloc.replace('www.', '')
        cache = _load_learning_cache()
        if host in cache:
            del cache[host]
            _save_learning_cache(cache)
        return True
    except Exception:
        return False


# Manual overrides for specific websites
SITE_OVERRIDES = {}


def get_site_override(url):
    """Check if there's a manual override for the given URL"""
    # Keeping function for compatibility, but manual overrides are disabled.
    # Scraper should extract from live content, not prepopulated data.
    return None


def _get(url, **kwargs):
    """Fast HTTP GET with reasonable timeout and proper encoding handling"""
    try:
        # Increase timeout to 15 seconds for slower sites
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False, **kwargs)
        r.raise_for_status()
        
        # Try to decode the response properly
        try:
            # Try to get encoding from headers
            if 'content-type' in r.headers and 'charset=' in r.headers['content-type']:
                r.encoding = r.headers['content-type'].split('charset=')[-1].split(';')[0]
            else:
                r.encoding = r.apparent_encoding
        except:
            r.encoding = 'utf-8'
        
        # Try to decode, handling errors gracefully
        try:
            content = r.text
        except:
            # If decoding fails, try other encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    content = r.content.decode(encoding, 'replace')
                    r.encoding = encoding
                    break
                except:
                    continue
        
        return r
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def _extract_company_name(soup: BeautifulSoup) -> str:
    """Extract company name from various sources (fast)"""
    page_text = soup.get_text(" ", strip=True).lower()
    error_texts = [
        "your connection is not private", "verification successful", "access denied",
        "certificate", "site can't be reached", "cf-error", "bot challenge"
    ]
    if any(err in page_text for err in error_texts):
        return ""

    # Try Open Graph first
    tag = soup.find("meta", property="og:site_name")
    if tag and tag.get("content", "").strip():
        content = tag["content"].strip()
        if len(content) < 100 and not content.startswith("http"):
            return content
    
    # Try Twitter card
    tag = soup.find("meta", property="twitter:title") or soup.find("meta", attrs={"name": "twitter:title"})
    if tag and tag.get("content", "").strip():
        content = tag["content"].strip()
        if len(content) < 100 and not content.startswith("http"):
            return content
    
    # Try title tag (remove suffixes like " | Home" or " - Welcome")
    tag = soup.select_one("title")
    if tag and tag.get_text(strip=True):
        title = tag.get_text(strip=True).strip()
        if len(title) < 150 and not title.startswith("http"):
            # Remove common suffixes
            for separator in [" | ", " - ", " — "]:
                if separator in title:
                    title = title.split(separator)[0].strip()
            # Remove query params and fragments
            if "?" in title:
                title = title.split("?")[0]
            if "#" in title:
                title = title.split("#")[0]
            if len(title) < 100 and title.lower() not in ["home", "welcome", "index", "main"]:
                return title
    
    # Try h1 tags (common for company names)
    for h1 in soup.select("h1"):
        text = h1.get_text(strip=True)
        if len(text) < 100 and not text.startswith("http"):
            # Skip generic titles like "Home" or "Welcome"
            if text.lower() not in ["home", "welcome", "index", "main"]:
                return text
    
    # Try to find company name in meta tags
    meta_names = ["application-name", "description", "keywords"]
    for name in meta_names:
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            content = tag["content"].strip()
            if len(content) < 200:
                # Look for company name patterns
                matches = re.findall(r"[A-Z][\w\s&]+(?:Ltd|Limited|PLC|LLC)", content)
                if matches:
                    return matches[0].strip()
    
    # Fallback to domain name
    return ""


def _extract_address(text: str) -> str:
    """Extract address using regex first, fallback to AI agents"""
    
    # Clean the text first to handle encoding issues
    try:
        text = text.encode('utf-8', 'replace').decode('utf-8')
    except:
        pass
    
    # Look for UK postcodes and extract surrounding text (more robust)
    uk_postcode = re.search(r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}", text)
    if uk_postcode:
        snippet = text[max(0, uk_postcode.start() - 200):uk_postcode.end()]
        # Clean up the snippet
        snippet = re.sub(r"\s+", " ", snippet)
        snippet = re.sub(r"\n|\r", " ", snippet)
        
        # Try to extract complete address by finding address components
        # Look for address lines containing street, road, avenue, etc.
        address_lines = []
        
        # Find all possible address components
        components = re.findall(r"[\w\s.,#'-]+(?:Street|Road|Rd|St|Avenue|Ave|Drive|Dr|Court|Crescent|Close|Lane|House|Building|Unit|Suite|Floor)", snippet)
        if components:
            address_lines.extend([comp.strip() for comp in components])
        
        # Look for city and country
        cities = re.findall(r"[A-Z][a-zA-Z\s]+(?:City|Town|Borough|Village)", snippet)
        if cities:
            address_lines.extend([city.strip() for city in cities])
        
        # Look for region or county
        regions = re.findall(r"[A-Z][a-zA-Z\s]+(?:County|Region|State|Province)", snippet)
        if regions:
            address_lines.extend([reg.strip() for reg in regions])
        
        # Add postcode if not already present
        if uk_postcode.group(0) not in [line for line in address_lines]:
            address_lines.append(uk_postcode.group(0))
        
        if address_lines:
            # Join address lines with proper formatting
            return ", ".join(address_lines).strip()
        else:
            # Fallback to just returning what we found around postcode
            return uk_postcode.group(0)
    
    # Look for patterns like "City, Country" or "Address, Town, Postcode"
    address_pattern = re.search(r"[\w\s]+(?:, [\w\s]+){2,}", text)
    if address_pattern:
        return address_pattern.group(0).strip()
    
    # Fallback to AI address extraction if regex fails
    try:
        from ai_agents import AIAddressExtractionAgent
        address = AIAddressExtractionAgent.extract_address(text)
        if address and len(address) > 3 and address.lower() not in ["london", "northamptonshire"]:
            return address
    except Exception as e:
        print(f"AI address extraction error: {e}")
        pass
    
    return ""


def _extract_person_name(text: str) -> str:
    """Extract person name using fast patterns for common officer roles"""
    patterns = [
        r"CEO\s*[:\s]+([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})",
        r"Managing Director\s*[:\s]+([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})",
        r"Founder\s*[:\s]+([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})",
        r"Owner\s*[:\s]+([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})",
        r"Director\s*[:\s]+([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})",
        r"([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})\s*-\s*CEO",
        r"([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})\s*-\s*Managing Director",
        r"([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})\s*-\s*Founder",
        r"([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})\s*-\s*Owner",
        r"([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})\s*-\s*Director",
        r"([A-Z][a-zA-Z']+(?:\s[A-Z][a-zA-Z']*){1,2})\s*(?:is|as)\s*(?:CEO|Managing Director|Founder|Owner|Director)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            # Validate name has at least first and last name and is not a keyword
            if len(name.split()) >= 2 and len(name) < 50 and not any(keyword in name.lower() for keyword in ["contact", "us", "our", "team", "staff", "careers", "select", "specialities", "scientific", "equipment", "login", "accreditations", "lifting", "studios", "engineers", "mastering"]):
                return name
    
    return ""


def _collect_candidates_from_page(url, soup, source_name):
    candidates = {"company_name": [], "address": [], "officer": []}
    json_data = _parse_json_ld(soup)

    if json_data.get('company_name'):
        valid = bool(json_data['company_name']) and len(json_data['company_name']) >= 2
        candidates['company_name'].append({
            'value': json_data['company_name'],
            'source': 'Website',
            'confidence': _score_candidate('company_name', json_data['company_name'], 'Website', valid)
        })

    structured_address_used = False
    if json_data.get('address'):
        addr_clean = _sanitize_address(json_data['address'])
        if _validate_address(addr_clean):
            structured_address_used = True
            candidates['address'].append({
                'value': addr_clean,
                'source': 'Website',
                'confidence': _score_candidate('address', addr_clean, 'Website', True)
            })

    company_name = _extract_company_name(soup)
    if company_name:
        valid = bool(company_name) and len(company_name) >= 3
        candidates['company_name'].append({
            'value': company_name,
            'source': 'Website',
            'confidence': _score_candidate('company_name', company_name, 'Website', valid)
        })

    page_text = soup.get_text(" ", strip=True)
    if not structured_address_used:
        addr_text = _extract_address(page_text)
        if addr_text:
            addr_text = _sanitize_address(addr_text)
            valid = _validate_address(addr_text)
            candidates['address'].append({
                'value': addr_text,
                'source': 'Website',
                'confidence': _score_candidate('address', addr_text, 'Website', valid)
            })

    officer_text = _extract_person_name(page_text)
    if officer_text:
        valid = _validate_officer(officer_text)
        candidates['officer'].append({
            'value': officer_text,
            'source': 'Website',
            'confidence': _score_candidate('officer', officer_text, 'Website', valid)
        })

    return candidates


def scrape_website_fast(url):
    """Fast scraping method using minimal HTTP calls"""
    from urllib.parse import urlparse, urljoin
    from concurrent.futures import ThreadPoolExecutor, as_completed

    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    candidate_pool = {"company_name": [], "address": [], "officer": []}

    # Page candidates prioritized based on data location insights:
    # - Address: contact page and footer
    # - Company name: copyright footer, header, about pages
    # - Officer: rarely on site, try search first
    page_urls = [url, f"{base}/contact", f"{base}/about", f"{base}/team", f"{base}/footer"]
    page_urls = list(dict.fromkeys(page_urls))

    def scrape_page(page_url):
        r = _get(page_url)
        if not r:
            return None
        s = BeautifulSoup(r.text, "lxml")
        page_text_raw = s.get_text(" ", strip=True)
        skip_markers = ["one moment", "checking your browser", "cf-browser-verification", "verification successful", "enable javascript and cookies", "your connection is not private", "access denied", "certificate", "site can't be reached", "cf-error", "bot challenge"]
        if any(marker in page_text_raw.lower() for marker in skip_markers):
            return None
        for tag in s(["script", "style"]):
            tag.decompose()
        return _collect_candidates_from_page(page_url, s, 'Website')

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(scrape_page, purl): purl for purl in page_urls}
        for future in as_completed(future_to_url):
            collected = future.result()
            if collected:
                for field in candidate_pool:
                    candidate_pool[field].extend(collected[field])

    # Try whois as secondary source
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc.replace('www.', '')
        whois_data = _whois_lookup(domain)
        if whois_data.get('organization'):
            company_override = whois_data.get('organization')
            valid = bool(company_override) and len(company_override) >= 3
            candidate_pool['company_name'].append({'value': company_override, 'source': 'Companies House', 'confidence': _score_candidate('company_name', company_override, 'Companies House', valid)})
        if whois_data.get('address'):
            address_override = _sanitize_address(whois_data.get('address'))
            valid = _validate_address(address_override)
            candidate_pool['address'].append({'value': address_override, 'source': 'Companies House', 'confidence': _score_candidate('address', address_override, 'Companies House', valid)})
    except Exception:
        pass

    best_company = _pick_best(candidate_pool['company_name'], 'company_name')
    best_address = _pick_best(candidate_pool['address'], 'address')
    best_officer = _pick_best(candidate_pool['officer'], 'officer')

    result = {
        'company_name': best_company['value'],
        'address': best_address['value'],
        'officer': best_officer['value'],
        'source': best_company['source'] or best_address['source'] or best_officer['source'] or 'Website',
        'confidence': {
            'company_name': best_company['confidence'],
            'address': best_address['confidence'],
            'officer': best_officer['confidence']
        }
    }

    # if high-confidence result, store to cache
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


def scrape(query: str):
    """Main fast scraping entry point with full search flow:
    - Officer: DuckDuckGo → Companies House → Serper → Website
    - Address: Website (contact/footer) → Companies House → DuckDuckGo → Serper
    """
    result = {"company_name": "", "address": "", "officer": "", "registered_name": "", "source": "", "confidence": {"company_name": 0.0, "address": 0.0, "officer": 0.0}}

    if query.strip() and not query.strip().startswith("http"):
        normalized = "https://" + query.strip().lstrip("http://").lstrip("https://").lstrip("www.")
    else:
        normalized = query.strip()

    # Note: We always scrape fresh as information may have changed.
    # Cache entries (especially ManualVerified) are used as format guides only.
    # Skipping cache return to ensure fresh data.

    is_url = query.strip().lower().startswith(("http://", "https://"))
    if not is_url and "." in query and not query.startswith(" "):
        if len(query.strip()) > 3 and any(ext in query.lower() for ext in [".com", ".co.uk", ".net", ".org", ".io"]):
            stripped = query.strip()
            if stripped.lower().startswith('http://'):
                stripped = stripped[7:]
            elif stripped.lower().startswith('https://'):
                stripped = stripped[8:]
            if stripped.lower().startswith('www.'):
                stripped = stripped[4:]
            query = f"https://{stripped}"
            is_url = True

    def _needs(r):
        return (not r.get("company_name"), not r.get("address"), not r.get("officer"))

    def _done(r):
        return all([r.get("company_name"), r.get("address"), r.get("officer")])

    # ── Step 1: Website scrape (name + address) ───────────────────────────
    if is_url:
        site = scrape_website_fast(query)
        result.update(site)
        if result.get("company_name") and result.get("address"):
            pass  # continue to search for officer

    # ── Step 2: WHOIS lookup ────────────────────────────────────────────────
    _, n_addr, n_off = _needs(result)
    if is_url and (n_addr or not result.get("company_name")):
        from urllib.parse import urlparse
        domain = urlparse(query).netloc.replace("www.", "")
        whois_data = _whois_lookup(domain)
        if whois_data:
            if not result["company_name"] and whois_data.get("organization"):
                candidate_name = whois_data["organization"]
                valid = bool(candidate_name) and len(candidate_name) >= 3
                score = _score_candidate('company_name', candidate_name, 'WHOIS', valid)
                if score > result['confidence']['company_name']:
                    result['company_name'] = candidate_name
                    result['confidence']['company_name'] = score
                    result['source'] = 'WHOIS'
            if n_addr and whois_data.get("address"):
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
                    candidate_address = ", ".join(address_parts)
                    valid = _validate_address(candidate_address)
                    score = _score_candidate('address', candidate_address, 'WHOIS', valid)
                    if score > result['confidence']['address']:
                        result['address'] = candidate_address
                        result['confidence']['address'] = score
                        result['source'] = 'WHOIS'

    # ── Step 3: DuckDuckGo for officer FIRST ───────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_off:
        search_query = result.get("company_name") or query
        ddg = _search_and_scrape(search_query, needs_address=False, needs_officer=True, engine="ddg")
        if ddg.get("officer"):
            result['officer'] = ddg['officer']
            result['confidence']['officer'] = _score_candidate('officer', ddg['officer'], 'DuckDuckGo', _validate_officer(ddg['officer']))
            result['source'] = (result.get('source', '') + ' | DuckDuckGo').strip(' |')
            print(f"  Found officer via DuckDuckGo: {result.get('officer')}")

    # ── Step 4: Companies House for officer (after DuckDuckGo) ─────────────
    _, n_addr, n_off = _needs(result)
    if n_off and result.get("company_name"):
        ch = search_companies_house(result["company_name"], needs_address=False, needs_officer=True)
        if ch.get("officer"):
            result['officer'] = ch['officer']
            result['confidence']['officer'] = _score_candidate('officer', ch['officer'], 'Companies House', _validate_officer(ch['officer']))
            result['source'] = (result.get('source', '') + ' | Companies House').strip(' |')
            print(f"  Found officer via Companies House: {result.get('officer')}")

    # ── Step 5: Serper for officer ─────────────────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_off:
        search_query = result.get("company_name") or query
        serper = _search_and_scrape(search_query, needs_address=False, needs_officer=True, engine="serper")
        if serper.get("officer"):
            result['officer'] = serper['officer']
            result['confidence']['officer'] = _score_candidate('officer', serper['officer'], 'Serper', _validate_officer(serper['officer']))
            result['source'] = (result.get('source', '') + ' | Serper').strip(' |')
            print(f"  Found officer via Serper: {result.get('officer')}")

    # ── Step 6: Website officer fallback (last resort - rarely has officer) ─
    if is_url and not result.get("officer"):
        site_off = scrape_website_fast(query)
        if site_off.get("officer"):
            result['officer'] = site_off['officer']
            result['confidence']['officer'] = _score_candidate('officer', site_off['officer'], 'Website', _validate_officer(site_off['officer']))
            print(f"  Found officer via Website: {result.get('officer')}")

    # ── Step 7: Companies House for remaining address ──────────────────────
    _, n_addr, n_off = _needs(result)
    if n_addr and result.get("company_name"):
        ch = search_companies_house(result["company_name"], needs_address=True, needs_officer=False)
        if ch.get("address"):
            result['address'] = ch['address']
            result['confidence']['address'] = _score_candidate('address', ch['address'], 'Companies House', _validate_address(ch['address']))
            result['source'] = (result.get('source', '') + ' | Companies House').strip(' |')

    # ── Step 8: DuckDuckGo for remaining address ────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_addr:
        search_query = result.get("company_name") or query
        ddg = _search_and_scrape(search_query, needs_address=True, needs_officer=False, engine="ddg")
        if ddg.get("address"):
            result['address'] = ddg['address']
            result['confidence']['address'] = _score_candidate('address', ddg['address'], 'DuckDuckGo', _validate_address(ddg['address']))
            result['source'] = (result.get('source', '') + ' | DuckDuckGo').strip(' |')

    # ── Step 9: Serper for remaining address ────────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_addr:
        search_query = result.get("company_name") or query
        serper = _search_and_scrape(search_query, needs_address=True, needs_officer=False, engine="serper")
        if serper.get("address"):
            result['address'] = serper['address']
            result['confidence']['address'] = _score_candidate('address', serper['address'], 'Serper', _validate_address(serper['address']))
            result['source'] = (result.get('source', '') + ' | Serper').strip(' |')

    # Fallback fallback - domain extraction for company name
    if not result["company_name"] or result["company_name"] == query or len(result["company_name"]) < 3:
        from urllib.parse import urlparse
        parsed = urlparse(query)
        domain = parsed.netloc.replace('www.', '')
        if domain:
            parts = domain.split('.')
            if len(parts) >= 3 and parts[-2] in ['co', 'com', 'net', 'org']:
                result["company_name"] = ' '.join(parts[:-2]).title()
            elif len(parts) >= 2:
                result["company_name"] = ' '.join(parts[:-1]).title()
            else:
                result["company_name"] = domain.title()
            if not result['confidence']['company_name']:
                result['confidence']['company_name'] = 0.3

    # Only auto-cache if at least one field meets threshold
    if is_url and max(result['confidence'].values()) >= 0.7:
        store_learning_candidate(query, {
            'company_name': result['company_name'],
            'address': result['address'],
            'officer': result['officer'],
            'source': result['source'],
            'confidence': result['confidence'],
            'validated': all(result['confidence'][k] >= CONFIDENCE_THRESHOLDS[k] for k in CONFIDENCE_THRESHOLDS)
        })

    return result
