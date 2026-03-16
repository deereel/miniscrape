@echo off
cd /d "%~dp0"
echo MiniScrape Windows Environment Test
echo ===================================
echo.
echo 1. Current directory: %cd%
echo 2. Python executable: %PYTHONHOME%\python.exe
echo.
python -c "
import sys, os
print('Python version:', sys.version)
print('Executable path:', sys.executable)
print('Current directory:', os.getcwd())
print('Script directory:', os.path.dirname(os.path.abspath(__file__)))
"
echo.
echo 3. Running test_scrape.py...
python test_scrape.py
echo.
pause
