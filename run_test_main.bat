@echo off
cd /d "%~dp0"
chcp 65001 >nul
echo MiniScrape Test - Running main.py
echo =================================

echo.
echo Step 1: Creating temporary input file
echo.

echo https://www.arts1.co.uk>temp_input.txt
echo https://www.onyxcomms.com>>temp_input.txt

echo Step 2: Running main.py from test file
echo.
python -c "
from main import load_queries, run_queries
urls = load_queries('temp_input.txt')
print('Loaded', len(urls), 'URLs')
run_queries(urls)
"

echo.
echo Step 3: Checking results file
echo.
if exist "results.csv" (
    echo OK: results.csv created
    python -c "
import pandas as pd
df = pd.read_csv('results.csv')
print('Records:', len(df))
for i, row in df.iterrows():
    print('  Company:', row['Company Full Name'])
"
) else (
    echo ERROR: No results file created
)

echo.
echo Step 4: Cleaning up
del temp_input.txt

echo.
pause
