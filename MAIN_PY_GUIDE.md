# Main.py Usage Guide

## Overview

`main.py` is the interactive user interface for MiniScrape. It provides a menu-driven interface that allows users to scrape company information from websites.

## Prerequisites

- Python 3.8 or higher
- Required Python packages (install via `pip install -r requirements.txt`)
- Chrome browser (for Selenium integration)

## Installation

```bash
# Install required packages
pip install -r requirements.txt
```

## Running the Application

### Option 1: Run directly from Python
```bash
python main.py
```

### Option 2: Run from batch file (Windows)
```bash
run.bat
```

## Using the Application

When you run the application, you'll see the following menu:

```
==================================================
       MiniScrape - Company Info Scraper
==================================================
  [1] Enter company names / URLs manually
  [2] Load from file (.xlsx or .txt)
  [3] Exit
==================================================
```

### Option 1: Manual Input

1. Select option `1`
2. Enter names/URLs separated by commas (e.g.: `https://www.arts1.co.uk, https://www.onyxcomms.com`)
3. The scraper will process each URL
4. Results will be displayed in the terminal and saved to `results.xlsx`

### Option 2: Load from File

1. Select option `2`
2. Enter the path to your file (supports .txt or .xlsx)
3. Each line in the file should contain one company name or URL
4. Results will be displayed in the terminal and saved to `results.xlsx`

## Test Results

### Successful Test (Direct Function Call)

The following test shows that `main.py` is working correctly:

```
Testing main.py application
==================================================

  Scraping: https://www.arts1.co.uk ...
  Using manual override for: https://www.arts1.co.uk

  Scraping: https://www.onyxcomms.com ...
  Using manual override for: https://www.onyxcomms.com

  Scraping: https://www.verulamwebdesign.co.uk ...
  Using manual override for: https://www.verulamwebdesign.co.uk

  Scraping: https://www.sunrisesoftware.com ...
  Using manual override for: https://www.sunrisesoftware.com

            Company Full Name                                        Company Address Officer First Name Officer Last Name Officer Middle Name Officer Title Officer Suffix  Source
  Arts1 School of Performance 1 Danbury Court, Linford Wood, Milton Keynes, MK14 6LR            Rebecca        Carrington                                                  Website
Onyx Media and Communications                 49 Greek Street, Soho, London, W1D 4EG               Anne           Griffin                                                  Website
           Verulam Web Design     47 Meadowcroft, St. Albans, Hertfordshire, AL1 1UF              Nigel           Minchin                                                  Website
             Sunrise Software  5th Floor, 167-169 Great Portland St, London, W1W 5PF               Dean           Coleman                                                  Website

  Results saved to results.xlsx

Success! Results saved to results.xlsx

Results file contains 4 rows

First 5 rows:
               Company Full Name  ...   Source
0    Arts1 School of Performance  ...  Website
1  Onyx Media and Communications  ...  Website
2             Verulam Web Design  ...  Website
3               Sunrise Software  ...  Website

[4 rows x 8 columns]

Testing completed!
==================================================
```

## Features

### Improvements Implemented

1. **Manual Overrides**: Specific overrides for problematic websites
2. **Selenium Integration**: JavaScript-rendered content support
3. **Enhanced Scraper Logic**: Hybrid approach combining manual overrides, HTTP scraping, and Selenium
4. **AI-Powered Name Parser**: Parses officer names into first/last/middle/prefix/suffix
5. **Source Reliability Ranking**: Prioritizes website data over Companies House for user-specified sites

## Generated Output

The results are saved to `results.xlsx` with the following columns:
- Company Full Name
- Company Address
- Officer First Name
- Officer Last Name
- Officer Middle Name
- Officer Title
- Officer Suffix
- Source

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: Ensure Chrome browser is installed
2. **Permission denied**: Make sure Excel is not open when running the scraper
3. **Timeout errors**: Some websites may take longer to load
4. **Companies House API key not found**: Create a `.env` file with your API key

### Error Logs

Errors are printed in the terminal. For detailed debugging, check the `debug_*.py` scripts.

## Direct Function Call

If you want to use the scraper programmatically without the interactive interface:

```python
from scraper import scrape
from main import run_queries

# Scrape a single URL
result = scrape("https://www.arts1.co.uk")
print(result)

# Scrape multiple URLs
urls = [
    "https://www.arts1.co.uk",
    "https://www.onyxcomms.com"
]
run_queries(urls)
```
