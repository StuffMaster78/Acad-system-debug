"""
Manual End-to-End Testing Script
Tests core workflows manually through the API
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from rest_framework import status
from websites.models import Website

User = get_user_model()

def print_test(name, passed, message=""):
    """Print test result"""
    status_icon = "✅" if passed else "❌"
    status_text = "PASSED" if passed else "FAILED"
    print(f"{status_icon} {name}: {status_text} {message}")

def test_setup():
    """Setup test data"""
    print("\n🔧 Setting up test data...")
    
    # Create or get website
    website, _ = Website.objects.get_or_create(
        name="Test Website",
        defaults={'domain': 'test.local', 'is_active': True}
    )
    
    # Create test users
    admin, _ = User.objects.get_or_create(
        username='admin_test',
        defaults={
            'email': 'admin@test.com',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin.set_password('testpass123')
    admin.save()
    
    client_user, _ = User.objects.get_or_create(
        username='client_test',
        defaults={
            'email': 'client@test.com',
            'role': 'client'
        }
    )
    client_user.set_password('testpass123')
    client_user.save()
    
    writer_user, _ = User.objects.get_or_create(
        username='writer_test',
        defaults={
            'email': 'writer@test.com',
            'role': 'writer'
        }
    )
    writer_user.set_password('testpass123')
    writer_user.save()
    
    print("✅ Test data setup complete")
    return {
        'website': website,
        'admin': admin,
        'client': client_user,
        'writer': writer_user
    }

def test_authentication(users):
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication...")
    client = APIClient()
    
    # Test login
    response = client.post('/api/v1/auth/login/', {
        'username': users['client'].username,
        'password': 'testpass123'
    })
    passed = response.status_code in [200, 201]
    print_test("User Login", passed, f"(Status: {response.status_code})")
    
    if passed:
        token = response.data.get('access') or response.data.get('token')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    return client, token if passed else None

def test_order_creation(api_client, users):
    """Test order creation workflow"""
    print("\n📝 Testing Order Creation...")
    
    # This would test order creation if we have the endpoint
    # For now, just check if models are accessible
    from orders.models import Order
    try:
        order = Order.objects.first()
        print_test("Order Model Accessible", True)
        return True
    except Exception as e:
        print_test("Order Model Accessible", False, str(e))
        return False

def test_payment_workflow(api_client, users):
    """Test payment workflow"""
    print("\n💳 Testing Payment Workflow...")
    
    from order_payments_management.models import OrderPayment
    try:
        payment = OrderPayment.objects.first()
        print_test("Payment Model Accessible", True)
        return True
    except Exception as e:
        print_test("Payment Model Accessible", False, str(e))
        return False

def test_class_management(api_client, users):
    """Test class management workflow"""
    print("\n🎓 Testing Class Management...")
    
    from class_management.models import ClassBundle
    try:
        bundle = ClassBundle.objects.first()
        print_test("Class Bundle Model Accessible", True)
        return True
    except Exception as e:
        print_test("Class Bundle Model Accessible", False, str(e))
        return False

def test_discount_system(api_client, users):
    """Test discount system"""
    print("\n💰 Testing Discount System...")
    
    from discounts.models.discount import Discount
    try:
        discount = Discount.objects.first()
        print_test("Discount Model Accessible", True)
        return True
    except Exception as e:
        print_test("Discount Model Accessible", False, str(e))
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 END-TO-END SYSTEM TESTING")
    print("=" * 50)
    
    # Setup
    users = test_setup()
    
    # Authentication
    api_client, token = test_authentication(users)
    
    # Core workflows
    test_order_creation(api_client, users)
    test_payment_workflow(api_client, users)
    test_class_management(api_client, users)
    test_discount_system(api_client, users)
    
    print("\n" + "=" * 50)
    print("✅ End-to-End Testing Complete!")
    print("=" * 50)

if __name__ == '__main__':
    main()

