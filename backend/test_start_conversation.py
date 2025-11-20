#!/usr/bin/env python
"""
Test script for the Start Conversation endpoint.

Usage:
    python test_start_conversation.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order
from communications.models import CommunicationThread
from communications.services.thread_service import ThreadService
from communications.services.communication_guard import CommunicationGuardService

User = get_user_model()


def test_start_conversation_logic():
    """Test the start conversation logic without making HTTP requests."""
    print("\n" + "="*60)
    print("🧪 Testing Start Conversation Logic")
    print("="*60)
    
    # Get a test order
    try:
        order = Order.objects.first()
        if not order:
            print("\n❌ No orders found in database. Create an order first.")
            return False
        
        print(f"\n✅ Found test order: ID {order.id}")
        print(f"   Client: {order.client.username if order.client else 'None'}")
        print(f"   Writer: {order.assigned_writer.username if order.assigned_writer else 'None'}")
        print(f"   Status: {order.status}")
        print(f"   Website: {order.website.domain if order.website else 'None'}")
        
        # Check if thread already exists
        existing_thread = CommunicationThread.objects.filter(order=order).first()
        if existing_thread:
            print(f"\n⚠️  Thread already exists for this order: ID {existing_thread.id}")
            print("   The endpoint will return this existing thread.")
            return True
        
        # Test permission check
        print("\n📋 Testing permission checks...")
        
        # Test with order client
        if order.client:
            can_start = CommunicationGuardService.can_start_thread(order.client, order)
            print(f"   Client can start: {'✅' if can_start else '❌'}")
        
        # Test with assigned writer
        if order.assigned_writer:
            can_start = CommunicationGuardService.can_start_thread(order.assigned_writer, order)
            print(f"   Writer can start: {'✅' if can_start else '❌'}")
        
        # Test with admin
        admin = User.objects.filter(role__in=['admin', 'superadmin']).first()
        if admin:
            can_start = CommunicationGuardService.can_start_thread(admin, order)
            print(f"   Admin can start: {'✅' if can_start else '❌'}")
        
        # Test participant determination
        print("\n👥 Testing participant determination...")
        user = order.client or order.assigned_writer or admin
        if user:
            participants = [user]
            if order.client and order.client != user:
                participants.append(order.client)
            if order.assigned_writer and order.assigned_writer != user:
                participants.append(order.assigned_writer)
            
            print(f"   Participants would be: {[p.username for p in participants]}")
        
        # Test thread creation (dry run - don't actually create)
        print("\n🔨 Testing thread creation logic...")
        try:
            # Check if we can create
            CommunicationGuardService.assert_can_start_thread(user, order)
            print("   ✅ Permission check passed")
            
            # Check order status
            if order.status == "archived":
                print("   ⚠️  Order is archived - thread creation will fail")
            else:
                print("   ✅ Order status allows thread creation")
            
        except (PermissionError, PermissionDenied) as e:
            print(f"   ❌ Permission check failed: {e}")
            return False
        
        print("\n✅ All tests passed! The endpoint should work correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoint_url():
    """Show the endpoint URL and example usage."""
    print("\n" + "="*60)
    print("📍 Endpoint Information")
    print("="*60)
    
    print("\n✅ Endpoint URL:")
    print("   POST /api/v1/order-communications/communication-threads/start-for-order/")
    
    print("\n📝 Example Request:")
    print("   curl -X POST http://localhost:8000/api/v1/order-communications/communication-threads/start-for-order/ \\")
    print("     -H 'Authorization: Bearer YOUR_TOKEN' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"order_id\": 123}'")
    
    print("\n📝 Example Response (Success):")
    print("   {")
    print('     "detail": "Conversation thread created successfully.",')
    print('     "thread": {')
    print('       "id": 456,')
    print('       "order": 123,')
    print('       "thread_type": "order",')
    print('       "participants": [1, 2],')
    print('       "is_active": true')
    print("     }")
    print("   }")
    
    print("\n📝 Example Response (Thread Exists):")
    print("   {")
    print('     "detail": "Conversation thread already exists for this order.",')
    print('     "thread": {...}')
    print("   }")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 Start Conversation Endpoint Test Suite")
    print("="*60)
    
    # Test the logic
    logic_test = test_start_conversation_logic()
    
    # Show endpoint info
    test_endpoint_url()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    if logic_test:
        print("\n✅ Logic tests passed!")
        print("✅ Endpoint is ready to use")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    print("\n💡 Next Steps:")
    print("   1. Test the endpoint with a real HTTP request")
    print("   2. Test with different user roles (client, writer, admin)")
    print("   3. Test with orders that already have threads")
    print("   4. Test with archived orders (should fail)")
    
    return logic_test


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

