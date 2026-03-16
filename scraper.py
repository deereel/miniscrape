import re
import os
import base64
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from nameparser import HumanName

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


def _needs(result: dict) -> tuple[bool, bool, bool]:
    """Return (needs_name, needs_address, needs_officer)."""
    return (
        not result.get("company_name"),
        not result.get("address"),
        not result.get("officer"),
    )


def _done(result: dict) -> bool:
    return all([result.get("company_name"), result.get("address"), result.get("officer")])


def _get_source_reliability(source: str) -> int:
    """Get reliability score for a source (higher = more reliable)."""
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
    tag = soup.find("meta", property="og:site_name")
    if tag and tag.get("content", "").strip():
        return _clean_name(tag["content"].strip())
    for prop in ["og:title", "twitter:title"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content", "").strip():
            return _clean_name(tag["content"].strip())
    for sel in ["h1", "title"]:
        tag = soup.select_one(sel)
        if tag and tag.get_text(strip=True):
            return _clean_name(tag.get_text(strip=True))[:120]
    return ""


def _extract_address(text: str) -> str:
    # UK: anchor on postcode, walk back to last address starter
    for match in re.finditer(r"[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}", text):
        snippet = text[max(0, match.start() - 200):match.end()]
        starters = list(re.finditer(r"(?:Unit|Floor|Suite|\d{1,4})\s[A-Za-z]", snippet, re.IGNORECASE))
        if starters:
            return snippet[starters[-1].start():].strip()
    # US ZIP fallback
    us = re.search(
        r"\d{1,4}\s[\w\s,\.]{5,60}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Way|Court|Place|Square)"
        r"[\w\s,\.]{0,40}\d{5}",
        text, re.IGNORECASE
    )
    return us.group(0).strip() if us else ""


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
    noise = {"about", "our", "home", "contact", "services", "team", "us", "the",
             "close", "open", "read", "more", "appoints", "new", "joins", "named",
             "welcomes", "announces", "hire", "hires"}

    for title_pattern in title_priority:
        # Name BEFORE title
        for m in re.finditer(rf"([A-Z][a-zA-Z']+\s[A-Z][a-zA-Z']+)\s+(?:{title_pattern})", text):
            name = m.group(1).strip()
            if not any(w in name.lower().split() for w in noise):
                return name
        # Title BEFORE name
        for m in re.finditer(rf"(?:{title_pattern})[\s:,\-]+([A-Z][a-zA-Z']+\s[A-Z][a-zA-Z']+)", text):
            name = m.group(1).strip()
            if not any(w in name.lower().split() for w in noise):
                return name
    return ""


def _parse_person_name(name: str) -> dict:
    """Parse a full name into first and last name using AI-powered nameparser."""
    try:
        parsed = HumanName(name)
        return {
            "first": parsed.first.strip(),
            "last": parsed.last.strip(),
            "middle": parsed.middle.strip(),
            "suffix": parsed.suffix.strip(),
            "prefix": parsed.title.strip()
        }
    except Exception:
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


def scrape_website(url: str, needs_name=True, needs_address=True, needs_officer=True) -> dict:
    from urllib.parse import urlparse, urljoin
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    result = {"company_name": "", "address": "", "officer": "", "registered_name": "", "source": url}
    subpages = ["", "/contact", "/contact-us", "/our-founder", "/about-us", "/about", "/team", "/our-team"]
    
    # Check for manual overrides
    from site_overrides import get_site_override
    override = get_site_override(url)
    if override:
        print(f"  Using manual override for: {url}")
        return override
        
    # First, try regular scraping
    for i, path in enumerate(subpages):
        if not needs_address and not needs_officer and not needs_name:
            break
        page_url = url if path == "" else urljoin(base, path)
        r = _get(page_url)
        if not r:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        page_text_raw = soup.get_text(" ", strip=True)
        # Skip Cloudflare / bot-challenge pages
        if any(p in page_text_raw.lower() for p in ["one moment", "checking your browser", "cf-browser-verification", "just a moment"]):
            continue
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)

        if needs_name and i == 0 and not result["company_name"]:
            result["company_name"] = _extract_company_name(soup)
        if i == 0 and not result["registered_name"]:
            result["registered_name"] = _extract_registered_name(soup)
        if needs_address and not result["address"]:
            result["address"] = _extract_address(text)
        if needs_officer and i > 0 and not result["officer"]:
            result["officer"] = _extract_person_name(text)

        if result["address"] and result["officer"]:
            break
    
    # If regular scraping failed, try Selenium for JavaScript-rendered content
    if (needs_name and not result["company_name"]) or \
       (needs_address and not result["address"]) or \
       (needs_officer and not result["officer"]):
        print(f"  Regular scraping failed, trying Selenium for: {url}")
        try:
            from selenium_scraper import scrape_with_selenium
            selenium_result = scrape_with_selenium(url)
            
            # Merge results from Selenium
            if needs_name and not result["company_name"] and selenium_result["company_name"]:
                result["company_name"] = selenium_result["company_name"]
            if needs_address and not result["address"] and selenium_result["address"]:
                result["address"] = selenium_result["address"]
            if needs_officer and not result["officer"] and selenium_result["officer"]:
                result["officer"] = selenium_result["officer"]
            if not result["registered_name"] and selenium_result["registered_name"]:
                result["registered_name"] = selenium_result["registered_name"]
                
        except Exception as e:
            print(f"  Selenium failed: {e}")
    
    return result

    for i, path in enumerate(subpages):
        if not needs_address and not needs_officer and not needs_name:
            break
        page_url = url if path == "" else urljoin(base, path)
        r = _get(page_url)
        if not r:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        page_text_raw = soup.get_text(" ", strip=True)
        # Skip Cloudflare / bot-challenge pages
        if any(p in page_text_raw.lower() for p in ["one moment", "checking your browser", "cf-browser-verification", "just a moment"]):
            continue
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)

        if needs_name and i == 0 and not result["company_name"]:
            result["company_name"] = _extract_company_name(soup)
        if i == 0 and not result["registered_name"]:
            result["registered_name"] = _extract_registered_name(soup)
        if needs_address and not result["address"]:
            result["address"] = _extract_address(text)
        if needs_officer and i > 0 and not result["officer"]:
            result["officer"] = _extract_person_name(text)

        if result["address"] and result["officer"]:
            break

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
    result = {"company_name": name, "address": "", "officer": "", "source": "Companies House"}

    if needs_address:
        addr = best.get("address", {})
        result["address"] = ", ".join(filter(None, [
            addr.get("premises"), addr.get("address_line_1"), addr.get("address_line_2"),
            addr.get("locality"), addr.get("postal_code"), addr.get("country")
        ]))

    if needs_officer:
        result["officer"] = _get_top_officer(company_number)

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


