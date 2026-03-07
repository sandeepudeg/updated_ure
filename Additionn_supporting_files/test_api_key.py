#!/usr/bin/env python3
"""Test data.gov.in API key"""

import requests
import json

api_key = '579b464db66ec23bdd000001d311dcc710d34a03456b277835b7abd3'
url = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'

params = {
    'api-key': api_key,
    'format': 'json',
    'limit': 5
}

print("Testing data.gov.in API...")
print(f"URL: {url}")
print(f"Commodity: Tomato, State: Maharashtra\n")

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])
        print(f"Records Found: {len(records)}\n")
        
        if records:
            print("Sample Record:")
            print(json.dumps(records[0], indent=2))
        else:
            print("No records found")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
