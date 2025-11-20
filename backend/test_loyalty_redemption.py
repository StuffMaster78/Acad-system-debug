#!/usr/bin/env python
"""
Test script for Loyalty Redemption system
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
from loyalty_management.views import (
    RedemptionCategoryViewSet,
    RedemptionItemViewSet,
    RedemptionRequestViewSet,
    LoyaltyAnalyticsViewSet
)
from loyalty_management.models import (
    RedemptionCategory,
    RedemptionItem,
    RedemptionRequest
)
from websites.models import Website
from client_management.models import ClientProfile

User = get_user_model()

def test_loyalty_redemption_system():
    """Test Loyalty Redemption system endpoints"""
    print("=" * 60)
    print("Testing Loyalty Redemption System")
    print("=" * 60)
    
    # Get admin and client users
    admin = User.objects.filter(role__in=['admin', 'superadmin']).first()
    client_user = User.objects.filter(role='client').first()
    
    if not admin:
        print("❌ No admin user found.")
        return False
    
    if not client_user:
        print("⚠️  No client user found. Some tests will be skipped.")
        client_user = None
    
    print(f"\n✓ Using admin user: {admin.username} (role: {admin.role})")
    if client_user:
        print(f"✓ Using client user: {client_user.username} (role: {client_user.role})")
    
    # Get a website
    website = Website.objects.first()
    if not website:
        print("❌ No website found.")
        return False
    print(f"✓ Using website: {website.name} (id: {website.id})")
    
    # Setup request factory
    factory = APIRequestFactory()
    
    def make_request(method, path, data=None, user=None):
        """Helper to create DRF Request object"""
        if method == 'get':
            request = factory.get(path, data or {})
        elif method == 'post':
            # For POST, use json format and set content type
            request = factory.post(path, data or {}, content_type='application/json')
        else:
            request = factory.put(path, data or {}, content_type='application/json')
        
        if user:
            force_authenticate(request, user=user)
            request.user = user
        return Request(request)
    
    def call_viewset_action(viewset_class, action, request, pk=None, **kwargs):
        """Helper to call viewset action with proper request setup"""
        viewset = viewset_class()
        viewset.request = request
        viewset.format_kwarg = None
        viewset.action = action
        viewset.kwargs = {'pk': pk} if pk else {}
        
        if action == 'list':
            return viewset.list(request)
        elif action == 'create':
            return viewset.create(request)
        elif action == 'retrieve':
            return viewset.retrieve(request, pk=pk)
        elif action == 'update':
            return viewset.update(request, pk=pk)
        elif action == 'approve':
            return viewset.approve(request, pk=pk)
        elif action == 'reject':
            return viewset.reject(request, pk=pk)
        return None
    
    # Test 1: List Redemption Categories (Admin)
    print("\n" + "-" * 60)
    print("Test 1: List Redemption Categories (Admin)")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/loyalty/redemption-categories/', user=admin)
        response = call_viewset_action(RedemptionCategoryViewSet, 'list', request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ List categories endpoint works!")
            print(f"  - Categories Count: {len(data.get('results', [])) if isinstance(data, dict) else len(data)}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: List Redemption Items (Admin)
    print("\n" + "-" * 60)
    print("Test 2: List Redemption Items (Admin)")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/loyalty/redemption-items/', user=admin)
        response = call_viewset_action(RedemptionItemViewSet, 'list', request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ List items endpoint works!")
            print(f"  - Items Count: {len(data.get('results', [])) if isinstance(data, dict) else len(data)}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Create Redemption Category (Direct Model Test)
    print("\n" + "-" * 60)
    print("Test 3: Create Redemption Category (Direct Model Test)")
    print("-" * 60)
    try:
        category, created = RedemptionCategory.objects.get_or_create(
            website=website,
            name='Test Discounts',
            defaults={
                'description': 'Test category for discounts',
                'is_active': True,
                'sort_order': 0
            }
        )
        if created:
            print("✓ Category created successfully!")
            category_id = category.id
            print(f"  - Created Category ID: {category_id}")
        else:
            print("✓ Category already exists!")
            category_id = category.id
            print(f"  - Existing Category ID: {category_id}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        category_id = None
    
    # Test 4: Create Redemption Item (Direct Model Test)
    print("\n" + "-" * 60)
    print("Test 4: Create Redemption Item (Direct Model Test)")
    print("-" * 60)
    try:
        # Get or create category first
        category = RedemptionCategory.objects.filter(website=website).first()
        if not category and category_id:
            category = RedemptionCategory.objects.filter(id=category_id).first()
        if not category:
            category = RedemptionCategory.objects.create(
                website=website,
                name='Test Category',
                is_active=True
            )
        
        item, created = RedemptionItem.objects.get_or_create(
            website=website,
            category=category,
            name='Test $10 Discount',
            defaults={
                'description': 'Test discount item',
                'points_required': 100,
                'redemption_type': 'discount',
                'discount_amount': 10.00,
                'is_active': True
            }
        )
        if created:
            print("✓ Item created successfully!")
            item_id = item.id
            print(f"  - Created Item ID: {item_id}")
        else:
            print("✓ Item already exists!")
            item_id = item.id
            print(f"  - Existing Item ID: {item_id}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        item_id = None
    
    # Test 4b: Test Redemption Service (Create Request)
    print("\n" + "-" * 60)
    print("Test 4b: Test Redemption Service - Create Request")
    print("-" * 60)
    if client_user and item_id:
        try:
            from loyalty_management.services.redemption_service import RedemptionService
            client_profile = ClientProfile.objects.filter(user=client_user).first()
            if client_profile:
                # Add some loyalty points first
                from loyalty_management.models import LoyaltyTransaction
                LoyaltyTransaction.objects.create(
                    client=client_profile,
                    website=website,
                    points=200,  # Enough for the 100 point item
                    transaction_type='add',
                    reason='Test points for redemption'
                )
                
                # Try to create redemption request
                redemption = RedemptionService.create_redemption_request(
                    client_profile=client_profile,
                    item_id=item_id,
                    fulfillment_details={}
                )
                print("✓ Redemption request created successfully!")
                print(f"  - Request ID: {redemption.id}")
                print(f"  - Status: {redemption.status}")
                print(f"  - Points Used: {redemption.points_used}")
                
                # Test approve
                print("\n" + "-" * 60)
                print("Test 4c: Test Redemption Service - Approve Request")
                print("-" * 60)
                RedemptionService.approve_redemption(redemption, admin)
                redemption.refresh_from_db()
                print("✓ Redemption approved successfully!")
                print(f"  - Status: {redemption.status}")
                print(f"  - Fulfillment Code: {redemption.fulfillment_code}")
            else:
                print("⚠️  No client profile found for client user")
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  Skipping - need client user and item")
    
    # Test 5: List Redemption Requests (Admin)
    print("\n" + "-" * 60)
    print("Test 5: List Redemption Requests (Admin)")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/loyalty/redemption-requests/', user=admin)
        response = call_viewset_action(RedemptionRequestViewSet, 'list', request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ List requests endpoint works!")
            print(f"  - Requests Count: {len(data.get('results', [])) if isinstance(data, dict) else len(data)}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Analytics Endpoint (Admin)
    print("\n" + "-" * 60)
    print("Test 6: Loyalty Analytics Endpoint (Admin)")
    print("-" * 60)
    try:
        request = make_request('get', '/api/v1/loyalty/analytics/', user=admin)
        response = call_viewset_action(LoyaltyAnalyticsViewSet, 'list', request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print("✓ Analytics endpoint works!")
            print(f"  - Analytics Records: {len(data.get('results', [])) if isinstance(data, dict) else len(data)}")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 7: Database Check
    print("\n" + "-" * 60)
    print("Test 7: Database Check")
    print("-" * 60)
    category_count = RedemptionCategory.objects.count()
    item_count = RedemptionItem.objects.count()
    request_count = RedemptionRequest.objects.count()
    print(f"Redemption Categories: {category_count}")
    print(f"Redemption Items: {item_count}")
    print(f"Redemption Requests: {request_count}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_loyalty_redemption_system()
    sys.exit(0 if success else 1)

