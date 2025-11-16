#!/usr/bin/env python3
"""
Test script for Profile Settings functionality.

Tests:
1. GET /api/v1/auth/user/ - Get current user profile
2. PATCH /api/v1/auth/user/ - Update user profile
3. GET /api/v1/users/profile-update-requests/ - Get pending update requests

Usage:
    python3 test_profile_settings.py
"""

import os
import sys
import django
import requests
import json
from typing import Dict, Any, Optional

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def print_test(msg):
    print(f"\n{BOLD}{BLUE}▶ Testing: {msg}{RESET}")

def get_or_create_test_user():
    """Get or create a test user for testing."""
    try:
        user = User.objects.filter(email='test_profile@example.com').first()
        if not user:
            user = User.objects.create_user(
                username='test_profile_user',
                email='test_profile@example.com',
                password='TestPassword123!',
                role='client',
                first_name='Test',
                last_name='User'
            )
            print_success(f"Created test user: {user.email}")
        else:
            print_info(f"Using existing test user: {user.email}")
        return user
    except Exception as e:
        print_error(f"Failed to create test user: {e}")
        return None

def test_get_user_profile(api_client: APIClient, user: User) -> bool:
    """Test GET /api/v1/auth/user/ endpoint."""
    print_test("GET /api/v1/auth/user/ - Get current user profile")
    
    try:
        response = api_client.get('/api/v1/auth/user/')
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Response keys: {list(data.keys())}")
            
            # Check for expected fields
            expected_fields = ['id', 'email', 'username']
            missing_fields = [f for f in expected_fields if f not in data]
            
            if missing_fields:
                print_error(f"Missing fields: {missing_fields}")
                return False
            
            # Check for profile fields
            profile_fields = ['first_name', 'last_name', 'phone_number', 'bio', 'country', 'state']
            found_fields = [f for f in profile_fields if f in data]
            print_info(f"Profile fields found: {found_fields}")
            
            print_success("Profile data retrieved successfully")
            print_info(f"Email: {data.get('email')}")
            print_info(f"Username: {data.get('username')}")
            print_info(f"Full Name: {data.get('full_name', 'N/A')}")
            print_info(f"Phone: {data.get('phone_number', 'N/A')}")
            print_info(f"Bio: {data.get('bio', 'N/A')[:50] if data.get('bio') else 'N/A'}")
            
            return True
        else:
            print_error(f"Unexpected status: {response.status_code}")
            print_error(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_update_user_profile(api_client: APIClient, user: User) -> bool:
    """Test PATCH /api/v1/auth/user/ endpoint."""
    print_test("PATCH /api/v1/auth/user/ - Update user profile")
    
    try:
        # Prepare update data
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890',
            'bio': 'This is a test bio for profile settings testing.',
            'country': 'US',
            'state': 'California'
        }
        
        print_info(f"Updating with data: {json.dumps(update_data, indent=2)}")
        
        response = api_client.patch(
            '/api/v1/auth/user/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            
            # Check response structure
            if 'message' in data:
                print_success(f"Message: {data['message']}")
            
            if 'user' in data:
                updated_user = data['user']
                print_info("Updated user data received")
                
                # Verify updates
                if updated_user.get('first_name') == update_data['first_name']:
                    print_success("First name updated correctly")
                else:
                    print_error(f"First name mismatch: {updated_user.get('first_name')} != {update_data['first_name']}")
                
                if updated_user.get('last_name') == update_data['last_name']:
                    print_success("Last name updated correctly")
                else:
                    print_error(f"Last name mismatch: {updated_user.get('last_name')} != {update_data['last_name']}")
            
            # Verify in database
            user.refresh_from_db()
            from users.models import UserProfile
            try:
                profile = user.user_main_profile
                print_info(f"Database - First Name: {user.first_name}")
                print_info(f"Database - Last Name: {user.last_name}")
                print_info(f"Database - Phone: {profile.phone_number if profile else 'N/A'}")
                print_info(f"Database - Bio: {profile.bio[:50] if profile and profile.bio else 'N/A'}")
                
                if user.first_name == update_data['first_name']:
                    print_success("Database updated correctly (first_name)")
                else:
                    print_error(f"Database first_name mismatch: {user.first_name} != {update_data['first_name']}")
                
            except UserProfile.DoesNotExist:
                print_error("UserProfile does not exist in database")
            
            return True
        else:
            print_error(f"Unexpected status: {response.status_code}")
            print_error(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_profile_update_requests(api_client: APIClient, user: User) -> bool:
    """Test GET /api/v1/users/profile-update-requests/ endpoint."""
    print_test("GET /api/v1/users/profile-update-requests/ - Get pending update requests")
    
    try:
        response = api_client.get('/api/v1/users/profile-update-requests/')
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            
            if 'pending_requests' in data:
                requests = data['pending_requests']
                print_info(f"Found {len(requests)} pending requests")
                
                if requests:
                    for req in requests:
                        print_info(f"  - Request ID: {req.get('id')}, Status: {req.get('status')}")
                else:
                    print_info("No pending requests (this is normal)")
                
                return True
            else:
                print_error("Response missing 'pending_requests' key")
                print_error(f"Response: {data}")
                return False
        else:
            print_error(f"Unexpected status: {response.status_code}")
            try:
                print_error(f"Response: {response.json()}")
            except:
                print_error(f"Response: {response.content}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_profile_fields_persistence(api_client: APIClient, user: User) -> bool:
    """Test that profile fields persist after update."""
    print_test("Profile Fields Persistence - Verify data persists")
    
    try:
        # First, get the profile
        get_response = api_client.get('/api/v1/auth/user/')
        if get_response.status_code != status.HTTP_200_OK:
            print_error("Failed to get profile")
            return False
        
        original_data = get_response.json()
        print_info(f"Original first_name: {original_data.get('first_name')}")
        print_info(f"Original phone_number: {original_data.get('phone_number')}")
        
        # Update with new values
        update_data = {
            'first_name': 'Persistent',
            'phone_number': '+9876543210',
            'bio': 'This bio should persist after update.'
        }
        
        update_response = api_client.patch(
            '/api/v1/auth/user/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        if update_response.status_code != status.HTTP_200_OK:
            print_error("Failed to update profile")
            return False
        
        # Get profile again to verify persistence
        get_response2 = api_client.get('/api/v1/auth/user/')
        if get_response2.status_code != status.HTTP_200_OK:
            print_error("Failed to get profile after update")
            return False
        
        updated_data = get_response2.json()
        print_info(f"Updated first_name: {updated_data.get('first_name')}")
        print_info(f"Updated phone_number: {updated_data.get('phone_number')}")
        
        # Verify persistence
        if updated_data.get('first_name') == update_data['first_name']:
            print_success("First name persisted correctly")
        else:
            print_error(f"First name did not persist: {updated_data.get('first_name')} != {update_data['first_name']}")
            return False
        
        if updated_data.get('phone_number') == update_data['phone_number']:
            print_success("Phone number persisted correctly")
        else:
            print_error(f"Phone number did not persist: {updated_data.get('phone_number')} != {update_data['phone_number']}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all profile settings tests."""
    print(f"\n{BOLD}{BLUE}{'='*60}")
    print("Profile Settings Test Suite")
    print(f"{'='*60}{RESET}\n")
    
    # Get or create test user
    user = get_or_create_test_user()
    if not user:
        print_error("Cannot proceed without test user")
        return False
    
    # Create API client and authenticate
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    
    results = []
    
    # Run tests
    results.append(("Get User Profile", test_get_user_profile(api_client, user)))
    results.append(("Update User Profile", test_update_user_profile(api_client, user)))
    results.append(("Get Profile Update Requests", test_get_profile_update_requests(api_client, user)))
    results.append(("Profile Fields Persistence", test_profile_fields_persistence(api_client, user)))
    
    # Summary
    print(f"\n{BOLD}{BLUE}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{BOLD}Results: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print_success("All tests passed! ✓")
        return True
    else:
        print_error(f"{total - passed} test(s) failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

