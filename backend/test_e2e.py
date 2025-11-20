#!/usr/bin/env python3
"""
End-to-End Testing Script for Writing System
Tests complete user journeys for both frontend and backend.
"""
import os
import sys
import django
import json
import requests
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from websites.models import Website

User = get_user_model()

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
FRONTEND_URL = "http://localhost:5173"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== {name} ==={Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.END}")

def test_backend_health():
    """Test if backend is running and accessible."""
    print_test("Backend Health Check")
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is running - Status: {response.status_code}")
            data = response.json()
            print_info(f"API Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Backend is not running or not accessible")
        print_info("Start backend with: python3 manage.py runserver 0.0.0.0:8000")
        return False
    except Exception as e:
        print_error(f"Backend health check failed: {e}")
        return False

def test_database():
    """Test database connectivity and data."""
    print_test("Database Status")
    try:
        user_count = User.objects.count()
        website_count = Website.objects.count()
        
        print_success(f"Database connected")
        print_info(f"Total Users: {user_count}")
        print_info(f"Total Websites: {website_count}")
        
        # Check for active website
        active_website = Website.objects.filter(is_active=True).first()
        if active_website:
            print_success(f"Active Website: {active_website.name} ({active_website.domain})")
        else:
            print_error("No active website found - users need a website")
            # Create a default website
            website = Website.objects.create(
                name="Default Website",
                domain="localhost",
                is_active=True,
                slug="default"
            )
            print_success(f"Created default website: {website.name}")
        
        return True
    except Exception as e:
        print_error(f"Database check failed: {e}")
        return False

def test_registration():
    """Test user registration flow."""
    print_test("User Registration")
    client = Client()
    
    timestamp = int(datetime.now().timestamp())
    register_data = {
        'username': f'testuser_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'TestPassword123!'
    }
    
    try:
        response = client.post(
            '/api/v1/auth/register/',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        
        if response.status_code in [200, 201]:
            print_success(f"Registration successful - Status: {response.status_code}")
            data = response.json()
            print_info(f"User ID: {data.get('user_id', 'Unknown')}")
            print_info(f"Email: {data.get('email', register_data['email'])}")
            return register_data
        else:
            print_error(f"Registration failed - Status: {response.status_code}")
            print_info(f"Response: {response.content.decode()[:200]}")
            return None
    except Exception as e:
        print_error(f"Registration test failed: {e}")
        return None

def test_login(credentials):
    """Test user login flow."""
    print_test("User Login")
    client = Client()
    
    if not credentials:
        print_error("No credentials provided - skipping login test")
        return None
    
    login_data = {
        'email': credentials['email'],
        'password': credentials['password']
    }
    
    try:
        response = client.post(
            '/api/v1/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token') or data.get('access')
            if token:
                print_success(f"Login successful - Token received")
                print_info(f"User: {data.get('user', {}).get('username', 'Unknown')}")
                return token
            else:
                print_error("Login successful but no token in response")
                return None
        else:
            print_error(f"Login failed - Status: {response.status_code}")
            print_info(f"Response: {response.content.decode()[:200]}")
            return None
    except Exception as e:
        print_error(f"Login test failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoints with token."""
    print_test("Protected Endpoint Access")
    
    if not token:
        print_error("No token provided - skipping protected endpoint test")
        return False
    
    try:
        response = requests.get(
            f"{API_BASE}/users/profile/",
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        
        if response.status_code == 200:
            print_success(f"Protected endpoint accessible - Status: {response.status_code}")
            data = response.json()
            print_info(f"User Profile: {data.get('username', 'Unknown')}")
            return True
        else:
            print_error(f"Protected endpoint failed - Status: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Protected endpoint test failed: {e}")
        return False

def test_admin_panel():
    """Test admin panel access."""
    print_test("Admin Panel Access")
    client = Client()
    
    # Try to login as admin
    admin = User.objects.filter(role__in=['admin', 'superadmin']).first()
    if not admin:
        print_info("No admin user found - creating test admin")
        website = Website.objects.filter(is_active=True).first()
        if not website:
            print_error("No active website - cannot create admin")
            return False
        
        admin = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='AdminPassword123!',
            role='admin',
            website=website,
            is_active=True,
            is_staff=True
        )
        print_success(f"Created test admin: {admin.username}")
    
    try:
        client.force_login(admin)
        response = client.get('/admin/')
        if response.status_code == 200:
            print_success(f"Admin panel accessible - Status: {response.status_code}")
            return True
        else:
            print_error(f"Admin panel failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Admin panel test failed: {e}")
        return False

def test_api_endpoints():
    """Test various API endpoints."""
    print_test("API Endpoints Check")
    client = Client()
    
    endpoints = [
        ('/', 'API Root'),
        ('/docs/swagger/', 'Swagger Docs'),
        ('/auth/login/', 'Login Endpoint'),
    ]
    
    results = []
    for endpoint, name in endpoints:
        try:
            response = client.get(f'/api/v1{endpoint}')
            if response.status_code in [200, 302, 401, 405]:  # Various valid responses
                print_success(f"{name}: Accessible (Status: {response.status_code})")
                results.append(True)
            else:
                print_error(f"{name}: Unexpected status {response.status_code}")
                results.append(False)
        except Exception as e:
            print_error(f"{name}: Failed - {e}")
            results.append(False)
    
    return all(results)

def test_frontend():
    """Test if frontend is accessible."""
    print_test("Frontend Health Check")
    
    urls = [FRONTEND_URL, "http://localhost:5174"]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"Frontend is running at {url}")
                return True
        except requests.exceptions.ConnectionError:
            continue
        except Exception as e:
            continue
    
    print_error("Frontend is not running or not accessible")
    print_info("Start frontend with: cd writing_system_frontend && npm run dev")
    return False

def test_django_checks():
    """Run Django system checks."""
    print_test("Django System Checks")
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        err = StringIO()
        call_command('check', stdout=out, stderr=err)
        
        output = out.getvalue()
        errors = err.getvalue()
        
        if not errors:
            print_success("Django system checks passed")
            return True
        else:
            print_error(f"Django system checks found issues:")
            print_info(errors[:500])
            return False
    except Exception as e:
        print_error(f"Django checks failed: {e}")
        return False

def main():
    """Run all end-to-end tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  End-to-End Testing - Writing System")
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.END}\n")
    
    results = {
        'backend_health': test_backend_health(),
        'database': test_database(),
        'django_checks': test_django_checks(),
        'api_endpoints': test_api_endpoints(),
        'registration': None,
        'login': None,
        'protected_endpoint': None,
        'admin_panel': test_admin_panel(),
        'frontend': test_frontend(),
    }
    
    # Test registration and login flow if backend is up
    if results['backend_health']:
        credentials = test_registration()
        results['registration'] = credentials is not None
        
        if credentials:
            token = test_login(credentials)
            results['login'] = token is not None
            
            if token:
                results['protected_endpoint'] = test_protected_endpoint(token)
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  Test Summary")
    print(f"{'='*60}{Colors.END}\n")
    
    passed = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name.replace('_', ' ').title()}")
        elif result is False:
            print_error(f"{test_name.replace('_', ' ').title()}")
        else:
            print_info(f"{test_name.replace('_', ' ').title()}: Skipped")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print_success("All tests passed! System is ready for use.")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed. Please review the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

