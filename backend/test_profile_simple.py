#!/usr/bin/env python3
"""
Simple Profile Settings Test using Django Test Client
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json

User = get_user_model()

def print_test(name):
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

def print_success(msg):
    print(f"✓ {msg}")

def print_error(msg):
    print(f"✗ {msg}")

def print_info(msg):
    print(f"  {msg}")

# Get or create test user
print_test("Setup")
try:
    user = User.objects.filter(email='test@client.local').first()
    if not user:
        print_error("Test user not found. Please create test users first.")
        print_info("Run: python3 create_test_users.py")
        sys.exit(1)
    print_success(f"Found test user: {user.email} (ID: {user.id})")
except Exception as e:
    print_error(f"Error: {e}")
    sys.exit(1)

# Create API client
client = APIClient()
client.force_authenticate(user=user)

# Test 1: Get User Profile
print_test("GET /api/v1/auth/auth/user/ - Get Current Profile")
try:
    response = client.get('/api/v1/auth/auth/user/')
    print_info(f"Status: {response.status_code}")
    
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        print_success("Profile retrieved successfully")
        print_info(f"Email: {data.get('email')}")
        print_info(f"Username: {data.get('username')}")
        print_info(f"First Name: {data.get('first_name', 'N/A')}")
        print_info(f"Last Name: {data.get('last_name', 'N/A')}")
        print_info(f"Phone: {data.get('phone_number', 'N/A')}")
        print_info(f"Bio: {data.get('bio', 'N/A')[:50] if data.get('bio') else 'N/A'}")
        print_info(f"Country: {data.get('country', 'N/A')}")
        print_info(f"State: {data.get('state', 'N/A')}")
    else:
        print_error(f"Unexpected status: {response.status_code}")
        print_error(f"Response: {response.json()}")
except Exception as e:
    print_error(f"Exception: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Update User Profile
print_test("PATCH /api/v1/auth/auth/user/ - Update Profile")
try:
    update_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'phone_number': '+1234567890',
        'bio': 'This is a test bio from Python test script',
        'country': 'US',
        'state': 'California'
    }
    
    response = client.patch(
        '/api/v1/auth/auth/user/',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    print_info(f"Status: {response.status_code}")
    
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        print_success("Profile updated successfully")
        if 'message' in data:
            print_info(f"Message: {data['message']}")
        if 'user' in data:
            user_data = data['user']
            print_info(f"Updated First Name: {user_data.get('first_name')}")
            print_info(f"Updated Last Name: {user_data.get('last_name')}")
            print_info(f"Updated Phone: {user_data.get('phone_number')}")
    else:
        print_error(f"Unexpected status: {response.status_code}")
        print_error(f"Response: {response.json()}")
except Exception as e:
    print_error(f"Exception: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Verify Update Persisted
print_test("GET /api/v1/auth/auth/user/ - Verify Update Persisted")
try:
    response = client.get('/api/v1/auth/auth/user/')
    
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        print_success("Profile retrieved after update")
        print_info(f"First Name: {data.get('first_name')} (expected: Test)")
        print_info(f"Last Name: {data.get('last_name')} (expected: User)")
        print_info(f"Phone: {data.get('phone_number')} (expected: +1234567890)")
        
        # Verify
        if data.get('first_name') == 'Test':
            print_success("First name persisted correctly")
        else:
            print_error(f"First name mismatch: {data.get('first_name')} != Test")
            
        if data.get('last_name') == 'User':
            print_success("Last name persisted correctly")
        else:
            print_error(f"Last name mismatch: {data.get('last_name')} != User")
    else:
        print_error(f"Unexpected status: {response.status_code}")
except Exception as e:
    print_error(f"Exception: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Get Profile Update Requests
print_test("GET /api/v1/users/users/profile-update-requests/ - Get Update Requests")
try:
    response = client.get('/api/v1/users/users/profile-update-requests/')
    print_info(f"Status: {response.status_code}")
    
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        print_success("Update requests retrieved")
        if 'pending_requests' in data:
            print_info(f"Pending requests: {len(data['pending_requests'])}")
        else:
            print_info(f"Response: {data}")
    else:
        print_error(f"Unexpected status: {response.status_code}")
        print_error(f"Response: {response.json()}")
except Exception as e:
    print_error(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*60}")
print("Test Complete!")
print('='*60)

