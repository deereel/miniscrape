@echo off
chcp 65001 >nul

echo.
echo ===============================================
echo         MiniScrape Web Application
echo ===============================================
echo.
echo Starting the MiniScrape web server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python and add it to your system PATH
    echo.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

REM Install/update dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some dependencies might have failed to install
    echo Please check for errors above
)

echo.
echo ===============================================
echo.
echo Web server is starting on port 5000
echo Open your browser and navigate to:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

REM Start the Flask application
python app.py

REM Deactivate virtual environment
deactivate
