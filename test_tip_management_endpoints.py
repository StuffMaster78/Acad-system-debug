#!/usr/bin/env python
"""
Test script for Tip Management endpoints
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework.request import Request
from admin_management.views import AdminTipManagementViewSet
from writer_management.models.tipping import Tip
from websites.models import Website

User = get_user_model()

def test_tip_management_endpoints():
    """Test all Tip Management endpoints"""
    print("=" * 60)
    print("Testing Tip Management Endpoints")
    print("=" * 60)
    
    # Get admin user
    admin = User.objects.filter(role__in=['admin', 'superadmin']).first()
    if not admin:
        print("❌ No admin user found. Please create an admin user first.")
        return False
    
    print(f"\n✓ Using admin user: {admin.username} (role: {admin.role})")
    
    # Setup request factory
    factory = APIRequestFactory()
    viewset = AdminTipManagementViewSet()
    
    def make_request(method, path, data=None):
        """Helper to create DRF Request object"""
        if method == 'get':
            request = factory.get(path, data or {})
        else:
            request = factory.post(path, data or {})
        force_authenticate(request, user=admin)
        request.user = admin
        return Request(request)
    
    # Test 1: Dashboard endpoint
    print("\n" + "-" * 60)
    print("Test 1: Dashboard Endpoint")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/admin-management/tips/dashboard/')
        response = viewset.dashboard(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ Dashboard endpoint works!")
            print(f"  - Total Tips: {data.get('total_tips', 0)}")
            print(f"  - Total Tip Amount: ${data.get('total_tip_amount', 0):.2f}")
            print(f"  - Total Writer Earnings: ${data.get('total_writer_earnings', 0):.2f}")
            print(f"  - Total Platform Profit: ${data.get('total_platform_profit', 0):.2f}")
        else:
            print(f"❌ Error: {response.data}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Dashboard with days filter
    print("\n" + "-" * 60)
    print("Test 2: Dashboard with days filter (7 days)")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/admin-management/tips/dashboard/', {'days': '7'})
        response = viewset.dashboard(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ Dashboard with days filter works!")
            print(f"  - Recent Tips (7 days): {data.get('recent_total_tips', 0)}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: List Tips endpoint
    print("\n" + "-" * 60)
    print("Test 3: List Tips Endpoint")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/admin-management/tips/list_tips/')
        response = viewset.list_tips(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ List tips endpoint works!")
            print(f"  - Total Count: {data.get('count', 0)}")
            print(f"  - Results: {len(data.get('results', []))}")
            print(f"  - Summary Total: ${data.get('summary', {}).get('total_tip_amount', 0):.2f}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: List Tips with filters
    print("\n" + "-" * 60)
    print("Test 4: List Tips with filters (tip_type=direct)")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/admin-management/tips/list_tips/', {'tip_type': 'direct', 'limit': '10'})
        response = viewset.list_tips(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ List tips with filters works!")
            print(f"  - Filtered Count: {data.get('count', 0)}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Analytics endpoint
    print("\n" + "-" * 60)
    print("Test 5: Analytics Endpoint")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/admin-management/tips/analytics/')
        response = viewset.analytics(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ Analytics endpoint works!")
            print(f"  - Top Writers: {len(data.get('top_writers', []))}")
            print(f"  - Top Clients: {len(data.get('top_clients', []))}")
            print(f"  - Type Breakdown: {len(data.get('type_breakdown', []))}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Earnings endpoint
    print("\n" + "-" * 60)
    print("Test 6: Earnings Endpoint")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/admin-management/tips/earnings/')
        response = viewset.earnings(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ Earnings endpoint works!")
            print(f"  - Overall Earnings: ${data.get('overall_earnings', {}).get('total_platform_profit', 0):.2f}")
            print(f"  - Level Breakdown: {len(data.get('level_breakdown', []))}")
            print(f"  - Type Breakdown: {len(data.get('type_breakdown', []))}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 7: Check if there are any tips in the database
    print("\n" + "-" * 60)
    print("Test 7: Database Check")
    print("-" * 60)
    tip_count = Tip.objects.count()
    print(f"Total Tips in Database: {tip_count}")
    if tip_count == 0:
        print("⚠️  No tips in database. Endpoints will return empty results.")
        print("   This is expected if no tips have been created yet.")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_tip_management_endpoints()
    sys.exit(0 if success else 1)

