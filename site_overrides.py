#!/usr/bin/env python3
"""Manual site overrides for websites that the scraper can't parse correctly"""

SITE_OVERRIDES = {
    "arts1.co.uk": {
        "company_name": "Arts1 School of Performance",
        "address": "1 Danbury Court, Linford Wood, Milton Keynes, MK14 6LR",
        "officer": "Rebecca Carrington"
    },
    "onyxcomms.com": {
        "company_name": "Onyx Media and Communications",
        "address": "49 Greek Street, Soho, London, W1D 4EG",
        "officer": "Anne Griffin"
    },
    "verulamwebdesign.co.uk": {
        "company_name": "Verulam Web Design",
        "address": "47 Meadowcroft, St. Albans, Hertfordshire, AL1 1UF",
        "officer": "Nigel Minchin"
    },
    "sunrisesoftware.com": {
        "company_name": "Sunrise Software",
        "address": "5th Floor, 167-169 Great Portland St, London, W1W 5PF",
        "officer": "Dean Coleman"
    }
}


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
