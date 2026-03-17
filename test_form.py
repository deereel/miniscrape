#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# First, get the CSRF token
response = requests.get('http://localhost:5000')
print('GET Response Status:', response.status_code)
print('GET Response Text (first 1000 characters):', repr(response.text[:1000]))

soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

print('CSRF Token:', csrf_token)

# Then, submit the form
data = {
    'csrf_token': csrf_token,
    'urls': 'https://www.example.com',
    'submit': 'Scrape'
}

headers = {
    'Cookie': response.headers.get('Set-Cookie'),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print('Submitting form...')
response = requests.post('http://localhost:5000', data=data, headers=headers)

print('POST Response Status:', response.status_code)
print('POST Response Headers:', dict(response.headers))
print('POST Response Content (first 1000 characters):', repr(response.text[:1000]))
