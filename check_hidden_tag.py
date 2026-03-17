#!/usr/bin/env python3
"""Check what form.hidden_tag() generates"""

import requests
import re

# Get main page
response = requests.get('http://localhost:5000')
print("Hidden tag content:")

# Find the form tags and look for hidden inputs
form_match = re.search(r'<form.*?>(.*?)</form>', response.text, re.DOTALL)
if form_match:
    form_content = form_match.group(1)
    hidden_inputs = re.findall(r'<input.*?type=["\']hidden["\'].*?>', form_content, re.IGNORECASE)
    for input_tag in hidden_inputs:
        print(input_tag)
