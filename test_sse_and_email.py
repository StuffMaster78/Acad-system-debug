#!/usr/bin/env python
"""
Test script for SSE and Gmail email configuration.

Usage:
    python test_sse_and_email.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model
from notifications_system.delivery.sse import SSEDeliveryBackend
from notifications_system.models.notifications import Notification
from notifications_system.services.core import NotificationService

User = get_user_model()


def test_email_configuration():
    """Test Gmail SMTP configuration."""
    print("\n" + "="*60)
    print("📧 Testing Email Configuration")
    print("="*60)
    
    # Check configuration
    print(f"\n✅ Email Backend: {settings.EMAIL_BACKEND}")
    print(f"✅ Email Host: {settings.EMAIL_HOST}")
    print(f"✅ Email Port: {settings.EMAIL_PORT}")
    print(f"✅ Email Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"✅ Email User: {settings.EMAIL_HOST_USER}")
    print(f"✅ From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # Check if credentials are set
    if not settings.EMAIL_HOST_USER:
        print("\n❌ ERROR: EMAIL_HOST_USER not set!")
        print("   Set it in .env file: EMAIL_HOST_USER=your-email@gmail.com")
        return False
    
    if not settings.EMAIL_HOST_PASSWORD:
        print("\n❌ ERROR: EMAIL_HOST_PASSWORD not set!")
        print("   Set it in .env file: EMAIL_HOST_PASSWORD=your-app-password")
        return False
    
    # Test email send
    print("\n📤 Sending test email...")
    try:
        test_email = input("\nEnter test email address (or press Enter to skip): ").strip()
        
        if not test_email:
            print("⏭️  Skipping email send test")
            return True
        
        send_mail(
            subject='✅ Writing System - Email Test',
            message='''
This is a test email from the Writing System Backend.

If you received this email, your Gmail SMTP configuration is working correctly!

Configuration:
- Backend: {backend}
- Host: {host}
- Port: {port}
- TLS: {tls}
            '''.format(
                backend=settings.EMAIL_BACKEND,
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                tls=settings.EMAIL_USE_TLS
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        print(f"✅ Test email sent successfully to {test_email}!")
        print("   Check your inbox (and spam folder) for the test email.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR sending email: {e}")
        print("\nTroubleshooting:")
        print("1. Check that 2-Step Verification is enabled on Gmail")
        print("2. Verify App Password is correct (no spaces)")
        print("3. Ensure EMAIL_HOST_USER matches your Gmail address")
        print("4. Check firewall/proxy settings")
        return False


def test_sse_configuration():
    """Test SSE configuration."""
    print("\n" + "="*60)
    print("🔔 Testing SSE Configuration")
    print("="*60)
    
    # Check if SSE backend exists
    try:
        sse_backend = SSEDeliveryBackend()
        print("\n✅ SSE Backend initialized successfully")
        print(f"✅ Connection timeout: {sse_backend.connection_timeout}s")
        print(f"✅ Heartbeat interval: {sse_backend.heartbeat_interval}s")
        print(f"✅ Max connections per user: {sse_backend.max_connections_per_user}")
        
        # Check Redis (required for SSE)
        from django.core.cache import cache
        try:
            cache.set('sse_test', 'test', 10)
            cache.get('sse_test')
            print("✅ Redis cache is working (required for SSE)")
        except Exception as e:
            print(f"❌ Redis cache error: {e}")
            print("   SSE requires Redis to be running!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_notification_creation():
    """Test creating a notification."""
    print("\n" + "="*60)
    print("📬 Testing Notification Creation")
    print("="*60)
    
    try:
        # Get or create a test user
        test_email = input("\nEnter test user email (or press Enter to skip): ").strip()
        
        if not test_email:
            print("⏭️  Skipping notification creation test")
            return True
        
        try:
            user = User.objects.get(email=test_email)
        except User.DoesNotExist:
            print(f"❌ User with email {test_email} not found")
            print("   Create a user first or use an existing email")
            return False
        
        # Create a test notification
        print(f"\n📝 Creating test notification for user: {user.email}")
        
        notification = NotificationService.create_notification(
            user=user,
            event="test.notification",
            title="Test Notification",
            message="This is a test notification to verify the system is working.",
            priority="normal",
            channels=["in_app", "email", "sse"],
        )
        
        print(f"✅ Notification created: ID {notification.id}")
        print(f"✅ Channels: {notification.channels}")
        print(f"✅ Priority: {notification.priority}")
        
        # Check if notification was delivered
        print("\n📊 Checking notification delivery...")
        from notifications_system.models.delivery import Delivery
        
        deliveries = Delivery.objects.filter(notification=notification)
        print(f"✅ Delivery records created: {deliveries.count()}")
        
        for delivery in deliveries:
            print(f"   - Channel: {delivery.channel}, Status: {delivery.status}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 SSE & Email Configuration Test Suite")
    print("="*60)
    
    results = {
        'email': False,
        'sse': False,
        'notifications': False,
    }
    
    # Test email
    results['email'] = test_email_configuration()
    
    # Test SSE
    results['sse'] = test_sse_configuration()
    
    # Test notifications
    results['notifications'] = test_notification_creation()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    print(f"\n{'✅' if results['email'] else '❌'} Email Configuration: {'PASS' if results['email'] else 'FAIL'}")
    print(f"{'✅' if results['sse'] else '❌'} SSE Configuration: {'PASS' if results['sse'] else 'FAIL'}")
    print(f"{'✅' if results['notifications'] else '❌'} Notification Creation: {'PASS' if results['notifications'] else 'FAIL'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Your system is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        print("\nNext steps:")
        if not results['email']:
            print("1. Configure Gmail SMTP (see SSE_AND_GMAIL_SETUP.md)")
        if not results['sse']:
            print("2. Ensure Redis is running")
        if not results['notifications']:
            print("3. Create a test user in the system")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

