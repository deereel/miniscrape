@echo off
cd /d "%~dp0"
chcp 65001 >nul
python windows_test.py
pause
