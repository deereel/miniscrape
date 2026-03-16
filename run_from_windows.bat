@echo off
cd /d "%~dp0"
chcp 65001 >nul

echo MiniScrape - Running from Windows
echo =================================

echo 1. Current directory: %cd%
echo 2. Python version:
python --version

echo 3. Running scraper test...
python -c "
from scraper import scrape
result = scrape('https://www.arts1.co.uk')
print('Company:', result['company_name'])
print('Address:', result['address'])
print('Officer:', result['officer'])
print('Source:', result['source'])
"

echo.
echo 4. Running main.py test with file input...

echo https://www.arts1.co.uk>test_urls.txt
echo https://www.onyxcomms.com>>test_urls.txt

python -c "
from main import load_queries, run_queries
urls = load_queries('test_urls.txt')
print('Loaded', len(urls), 'URLs')
run_queries(urls)
"

echo.
echo 5. Results file:
if exist "results.csv" (
    python -c "
import pandas as pd
df = pd.read_csv('results.csv')
print('Records:', len(df))
for i, row in df.iterrows():
    print('  {}. {}'.format(i+1, row['Company Full Name']))
"
)

del test_urls.txt

echo.
echo 6. Complete!
pause
