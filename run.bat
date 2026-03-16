@echo off
title MiniScrape - Company Info Scraper
cd /d "%~dp0"
chcp 65001 >nul
echo MiniScrape - Company Information Scraper
echo =======================================
echo.
python main.py
echo.
echo.
pause
