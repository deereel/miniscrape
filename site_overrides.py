#!/usr/bin/env python3
"""Manual site overrides for websites that the scraper can't parse correctly"""

SITE_OVERRIDES = {}


def get_site_override(url):
    """Check if there's a manual override for the given URL"""
    from urllib.parse import urlparse
    try:
        hostname = urlparse(url).netloc.replace('www.', '')
        for domain, data in SITE_OVERRIDES.items():
            if domain in hostname:
                return {
                    **data,
                    "registered_name": data.get("company_name", ""),
                    "source": "Website"
                }
    except Exception:
        pass
    return None


def get_site_override(url):
    """Check if there's a manual override for the given URL"""
    from urllib.parse import urlparse
    try:
        hostname = urlparse(url).netloc.replace('www.', '')
        for domain, data in SITE_OVERRIDES.items():
            if domain in hostname:
                # Return override with source set to website
                return {
                    **data,
                    "registered_name": data["company_name"],
                    "source": "Website"
                }
    except Exception:
        pass
    return None
