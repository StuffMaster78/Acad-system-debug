"""
Django test script for fixed endpoints.
Run with: docker exec writing_project-web-1 python manage.py shell < test_endpoints_fixed.py
Or: docker exec -it writing_project-web-1 python manage.py test_endpoints_fixed
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json

User = get_user_model()

def test_endpoints():
    """Test the fixed endpoints"""
    print("=" * 60)
    print("Testing Fixed Endpoints")
    print("=" * 60)
    
    # Get admin user
    admin = User.objects.filter(role__in=['admin', 'superadmin']).first()
    if not admin:
        print("❌ No admin user found. Please create one first.")
        return
    
    print(f"\n🔐 Using admin user: {admin.email}")
    
    # Create API client
    client = APIClient()
    
    # Login (we'll use force_authenticate for testing)
    client.force_authenticate(user=admin)
    
    results = []
    
    # Test 1: Financial Overview
    print("\n📊 Testing Financial Overview Endpoint...")
    try:
        response = client.get('/api/v1/admin-management/financial-overview/overview/')
        passed = response.status_code == status.HTTP_200_OK
        if passed:
            data = response.json()
            revenue = data.get('summary', {}).get('total_revenue', 0)
            print(f"✅ PASS: Financial Overview - Status: {response.status_code}, Revenue: ${revenue:,.2f}")
        else:
            print(f"❌ FAIL: Financial Overview - Status: {response.status_code}")
            print(f"   Error: {response.data if hasattr(response, 'data') else response.content[:200]}")
        results.append(("Financial Overview", passed))
    except Exception as e:
        print(f"❌ FAIL: Financial Overview - Exception: {e}")
        results.append(("Financial Overview", False))
    
    # Test 2: Websites Listing
    print("\n🌐 Testing Websites Endpoint...")
    try:
        response = client.get('/api/v1/websites/websites/')
        passed = response.status_code == status.HTTP_200_OK
        if passed:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', len(data.get('results', [])))
            print(f"✅ PASS: Websites Listing - Status: {response.status_code}, Count: {count}")
        else:
            print(f"❌ FAIL: Websites Listing - Status: {response.status_code}")
            print(f"   Error: {response.data if hasattr(response, 'data') else response.content[:200]}")
        results.append(("Websites Listing", passed))
    except Exception as e:
        print(f"❌ FAIL: Websites Listing - Exception: {e}")
        results.append(("Websites Listing", False))
    
    # Test 3: Payment Transactions
    print("\n💳 Testing Payment Transactions Endpoint...")
    try:
        from datetime import datetime, timedelta
        date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        response = client.get(
            '/api/v1/order-payments/order-payments/all-transactions/',
            {'date_from': date_from, 'date_to': date_to, 'page_size': 10}
        )
        passed = response.status_code == status.HTTP_200_OK
        if passed:
            data = response.json()
            count = data.get('count', 0) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0
            print(f"✅ PASS: Payment Transactions - Status: {response.status_code}, Count: {count}")
        else:
            print(f"❌ FAIL: Payment Transactions - Status: {response.status_code}")
            print(f"   Error: {response.data if hasattr(response, 'data') else response.content[:200]}")
        results.append(("Payment Transactions", passed))
    except Exception as e:
        print(f"❌ FAIL: Payment Transactions - Exception: {e}")
        results.append(("Payment Transactions", False))
    
    # Test 4: Writer Payments Grouped
    print("\n💰 Testing Writer Payments Grouped Endpoint...")
    try:
        response = client.get('/api/v1/writer-wallet/writer-payments/grouped/')
        passed = response.status_code == status.HTTP_200_OK
        if passed:
            data = response.json()
            biweekly = len(data.get('biweekly', []))
            monthly = len(data.get('monthly', []))
            print(f"✅ PASS: Writer Payments Grouped - Status: {response.status_code}, Bi-weekly: {biweekly}, Monthly: {monthly}")
        else:
            print(f"❌ FAIL: Writer Payments Grouped - Status: {response.status_code}")
            print(f"   Error: {response.data if hasattr(response, 'data') else response.content[:200]}")
        results.append(("Writer Payments Grouped", passed))
    except Exception as e:
        print(f"❌ FAIL: Writer Payments Grouped - Exception: {e}")
        results.append(("Writer Payments Grouped", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed_count = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status_icon = "✅ PASS" if result else "❌ FAIL"
        print(f"{status_icon}: {name}")
    
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")
    
    return passed_count == total

if __name__ == "__main__":
    test_endpoints()

