#!/usr/bin/env python3
"""
Test script for fixed endpoints.
Tests the endpoints that were fixed in this session.
"""
import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def print_test(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")
    return passed

def login(email, password):
    """Login and get access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [200, 201]:
            data = response.json()
            token = data.get('access') or data.get('access_token') or data.get('token')
            return token
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_financial_overview(token):
    """Test financial overview endpoint"""
    print("\n📊 Testing Financial Overview Endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            f"{BASE_URL}/admin-management/financial-overview/overview/",
            headers=headers
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            print_test(
                "Financial Overview",
                True,
                f"Status: {response.status_code}, Revenue: ${data.get('summary', {}).get('total_revenue', 0):,.2f}"
            )
            return True
        else:
            print_test(
                "Financial Overview",
                False,
                f"Status: {response.status_code}, Error: {response.text[:200]}"
            )
            return False
    except Exception as e:
        print_test("Financial Overview", False, f"Exception: {e}")
        return False

def test_websites_endpoint(token):
    """Test websites listing endpoint"""
    print("\n🌐 Testing Websites Endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            f"{BASE_URL}/websites/websites/",
            headers=headers
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            print_test(
                "Websites Listing",
                True,
                f"Status: {response.status_code}, Websites: {count}"
            )
            return True
        else:
            print_test(
                "Websites Listing",
                False,
                f"Status: {response.status_code}, Error: {response.text[:200]}"
            )
            return False
    except Exception as e:
        print_test("Websites Listing", False, f"Exception: {e}")
        return False

def test_payment_transactions(token):
    """Test payment transactions endpoint"""
    print("\n💳 Testing Payment Transactions Endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # Test with date range
        date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/order-payments/order-payments/all-transactions/",
            headers=headers,
            params={"date_from": date_from, "date_to": date_to, "page_size": 10}
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            count = data.get('count', 0) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0
            print_test(
                "Payment Transactions",
                True,
                f"Status: {response.status_code}, Transactions: {count}"
            )
            return True
        else:
            print_test(
                "Payment Transactions",
                False,
                f"Status: {response.status_code}, Error: {response.text[:200]}"
            )
            return False
    except Exception as e:
        print_test("Payment Transactions", False, f"Exception: {e}")
        return False

def test_writer_payments_grouped(token):
    """Test writer payments grouped endpoint"""
    print("\n💰 Testing Writer Payments Grouped Endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            f"{BASE_URL}/writer-wallet/writer-payments/grouped/",
            headers=headers
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            biweekly_count = len(data.get('biweekly', []))
            monthly_count = len(data.get('monthly', []))
            print_test(
                "Writer Payments Grouped",
                True,
                f"Status: {response.status_code}, Bi-weekly: {biweekly_count}, Monthly: {monthly_count}"
            )
            return True
        else:
            print_test(
                "Writer Payments Grouped",
                False,
                f"Status: {response.status_code}, Error: {response.text[:200]}"
            )
            return False
    except Exception as e:
        print_test("Writer Payments Grouped", False, f"Exception: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Testing Fixed Endpoints")
    print("=" * 60)
    
    # Get credentials from user or use defaults
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        print("\n⚠️  Usage: python test_fixed_endpoints.py <email> <password>")
        print("   Or set credentials in the script")
        print("\nTrying to find admin user...")
        
        # Try to get admin user from database
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "exec", "writing_project-web-1", "python", "manage.py", "shell", "-c",
                 "from django.contrib.auth import get_user_model; User = get_user_model(); admin = User.objects.filter(role__in=['admin', 'superadmin']).first(); print(admin.email if admin else 'None')"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip() != "None":
                email = result.stdout.strip()
                print(f"   Found admin user: {email}")
                print("   Please provide password as second argument")
                return
        except:
            pass
        
        print("   Could not find admin user automatically")
        return
    
    # Login
    print(f"\n🔐 Logging in as {email}...")
    token = login(email, password)
    if not token:
        print("❌ Login failed. Cannot proceed with tests.")
        return
    
    print("✅ Login successful")
    
    # Run tests
    results = []
    results.append(("Financial Overview", test_financial_overview(token)))
    results.append(("Websites Listing", test_websites_endpoint(token)))
    results.append(("Payment Transactions", test_payment_transactions(token)))
    results.append(("Writer Payments Grouped", test_writer_payments_grouped(token)))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

