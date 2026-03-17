#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# Get homepage
response = requests.get('http://localhost:5000')
soup = BeautifulSoup(response.text, 'html.parser')

# Get CSRF token
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
print('CSRF Token:', csrf_token)

# Submit form
data = {
    'csrf_token': csrf_token,
    'urls': 'acuitytraining.co.uk\nyork-it-services.co.uk\ndevereintellica.com\nsangersaah.co.uk',
    'submit': 'Scrape'
}

response = requests.post('http://localhost:5000', data=data, cookies=response.cookies)
print('Response status:', response.status_code)

# Check for form errors
soup = BeautifulSoup(response.text, 'html.parser')
errors = soup.find_all(class_='invalid-feedback')
if errors:
    print('Form errors:', [e.get_text(strip=True) for e in errors])

# Check if we got results
if 'Scraping Results' in response.text:
    print('Results page loaded successfully')
else:
    print('Still on form page')

# Save response to file for debugging
with open('form_response.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
    print('Response saved to form_response.html')
