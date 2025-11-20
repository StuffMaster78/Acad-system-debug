#!/usr/bin/env python
"""
Test script to verify Gmail SMTP configuration.
Run this after setting up Gmail SMTP to verify everything works.
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
from django.core.exceptions import ImproperlyConfigured


def test_email_configuration():
    """Test email configuration and send a test email."""
    print("=" * 60)
    print("Gmail SMTP Configuration Test")
    print("=" * 60)
    
    # Check configuration
    print("\n📋 Checking Configuration...")
    
    required_settings = [
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'DEFAULT_FROM_EMAIL',
    ]
    
    missing_settings = []
    for setting in required_settings:
        value = getattr(settings, setting, None)
        if not value:
            missing_settings.append(setting)
            print(f"  ❌ {setting}: Not set")
        else:
            # Mask password
            if 'PASSWORD' in setting:
                masked = '*' * len(str(value))
                print(f"  ✅ {setting}: {masked}")
            else:
                print(f"  ✅ {setting}: {value}")
    
    if missing_settings:
        print(f"\n❌ Missing required settings: {', '.join(missing_settings)}")
        print("\nPlease set these in your .env file or environment variables:")
        for setting in missing_settings:
            print(f"  - {setting}")
        return False
    
    # Check email backend
    print(f"\n📧 Email Backend: {settings.EMAIL_BACKEND}")
    print(f"🔐 Using TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
    print(f"🔐 Using SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    
    # Get test recipient
    print("\n" + "=" * 60)
    recipient = input("Enter test email address (or press Enter to skip sending): ").strip()
    
    if not recipient:
        print("\n⚠️  Skipping email send test. Configuration looks good!")
        return True
    
    # Send test email
    print(f"\n📤 Sending test email to {recipient}...")
    
    try:
        send_mail(
            subject='✅ Writing System - Email Configuration Test',
            message=f"""
Hello!

This is a test email from your Writing System backend.

If you received this email, your Gmail SMTP configuration is working correctly! 🎉

Configuration Details:
- Email Host: {settings.EMAIL_HOST}
- Email Port: {settings.EMAIL_PORT}
- From Email: {settings.DEFAULT_FROM_EMAIL}
- Backend: {settings.EMAIL_BACKEND}

You can now use email notifications in your system.

Best regards,
Writing System Backend
            """.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        
        print("\n✅ Test email sent successfully!")
        print(f"   Please check {recipient} inbox (and spam folder)")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to send email: {e}")
        print("\nCommon issues:")
        print("  1. Check that 2-Step Verification is enabled on Gmail")
        print("  2. Verify you're using an App Password (not regular password)")
        print("  3. Check that EMAIL_HOST_PASSWORD is set correctly")
        print("  4. Verify network/firewall allows SMTP connections")
        return False


def test_html_email():
    """Test sending HTML email."""
    print("\n" + "=" * 60)
    send_html = input("Send HTML test email? (y/n): ").strip().lower()
    
    if send_html != 'y':
        return
    
    recipient = input("Enter test email address: ").strip()
    if not recipient:
        return
    
    print(f"\n📤 Sending HTML test email to {recipient}...")
    
    try:
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">✅ Email Test Successful!</h1>
            </div>
            <div style="padding: 20px; background: #f9f9f9;">
                <p>This is a test HTML email from your Writing System backend.</p>
                <p>If you can see this styled content, HTML emails are working correctly!</p>
                <div style="margin-top: 20px; padding: 15px; background: white; border-left: 4px solid #667eea;">
                    <strong>Configuration:</strong><br>
                    Email Host: {EMAIL_HOST}<br>
                    Email Port: {EMAIL_PORT}<br>
                    From: {DEFAULT_FROM_EMAIL}
                </div>
            </div>
            <div style="padding: 20px; text-align: center; color: #666;">
                <p>Writing System Backend</p>
            </div>
        </body>
        </html>
        """.format(
            EMAIL_HOST=settings.EMAIL_HOST,
            EMAIL_PORT=settings.EMAIL_PORT,
            DEFAULT_FROM_EMAIL=settings.DEFAULT_FROM_EMAIL
        )
        
        email = EmailMessage(
            subject='✅ Writing System - HTML Email Test',
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.content_subtype = 'html'
        email.send()
        
        print("✅ HTML email sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send HTML email: {e}")


if __name__ == '__main__':
    print("\n")
    success = test_email_configuration()
    
    if success:
        test_html_email()
        print("\n" + "=" * 60)
        print("✅ Email configuration test complete!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Please fix configuration issues and try again")
        print("=" * 60)
        sys.exit(1)

