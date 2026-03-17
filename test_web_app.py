#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# Get CSRF token from homepage
response = requests.get('http://localhost:5000')
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
print('CSRF Token:', csrf_token)

# Submit the form with test URLs
data = {
    'csrf_token': csrf_token,
    'urls': 'acuitytraining.co.uk\nyork-it-services.co.uk\ndevereintellica.com\nsangersaah.co.uk',
    'submit': 'Scrape'
}

response = requests.post('http://localhost:5000', data=data)
print('Response status:', response.status_code)
print('Response URL:', response.url)

# Write response to file for debugging
with open('debug_response.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print('Response saved to debug_response.html')

# Check if results are in response
if 'Results' in response.text:
    print('Results page loaded successfully!')
else:
    print('Results not found in response')