# ── Step 4: Serper (Google) ────────────────────────────────────────────────

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


# ── Main entry point ───────────────────────────────────────────────────────

def scrape(query: str) -> dict:
    result = {"company_name": "", "address": "", "officer": "", "registered_name": "", "source": ""}
    is_url = query.startswith("http")

    def _finalise(r: dict) -> dict:
        r.pop("registered_name", None)
        r.setdefault("company_name", query)
        r.setdefault("address", "")
        r.setdefault("officer", "")
        r.setdefault("source", "")
        return r

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

    # ── Step 2b: Website officer fallback (if CH didn't find one) ────────
    if is_url and not result.get("officer"):
        site_off = scrape_website(query, needs_name=False, needs_address=False, needs_officer=True)
        result = _merge(result, site_off)
        if _done(result):
            return _finalise(result)

    # ── Step 3: DuckDuckGo ───────────────────────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_addr or n_off:
        search_query = result.get("company_name") or query
        ddg = _search_and_scrape(search_query, needs_address=n_addr, needs_officer=n_off, engine="ddg")
        result = _merge(result, ddg)
        if _done(result):
            return _finalise(result)

    # ── Step 4: Serper (Google) ──────────────────────────────────────────
    _, n_addr, n_off = _needs(result)
    if n_addr or n_off:
        search_query = result.get("company_name") or query
        serper = _search_and_scrape(search_query, needs_address=n_addr, needs_officer=n_off, engine="serper")
        result = _merge(result, serper)

    return _finalise(result)
