"""
MiniScrape - Company Information Scraper
Run directly: python main.py
Or double-click: run.bat
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from scraper import scrape

load_dotenv()
CH_API_KEY = os.environ.get("COMPANIES_HOUSE_API_KEY", "")


def load_queries(input_file: str) -> list[str]:
    ext = input_file.rsplit(".", 1)[-1].lower()
    if ext in ("xlsx", "xls"):
        df = pd.read_excel(input_file, header=None)
        return df.iloc[:, 0].dropna().astype(str).tolist()
    with open(input_file, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run_queries(queries: list[str]):
    rows = []
    for q in queries:
        print(f"\n  Scraping: {q} ...")
        result = scrape(q)
        officer = result.get("officer", "")
        # Use AI-powered name parser to split first/last names
        from scraper import _parse_person_name
        parsed = _parse_person_name(officer)
        rows.append({
            "Company Full Name": result.get("company_name", ""),
            "Company Address":   result.get("address", ""),
            "Officer First Name": parsed["first"],
            "Officer Last Name":  parsed["last"],
            "Officer Middle Name": parsed["middle"],
            "Officer Title": parsed["prefix"],
            "Officer Suffix": parsed["suffix"],
            "Source":             result.get("source", ""),
        })

    df = pd.DataFrame(rows)
    print("\n" + df.to_string(index=False))

    out = "results.xlsx"
    df.to_excel(out, index=False)
    print(f"\n  Results saved to {out}")


def print_menu():
    print("\n" + "=" * 50)
    print("       MiniScrape - Company Info Scraper")
    print("=" * 50)
    print("  [1] Enter company names / URLs manually")
    print("  [2] Load from file (.xlsx or .txt)")
    print("  [3] Exit")
    print("=" * 50)


def main():
    while True:
        print_menu()
        choice = input("  Choose an option: ").strip()

        if choice == "1":
            raw = input("\n  Enter names/URLs separated by commas:\n  > ").strip()
            if not raw:
                print("  No input provided.")
                continue
            queries = [q.strip() for q in raw.split(",") if q.strip()]
            run_queries(queries)

        elif choice == "2":
            path = input("\n  Enter file path (.xlsx or .txt):\n  > ").strip().strip('"')
            if not os.path.exists(path):
                print(f"  File not found: {path}")
                continue
            try:
                queries = load_queries(path)
                print(f"  Loaded {len(queries)} entries.")
                run_queries(queries)
            except Exception as e:
                print(f"  Error reading file: {e}")

        elif choice == "3":
            print("\n  Goodbye!\n")
            break

        else:
            print("  Invalid option, please choose 1, 2, or 3.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
