import requests
import time

# Wait for server to be fully ready
time.sleep(2)

# Test the main page
try:
    response = requests.get('http://localhost:5000')
    print(f"Main page status: {response.status_code}")
    if response.status_code == 200:
        print("Application is running successfully!")
        print(f"Page content contains form: {'<form' in response.text}")
        print(f"Page content length: {len(response.text)} characters")
    else:
        print(f"Error accessing application: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
