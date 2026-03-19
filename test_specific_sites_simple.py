#!/usr/bin/env python3
from fast_scraper import scrape
import csv

# Sites from user's expected results
sites = [
    "aquaterra.co.uk",
    "drewry.co.uk",
    "weareyellowball.com",
    "vistechcooling.co.uk",
    "avs-uk.co.uk"
]

# Expected results
expected = [
    ("aquaterra.co.uk", "Stephen", "Taylor", "AquaTerra Group Ltd", "AquaTerra House, Tofthills Avenue, Aberdeen, AB51 0QP"),
    ("drewry.co.uk", "Tim", "Power", "Drewry Shipping Consultants Ltd", "35-41 Folgate Street, London, E1 6BX"),
    ("weareyellowball.com", "Owen", "Hunnam", "Yellowball", "Borough Yards, 13 Dirty Lane, London, SE1 9PA"),
    ("vistechcooling.co.uk", "Martin", "Crunden", "Vistech Cooling Systems Ltd", "Unit 1, Blackhouse Farm, Blackhouse Road, RH13 6HS"),
    ("avs-uk.co.uk", "Ian", "Baker", "Associated Vending Services Ltd", "Unit 10, Tame Valley Business Centre, Tamworth, B77 5BY")
]

# Test each site
results = []
for site in sites:
    print(f"Scraping {site}...")
    data = scrape(site)
    results.append(data)

# Print comparison without Unicode characters
print("\n" + "="*80)
print(f"{'Site':20} {'Expected Company':30} {'Actual Company':30} {'Match'}")
print("-"*80)
for i, (expected_site, exp_first, exp_last, exp_company, exp_address) in enumerate(expected):
    result = results[i]
    actual_company = result.get("company_name", "")
    match = "OK" if exp_company.lower() in actual_company.lower() or actual_company.lower() in exp_company.lower() else "FAIL"
    print(f"{expected_site:20} {exp_company:30} {actual_company:30} {match}")

print("\n" + "="*80)
print(f"{'Site':20} {'Expected Officer':25} {'Actual Officer':25} {'Match'}")
print("-"*80)
for i, (expected_site, exp_first, exp_last, exp_company, exp_address) in enumerate(expected):
    result = results[i]
    actual_officer = result.get("officer", "")
    expected_officer = f"{exp_first} {exp_last}"
    match = "OK" if expected_officer.lower() in actual_officer.lower() or actual_officer.lower() in expected_officer.lower() else "FAIL"
    print(f"{expected_site:20} {expected_officer:25} {actual_officer:25} {match}")

print("\n" + "="*80)
print(f"{'Site':20} {'Expected Address':40} {'Actual Address':40}")
print("-"*80)
for i, (expected_site, exp_first, exp_last, exp_company, exp_address) in enumerate(expected):
    result = results[i]
    actual_address = result.get("address", "")
    print(f"{expected_site:20} {exp_address:40} {actual_address:40}")

# Save results to CSV
with open("test_specific_sites_simple_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Site", "Expected First", "Expected Last", "Expected Company", "Expected Address", "Actual Company", "Actual Officer", "Actual Address"])
    for i, (expected_site, exp_first, exp_last, exp_company, exp_address) in enumerate(expected):
        result = results[i]
        writer.writerow([expected_site, exp_first, exp_last, exp_company, exp_address, result.get("company_name"), result.get("officer"), result.get("address")])

print("\nResults saved to test_specific_sites_simple_results.csv")
