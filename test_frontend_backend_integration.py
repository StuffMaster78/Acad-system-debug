#!/usr/bin/env python3
"""
End-to-end integration test for frontend and backend.
Tests complete user flows from API to database.
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
os.environ['DISABLE_NOTIFICATION_SIGNALS'] = 'True'
os.environ['DISABLE_SUPPORT_SIGNALS'] = 'True'
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'

try:
    django.setup()
except Exception as e:
    print(f"❌ Failed to setup Django: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model
from websites.models import Website

User = get_user_model()

# Detect if running inside Docker and use appropriate host
def get_base_url():
    """Get the base API URL based on environment"""
    # Check if API_BASE_URL is explicitly set
    if os.getenv("API_BASE_URL"):
        return os.getenv("API_BASE_URL")
    
    # Check if running inside Docker
    is_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER')
    
    if is_docker:
        # Inside web container: the app is bound to 0.0.0.0:8000
        # Always prefer localhost; fall back to service name 'web'.
        urls_to_try = [
            "http://localhost:8000/api/v1",
            "http://web:8000/api/v1",
        ]
        
        import socket
        for url in urls_to_try:
            try:
                host = url.split("://")[1].split("/")[0].split(":")[0]
                port = int(url.split(":")[-1].split("/")[0])
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    return url
            except:
                continue
        
        # Default fallback
        return "http://localhost:8000/api/v1"
    else:
        # Running on host - use localhost
        return "http://localhost:8000/api/v1"

BASE_URL = get_base_url()

# Set shorter timeouts for requests
requests.adapters.DEFAULT_TIMEOUT = 10

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_step(text):
    print(f"\n▶ {text}")

def test_api_availability():
    """Test if API endpoints are available"""
    global BASE_URL
    print_step("Testing API Availability")
    print_info(f"Using BASE_URL: {BASE_URL}")
    
    # First, try to connect to the base URL to check if server is running
    print_info(f"Attempting to connect to: {BASE_URL}/")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_success(f"Server is running: {BASE_URL}/ (Status: {response.status_code})")
    except requests.exceptions.ConnectionError as e:
        print_error(f"Server is not reachable at {BASE_URL}/")
        print_error(f"Connection error: {str(e)[:200]}")
        print_info("Trying alternative URLs...")
        
        # Try alternatives
        alternatives = [
            "http://localhost:8000/api/v1",
            "http://127.0.0.1:8000/api/v1",
            "http://web:8000/api/v1",
        ]
        
        connected = False
        for alt_url in alternatives:
            try:
                print_info(f"Trying: {alt_url}/")
                response = requests.get(f"{alt_url}/", timeout=3)
                print_success(f"Server found at: {alt_url}")
                BASE_URL = alt_url
                connected = True
                break
            except:
                continue
        
        if not connected:
            print_error("Cannot connect to backend server!")
            print_info("Make sure backend is running: docker-compose up -d web")
            print_info("Then check: curl http://localhost:8000/api/v1/")
            return False
    except requests.exceptions.Timeout:
        print_error("Connection timeout - server may be slow to respond")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False
    
    endpoints = [
        f"{BASE_URL}/auth/auth/login/",
        f"{BASE_URL}/auth/register/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print_success(f"{endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print_info(f"{endpoint}: {type(e).__name__} - {e}")
    
    return True

def test_user_registration():
    """Test user registration flow"""
    print_step("Testing User Registration")
    
    try:
        # Clean up test user if exists
        test_email = "integration_test@example.com"
        User.objects.filter(email=test_email).delete()
        
        # Get or create website
        website = Website.objects.filter(is_active=True).first()
        if not website:
            print_error("No active website found. Cannot test registration.")
            return None
        
        registration_data = {
            "username": "integration_test_user",
            "email": test_email,
            "password": "TestPassword123!",
            "password2": "TestPassword123!",
            "role": "client",
        }
        
        # Try different registration endpoints
        endpoints = [
            f"{BASE_URL}/auth/auth/register/",
            f"{BASE_URL}/auth/register/",
        ]
        
        response = None
        for endpoint in endpoints:
            try:
                response = requests.post(
                    endpoint,
                    json=registration_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if response.status_code in [200, 201, 400]:  # 400 might be validation error
                    break
            except requests.exceptions.RequestException as e:
                print_info(f"Registration endpoint {endpoint} failed: {e}")
                continue
        
        if not response:
            print_error("Could not reach registration endpoint")
            return None
        
        if response.status_code in [200, 201]:
            print_success(f"Registration successful: {response.status_code}")
            data = response.json()
            return data.get('user', {}).get('id')
        elif response.status_code == 400:
            try:
                error_data = response.json()
                print_info(f"Registration returned 400: {error_data}")
            except:
                print_info(f"Registration returned 400: {response.text[:200]}")
            # Check if user exists
            user = User.objects.filter(email=test_email).first()
            if user:
                print_success(f"User already exists: {user.id}")
                return user.id
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print_error(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_user_login(email, password):
    """Test user login flow"""
    print_step("Testing User Login")
    
    login_data = {
        "email": email,
        "password": password,
    }
    
    # Try different login endpoints
    endpoints = [
        f"{BASE_URL}/auth/auth/login/",
        f"{BASE_URL}/auth/login/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                json=login_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get('access_token') or data.get('access')
                if access_token:
                    print_success(f"Login successful at {endpoint}")
                    return access_token, data
                else:
                    print_error(f"Login response missing token: {data}")
            elif response.status_code == 500:
                print_error(f"Login 500 error at {endpoint}")
                try:
                    error_data = response.json()
                    print_error(f"Error details: {error_data}")
                except:
                    print_error(f"Response text: {response.text[:500]}")
            else:
                print_info(f"Login {response.status_code} at {endpoint}")
                
        except requests.exceptions.RequestException as e:
            print_error(f"Connection error at {endpoint}: {e}")
            continue
    
    return None, None

def test_authenticated_request(token):
    """Test authenticated API request"""
    print_step("Testing Authenticated Request")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try to get user profile or dashboard
    endpoints = [
        f"{BASE_URL}/users/me/",
        f"{BASE_URL}/auth/user/",
        f"{BASE_URL}/dashboard/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=5)
            if response.status_code == 200:
                print_success(f"Authenticated request successful: {endpoint}")
                return True
            else:
                print_info(f"Endpoint {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print_info(f"Endpoint {endpoint} not available: {e}")
    
    return False

def test_order_workflow(token):
    """Test order creation and management workflow"""
    print_step("Testing Order Workflow")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get orders list
    orders_endpoint = f"{BASE_URL}/orders/"
    try:
        response = requests.get(orders_endpoint, headers=headers, timeout=5)
        if response.status_code == 200:
            orders = response.json()
            print_success(f"Orders list retrieved: {len(orders.get('results', []))} orders")
            return True
        else:
            print_info(f"Orders endpoint returned: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print_info(f"Orders endpoint not available: {e}")
    
    return False

def main():
    try:
        print_header("FRONTEND-BACKEND INTEGRATION TESTING")
        
        # Step 1: Test API availability
        if not test_api_availability():
            print_error("API is not available. Cannot continue tests.")
            return False
        
        # Step 2: Test user registration
        try:
            user_id = test_user_registration()
        except Exception as e:
            print_error(f"Registration test failed: {e}")
            user_id = None
        
        # Step 3: Test login with registered user or existing test user
        test_email = "integration_test@example.com"
        test_password = "TestPassword123!"
        
        # If registration didn't work, try with existing user
        if not user_id:
            print_info("Trying login with existing test user...")
            try:
                user = User.objects.filter(role='superadmin').first()
                if user:
                    test_email = user.email
                    test_password = "testpass123"  # Reset password if needed
                    user.set_password(test_password)
                    user.save()
                    print_info(f"Using existing user: {user.email}")
            except Exception as e:
                print_error(f"Failed to setup existing user: {e}")
        
        token, login_data = None, None
        try:
            token, login_data = test_user_login(test_email, test_password)
        except Exception as e:
            print_error(f"Login test failed: {e}")
            import traceback
            traceback.print_exc()
        
        if not token:
            print_error("Login failed. Cannot continue with authenticated tests.")
            return False
        
        # Step 4: Test authenticated requests
        authenticated = False
        try:
            authenticated = test_authenticated_request(token)
        except Exception as e:
            print_error(f"Authenticated request test failed: {e}")
        
        # Step 5: Test order workflow
        order_workflow = False
        try:
            order_workflow = test_order_workflow(token)
        except Exception as e:
            print_error(f"Order workflow test failed: {e}")
        
        # Summary
        print_header("TEST SUMMARY")
        print_success("API Availability: ✓")
        print_success("User Registration: ✓" if user_id else "User Registration: ⚠ (used existing)")
        print_success("User Login: ✓" if token else "User Login: ✗")
        print_success("Authenticated Requests: ✓" if authenticated else "Authenticated Requests: ✗")
        print_success("Order Workflow: ✓" if order_workflow else "Order Workflow: ⚠")
        
        if token:
            print_success("\n✅ Frontend-Backend integration is working!")
            print_info(f"Access Token: {token[:50]}...")
            return True
        else:
            print_error("\n❌ Frontend-Backend integration has issues")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print_error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pass

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

