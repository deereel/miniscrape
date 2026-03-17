# Running the MiniScrape Application

## Quick Startup Guide

### Option 1: Quick Start (No Virtual Environment)
If you don't want to use a virtual environment, you can run the application directly:

1. **Ensure dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application:**
   ```bash
   python app.py
   ```

3. **Access the application:**
   Open your browser and go to: `http://localhost:5000`

---

### Option 2: Virtual Environment (Recommended for Development)

#### Creating the Virtual Environment
```bash
# Create virtual environment (run once)
python -m venv venv
```

#### Activating the Virtual Environment

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### Installing Dependencies
```bash
pip install -r requirements.txt
```

#### Starting the Application
```bash
python app.py
```

**Accessing the Application:**
Open your browser and navigate to: `http://localhost:5000`

---

## Complete Workflow

### 1. Start the Application
```bash
# Step 1: Activate virtual environment (if using)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Step 2: Run the application
python app.py
```

### 2. Use the Application

**Basic Usage:**
1. Go to `http://localhost:5000` in your browser
2. Enter URLs to scrape (one per line or separated by commas)
3. Click "Scrape" button
4. View results on the results page
5. Export results to CSV or Excel

**Advanced Options:**
- Upload a file containing URLs (TXT, CSV, or Excel formats)
- Enable/Disable scraping of specific fields
- View detailed scraping progress

### 3. Stop the Application
- Press `Ctrl + C` in the terminal
- Deactivate virtual environment (if using):
  ```bash
  deactivate
  ```

---

## Troubleshooting

### Common Issues and Solutions

**1. Port already in use (Windows):**
```bash
# Find which process is using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /F /PID <PID>
```

**2. Missing Dependencies:**
```bash
pip install -r requirements.txt
```

**3. Virtual Environment Not Activated:**
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

**4. Browser Connection Issues:**
- Make sure `app.py` is still running in the terminal
- Check for any error messages in the terminal
- Try refreshing your browser

**5. Python Version Issues:**
- The application is tested with Python 3.8+
- If you encounter syntax errors, verify your Python version:
  ```bash
  python --version
  ```

---

## Testing

### Run All Tests
```bash
python test_comprehensive.py
```

### Run Specific Tests
```bash
# Test validation schemas
python test_validation_demo.py

# Test scraping functionality
python test_scrape.py

# Test web application functionality
python test_web_app_functionality.py
```

---

## Browser Compatibility

The application works with modern browsers:
- Chrome (recommended)
- Firefox
- Safari
- Edge

---

## Laragon Integration (Optional)

If you want to use Laragon for local development:

1. **Install Laragon:** Download from [laragon.org](https://laragon.org/)
2. **Add Project:** Copy the MiniScrape folder to Laragon's `www` directory
3. **Start Laragon:** Open Laragon and click "Start"
4. **Create Virtual Host:**
   - In Laragon, go to Menu > Apache > Sites Enabled
   - Create a virtual host entry for the project
5. **Access via Browser:** `http://miniscrape.test`

**Note:** You may need to adjust Laragon's Python version in `C:\laragon\bin\python\python.exe`

---

## Performance Tips

- For large batches of URLs, use file upload instead of manual entry
- If scraping is slow, reduce the number of URLs per batch
- Close unnecessary browser tabs and applications
- For best performance, use Chrome or Firefox

---

## Support

If you encounter issues not covered in this guide:
1. Check the terminal for error messages
2. Review the `requirements.txt` file for missing dependencies
3. Ensure you're using Python 3.8 or later
4. Try reinstalling dependencies: `pip install -r requirements.txt --force-reinstall`

---

*Last updated: March 2024*
