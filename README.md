# MiniScrape

A fast and efficient web scraping application with AI-assisted extraction.

## Features

- AI-assisted address extraction using spaCy NER
- AI name parsing using nameparser library
- Source reliability ranking
- Page classification to avoid scraping irrelevant pages
- Company name deduplication
- Manual overrides for specific websites

## AI Agents

### AIAddressExtractionAgent
Uses spaCy NER to extract addresses from text. Prioritizes UK postcode-based extraction for reliability.

### AINameParserAgent
Parses person names using the nameparser library, extracting first, middle, last names, titles, and suffixes.

### AISourceRankingAgent
Ranks sources by reliability (Companies House: 90, LinkedIn: 85, Website: 95, Google snippet: 60, DuckDuckGo: 55).

### AIPageClassifierAgent
Classifies pages to determine if they contain relevant information (address, leadership, company info).

### AIDeduplicationAgent
Normalizes and deduplicates company names.

## Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage

```bash
# Run the web application
python app.py

# Run tests
python test_comprehensive.py
```
