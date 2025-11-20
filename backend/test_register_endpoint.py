#!/usr/bin/env python3
"""
Quick test script to verify registration endpoint
"""
import requests
import json

url = "http://localhost:8000/api/v1/auth/register/"

test_data = {
    "username": "testuser123",
    "email": "test@example.com",
    "password": "testpass123"
}

print(f"Testing registration endpoint: {url}")
print(f"Data: {json.dumps({**test_data, 'password': '***'}, indent=2)}")
print()

try:
    response = requests.post(url, json=test_data, headers={"Content-Type": "application/json"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to backend")
    print("   Make sure backend is running: python3 manage.py runserver 0.0.0.0:8000")
except Exception as e:
    print(f"❌ ERROR: {e}")

