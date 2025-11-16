#!/usr/bin/env python
"""
Test script to verify SSE (Server-Sent Events) configuration.
This tests the SSE endpoint and connection management.
"""
import os
import sys
import django
import requests
import json
from time import sleep

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.conf import settings

User = get_user_model()


def test_sse_endpoint():
    """Test SSE endpoint configuration."""
    print("=" * 60)
    print("SSE (Server-Sent Events) Configuration Test")
    print("=" * 60)
    
    # Check if SSE is enabled
    print("\n📋 Checking Configuration...")
    
    # Check notification settings
    sse_enabled = getattr(settings, 'NOTIFICATION_ENABLED_CHANNELS', {}).get('sse', False)
    print(f"  {'✅' if sse_enabled else '❌'} SSE Channel Enabled: {sse_enabled}")
    
    # Check URL configuration
    print("\n🔗 Checking URL Configuration...")
    try:
        from django.urls import reverse
        sse_url = reverse('notifications:sse_stream')
        print(f"  ✅ SSE URL configured: {sse_url}")
    except Exception as e:
        print(f"  ❌ SSE URL not found: {e}")
        return False
    
    # Test with Django test client
    print("\n🧪 Testing SSE Endpoint...")
    
    # Create or get test user
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("  ⚠️  No superuser found. Creating test user...")
            user = User.objects.create_user(
                username='test_sse_user',
                email='test_sse@example.com',
                password='test_password_123'
            )
            print(f"  ✅ Created test user: {user.username}")
        else:
            print(f"  ✅ Using existing user: {user.username}")
    except Exception as e:
        print(f"  ❌ Failed to get/create user: {e}")
        return False
    
    # Create authenticated client
    client = Client()
    logged_in = client.login(username=user.username, password='test_password_123' if user.username == 'test_sse_user' else None)
    
    if not logged_in and user.username != 'test_sse_user':
        print("  ⚠️  Could not auto-login. Please test manually via frontend.")
        print("  📝 SSE endpoint: /api/v1/notifications/sse/stream/")
        return True
    
    # Test SSE endpoint
    print("\n📡 Testing SSE Connection...")
    try:
        response = client.get('/api/v1/notifications/sse/stream/', HTTP_ACCEPT='text/event-stream')
        
        if response.status_code == 200:
            print(f"  ✅ SSE endpoint responding: {response.status_code}")
            print(f"  ✅ Content-Type: {response.get('Content-Type', 'Not set')}")
            
            # Check response headers
            if 'text/event-stream' in response.get('Content-Type', ''):
                print("  ✅ Correct Content-Type header")
            else:
                print("  ⚠️  Content-Type may not be correct")
            
            # Check for SSE headers
            cache_control = response.get('Cache-Control', '')
            if 'no-cache' in cache_control:
                print("  ✅ Cache-Control header set correctly")
            
            print("\n✅ SSE endpoint is working!")
            return True
        else:
            print(f"  ❌ SSE endpoint returned status: {response.status_code}")
            print(f"  Response: {response.content[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing SSE endpoint: {e}")
        return False


def test_sse_connection_manager():
    """Test SSE connection manager."""
    print("\n" + "=" * 60)
    print("Testing SSE Connection Manager...")
    print("=" * 60)
    
    try:
        from notifications_system.delivery.sse import get_connection_manager
        
        manager = get_connection_manager()
        print("  ✅ Connection manager imported successfully")
        
        # Test connection methods
        connections = manager.get_all_connections()
        print(f"  ✅ Active connections: {len(connections)}")
        
        return True
        
    except ImportError as e:
        print(f"  ⚠️  Connection manager not available: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error testing connection manager: {e}")
        return False


def show_sse_integration_example():
    """Show frontend integration example."""
    print("\n" + "=" * 60)
    print("Frontend Integration Example")
    print("=" * 60)
    
    example = """
// JavaScript/TypeScript Example for Frontend

// 1. Basic SSE Connection
const eventSource = new EventSource('/api/v1/notifications/sse/stream/', {
    withCredentials: true  // Include authentication cookies
});

// 2. Handle incoming notifications
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('New notification:', data);
    
    // Update UI
    updateNotificationBadge(data);
    showNotificationToast(data);
};

// 3. Handle specific event types
eventSource.addEventListener('notification', (event) => {
    const notification = JSON.parse(event.data);
    handleNotification(notification);
});

eventSource.addEventListener('heartbeat', (event) => {
    // Connection is alive
    console.log('SSE heartbeat received');
});

// 4. Handle errors
eventSource.onerror = (error) => {
    console.error('SSE connection error:', error);
    // EventSource will automatically reconnect
};

// 5. Close connection when done
// eventSource.close();

// 6. With Authentication (if using JWT)
const token = localStorage.getItem('access_token');
const eventSource = new EventSource(
    `/api/v1/notifications/sse/stream/?token=${token}`
);

// Or use fetch with credentials
fetch('/api/v1/notifications/sse/stream/', {
    credentials: 'include',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
    """
    
    print(example)
    
    print("\n📝 Vue.js Example:")
    vue_example = """
// In your Vue component
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  setup() {
    const notifications = ref([])
    let eventSource = null
    
    onMounted(() => {
      const authStore = useAuthStore()
      const token = authStore.token
      
      // Connect to SSE stream
      eventSource = new EventSource(
        `/api/v1/notifications/sse/stream/`,
        {
          withCredentials: true,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)
        notifications.value.unshift(data)
      }
      
      eventSource.onerror = (error) => {
        console.error('SSE error:', error)
      }
    })
    
    onUnmounted(() => {
      if (eventSource) {
        eventSource.close()
      }
    })
    
    return { notifications }
  }
}
    """
    
    print(vue_example)


if __name__ == '__main__':
    print("\n")
    
    # Test SSE configuration
    config_ok = test_sse_endpoint()
    
    # Test connection manager
    manager_ok = test_sse_connection_manager()
    
    # Show integration examples
    show_sse_integration_example()
    
    print("\n" + "=" * 60)
    if config_ok:
        print("✅ SSE configuration test complete!")
        print("\n📝 Next Steps:")
        print("  1. Integrate SSE in your frontend (see examples above)")
        print("  2. Replace polling with SSE connections")
        print("  3. Test with real notifications")
    else:
        print("⚠️  Some SSE tests failed. Check configuration.")
    print("=" * 60)

