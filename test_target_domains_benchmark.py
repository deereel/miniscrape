#!/usr/bin/env python3
import re
import time
import os
import json

from fast_scraper import scrape as fast_scrape
from scraper import scrape as deep_scrape

# Reset learning cache before benchmark to avoid stale cross-domain pollution
cache_file = os.path.join(os.path.dirname(__file__), 'learning_cache.json')
if os.path.exists(cache_file):
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump({}, f)

sites = [
    "armonia.co.uk",
    "creative-bridge.com",
    "robotindustrial.co.za",
    "andersonacoustics.co.uk",
    "exmoortrim.co.uk",
    "cedartreehospitality.com",
    "purplespace.org",
    "hoge100.co.uk",
    "careercheck.co.uk",
    "dysk.co.uk",
    "blossomhouseschool.co.uk",
    "ballyhoo-pr.co.uk",
    "charnwood-milling.co.uk",
    "argolin.com",
    "booth-ac.com",
    "independentlifting.com",
    "beeteealarmsltd.co.uk"
]

expected = {
    "armonia.co.uk": {
        "company": "Armonia Limited",
        "officer_tokens": ["Diane", "Lawrie-Hey"],
    },
    "creative-bridge.com": {
        "company": "Creative Bridge Ltd",
        "officer_tokens": ["Timothy", "Perutz"],
    },
    "robotindustrial.co.za": {
        "company": "Robot Industrial Supplies (Pty) Ltd",
        "officer_tokens": ["Mark", "Jackson"],
    },
    "andersonacoustics.co.uk": {
        "company": "Anderson Acoustics Limited",
        "officer_tokens": ["Robin", "Monaghan"],
    },
    "exmoortrim.co.uk": {
        "company": "Exmoor Trim Limited",
        "officer_tokens": ["Andrew", "Horton"],
    },
    "cedartreehospitality.com": {
        "company": "Cedar Tree Hospitality",
        "officer_tokens": ["Mohsen", "Ghosen"],
    },
    "purplespace.org": {
        "company": "PURPLESPACE LIMITED",
        "officer_tokens": ["Brendan", "Roach"],
    },
    "hoge100.co.uk": {
        "company": "Hoge 100 Business Systems Ltd",
        "officer_tokens": ["Stuart", "Wild"],
    },
    "careercheck.co.uk": {
        "company": "Career Check Limited",
        "officer_tokens": ["Clive", "Jackson"],
    },
    "dysk.co.uk": {
        "company": "Dysk Plc",
        "officer_tokens": ["Timothy", "Gurney"],
    },
    "blossomhouseschool.co.uk": {
        "company": "Blossom House School Limited",
        "officer_tokens": ["Joey", "Burgess"],
    },
    "ballyhoo-pr.co.uk": {
        "company": "Ballyhoo PR",
        "officer_tokens": ["Emma", "Speirs"],
    },
    "charnwood-milling.co.uk": {
        "company": "Charnwood Milling Company Ltd",
        "officer_tokens": ["Philip", "Newton"],
    },
    "argolin.com": {
        "company": "Argolin Limited",
        "officer_tokens": ["Julian", "Argolin"],
    },
    "booth-ac.com": {
        "company": "Booth Air Conditioning Limited",
        "officer_tokens": ["Gordon", "Booth"],
    },
    "independentlifting.com": {
        "company": "Independent Lifting Services Limited",
        "officer_tokens": ["Barry", "Thompson"],
    },
    "beeteealarmsltd.co.uk": {
        "company": "Bee Tee Alarms Ltd",
        "officer_tokens": ["Mark", "Taylor"],
    }
}

postcode_pattern = re.compile(r"[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2}", re.I)

print("Benchmarking target domains:")
print("{:<25} {:<15} {:<15} {:<30} {:<60}".format("Company Domain", "CEO First Name", "CEO Last Name", "Company Name", "Company Address"))

summary = []
for site in sites:
    for mode in ["fast", "deep"]:
        scrape_fn = fast_scrape if mode == "fast" else deep_scrape
        url = f"https://{site}"
        start = time.perf_counter()
        result = scrape_fn(url)
        elapsed = time.perf_counter() - start

        company = result.get("company_name", "") or "" 
        officer = result.get("officer", "") or ""
        address = result.get("address", "") or ""
        confidence = result.get("confidence", {})
        company_conf = confidence.get("company_name", 0)
        address_conf = confidence.get("address", 0)
        officer_conf = confidence.get("officer", 0)
        max_conf = max(company_conf, address_conf, officer_conf)

        postcode_ok = bool(postcode_pattern.search(address))
        company_viable = expected[site]["company"].lower() in company.lower() or company.lower() in expected[site]["company"].lower()
        officer_tokens = expected[site]["officer_tokens"]
        officer_viable = all(tok.lower() in officer.lower() for tok in officer_tokens)

        status = "PASS" if company_viable and officer_viable and postcode_ok else "FAIL"

        officer_parts = officer.split()
        officer_first = officer_parts[0] if len(officer_parts) > 0 else ""
        officer_last = officer_parts[-1] if len(officer_parts) > 1 else ""

        summary.append({
            "company_domain": site,
            "ceo_first_name": officer_first,
            "ceo_last_name": officer_last,
            "company_name": company,
            "company_address": address,
            "mode": mode,
            "status": status,
            "time": elapsed,
            "confidence": max_conf
        })

        print("{:<25} {:<15} {:<15} {:<30} {:<60}".format(site, officer_first, officer_last, company, address))

print("\nSummary per site:")
for site in sites:
    entries = [r for r in summary if r["company_domain"] == site]
    for r in entries:
        print(f"{site} ({r['mode']}): status={r['status']} time={r['time']:.2f}s conf={r['confidence']:.2f} company={r['company_name']} officer={r['ceo_first_name']} {r['ceo_last_name']}" )

# Save to CSV
import csv
with open("test_target_domains_benchmark.csv", "w", newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=["Company Domain", "CEO First Name", "CEO Last Name", "Company Name", "Company Address", "Mode", "Status", "Time", "Confidence"])
    w.writeheader()
    for row in summary:
        w.writerow({
            "Company Domain": row.get("company_domain", ""),
            "CEO First Name": row.get("ceo_first_name", ""),
            "CEO Last Name": row.get("ceo_last_name", ""),
            "Company Name": row.get("company_name", ""),
            "Company Address": row.get("company_address", ""),
            "Mode": row.get("mode", ""),
            "Status": row.get("status", ""),
            "Time": f"{row.get('time', 0):.2f}",
            "Confidence": f"{row.get('confidence', 0):.2f}"
        })

print("\nSaved results to test_target_domains_benchmark.csv")
