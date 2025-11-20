"""
Test script for Invoice Payment System
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from order_payments_management.models import Invoice
from order_payments_management.services.invoice_service import InvoiceService
from websites.models import Website
from users.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

def test_invoice_creation():
    """Test invoice creation"""
    print("=" * 60)
    print("Testing Invoice System")
    print("=" * 60)
    
    # Get a website
    website = Website.objects.filter(is_active=True).first()
    if not website:
        print("❌ No active website found. Please create a website first.")
        return False
    
    print(f"✓ Using website: {website.name}")
    
    # Get an admin user
    admin = User.objects.filter(role__in=['admin', 'superadmin']).first()
    if not admin:
        print("❌ No admin user found. Please create an admin user first.")
        return False
    
    print(f"✓ Using admin: {admin.email}")
    
    # Test 1: Create invoice
    print("\n1. Testing Invoice Creation...")
    try:
        invoice = InvoiceService.create_invoice(
            recipient_email="test@example.com",
            website=website,
            amount=Decimal("150.00"),
            title="Test Invoice",
            due_date=(timezone.now() + timedelta(days=30)).date(),
            issued_by=admin,
            recipient_name="Test User",
            purpose="Order Payment",
            description="This is a test invoice for order #12345",
            order_number="ORD-12345",
            send_email=False,  # Don't send email in test
        )
        print(f"✓ Invoice created successfully!")
        print(f"  - Reference ID: {invoice.reference_id}")
        print(f"  - Amount: ${invoice.amount}")
        print(f"  - Recipient: {invoice.recipient_email}")
        print(f"  - Payment Token: {invoice.payment_token[:20]}...")
        print(f"  - Token Expires: {invoice.token_expires_at}")
    except Exception as e:
        print(f"❌ Failed to create invoice: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Get payment link
    print("\n2. Testing Payment Link Generation...")
    try:
        payment_link = InvoiceService.get_payment_link(invoice)
        print(f"✓ Payment link generated: {payment_link}")
    except Exception as e:
        print(f"❌ Failed to generate payment link: {e}")
        return False
    
    # Test 3: Get invoice by token
    print("\n3. Testing Invoice Retrieval by Token...")
    try:
        retrieved_invoice = InvoiceService.get_invoice_by_token(invoice.payment_token)
        if retrieved_invoice and retrieved_invoice.id == invoice.id:
            print(f"✓ Invoice retrieved successfully by token")
        else:
            print(f"❌ Failed to retrieve invoice by token")
            return False
    except Exception as e:
        print(f"❌ Failed to retrieve invoice: {e}")
        return False
    
    # Test 4: Check invoice methods
    print("\n4. Testing Invoice Model Methods...")
    try:
        recipient_email = invoice.get_recipient_email()
        recipient_name = invoice.get_recipient_name()
        is_overdue = invoice.is_overdue()
        is_token_valid = invoice.is_token_valid()
        
        print(f"✓ get_recipient_email(): {recipient_email}")
        print(f"✓ get_recipient_name(): {recipient_name}")
        print(f"✓ is_overdue(): {is_overdue}")
        print(f"✓ is_token_valid(): {is_token_valid}")
    except Exception as e:
        print(f"❌ Failed to test invoice methods: {e}")
        return False
    
    # Test 5: List invoices
    print("\n5. Testing Invoice Query...")
    try:
        invoices = Invoice.objects.filter(website=website)
        print(f"✓ Found {invoices.count()} invoice(s) for website")
    except Exception as e:
        print(f"❌ Failed to query invoices: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All Invoice System Tests Passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_invoice_creation()
    sys.exit(0 if success else 1)

