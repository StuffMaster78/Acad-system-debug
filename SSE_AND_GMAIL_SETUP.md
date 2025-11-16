# SSE & Gmail Setup Guide

**Complete setup guide for Server-Sent Events (SSE) and Gmail email notifications**

---

## 📋 Table of Contents

1. [SSE Implementation Status](#sse-implementation-status)
2. [Gmail SMTP Setup](#gmail-smtp-setup)
3. [Environment Configuration](#environment-configuration)
4. [Testing](#testing)
5. [Frontend Integration](#frontend-integration)

---

## ✅ SSE Implementation Status

### Backend: **Fully Implemented** ✅

Your system already has SSE fully implemented:

**Endpoints:**
- `GET /api/v1/notifications/sse/stream/` - SSE stream for real-time notifications
- `GET /api/v1/notifications/sse/status/` - Check SSE connection status
- `POST /api/v1/notifications/sse/close/` - Close SSE connection

**Implementation Files:**
- `notifications_system/delivery/sse.py` - SSE backend implementation
- `notifications_system/views/sse.py` - SSE view endpoints
- `notifications_system/urls.py` - URL routing

**Features:**
- ✅ Automatic reconnection
- ✅ Heartbeat system (30-second intervals)
- ✅ Connection management
- ✅ Event batching
- ✅ User authentication
- ✅ Performance monitoring

**No additional backend work needed!** ✅

---

## 📧 Gmail SMTP Setup

### Step 1: Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under **Signing in to Google**, click **2-Step Verification**
4. Follow the prompts to enable 2-Step Verification
   - You'll need to verify your phone number
   - You'll receive a verification code via SMS

**Why?** Gmail requires 2-Step Verification to generate App Passwords for SMTP.

---

### Step 2: Generate App Password

1. Go back to **Security** settings: https://myaccount.google.com/security
2. Under **Signing in to Google**, click **App passwords**
   - If you don't see this option, make sure 2-Step Verification is enabled
3. Select **Mail** as the app
4. Select **Other (Custom name)** as the device
5. Enter a name like: **"Writing System Backend"**
6. Click **Generate**
7. **Copy the 16-character password** (you'll see it only once!)
   - Format: `xxxx xxxx xxxx xxxx` (remove spaces when using)

**Important:** This is a one-time password. Save it securely!

---

### Step 3: Configure Environment Variables

#### Option A: Using `.env` file (Recommended for Development)

Create a `.env` file in your project root (`/Users/awwy/writing_system_backend/.env`):

```bash
# Gmail SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Replace:**
- `your-email@gmail.com` with your Gmail address
- `your-16-char-app-password` with the App Password (remove spaces)

#### Option B: Using Docker Environment Variables

If using Docker, add to `docker-compose.yml`:

```yaml
services:
  web:
    environment:
      - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
      - EMAIL_HOST=smtp.gmail.com
      - EMAIL_PORT=587
      - EMAIL_USE_TLS=True
      - EMAIL_HOST_USER=your-email@gmail.com
      - EMAIL_HOST_PASSWORD=your-16-char-app-password
      - DEFAULT_FROM_EMAIL=your-email@gmail.com
```

#### Option C: Export in Shell (Temporary)

```bash
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER=your-email@gmail.com
export EMAIL_HOST_PASSWORD=your-16-char-app-password
export DEFAULT_FROM_EMAIL=your-email@gmail.com
```

---

## 🔧 Environment Configuration

### Complete `.env` File Template

Create `.env` in your project root:

```bash
# Database Configuration
DB_HOST=db
DB_PORT=5432
POSTGRES_USER_NAME=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB_NAME=writing_system_db

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Gmail SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

**Note:** Make sure `.env` is in `.gitignore` to avoid committing credentials!

---

## 🧪 Testing

### Test Email Configuration

Run the test script:

```bash
python manage.py shell
```

Then run:

```python
from django.core.mail import send_mail
from django.conf import settings

# Test email
send_mail(
    subject='Test Email from Writing System',
    message='This is a test email to verify Gmail SMTP configuration.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-test-email@gmail.com'],
    fail_silently=False,
)
```

**Expected Result:** You should receive an email in your inbox.

### Test SSE Connection

#### Using curl:

```bash
# First, get your authentication token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com","password":"your-password"}' \
  | jq -r '.access')

# Then test SSE stream
curl -N -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/notifications/sse/stream/
```

#### Using Python:

```python
import requests
import json

# Login to get token
login_response = requests.post(
    'http://localhost:8000/api/v1/auth/login/',
    json={'email': 'your-email@example.com', 'password': 'your-password'}
)
token = login_response.json()['access']

# Test SSE stream
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:8000/api/v1/notifications/sse/stream/',
    headers=headers,
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### Automated Test Script

I'll create a test script for you (see `test_sse_and_email.py` below).

---

## 🎨 Frontend Integration

### SSE Client Implementation

Add this to your frontend (Vue.js example):

```javascript
// src/utils/sse.js
export class SSENotificationClient {
  constructor(apiBaseUrl, authToken) {
    this.apiBaseUrl = apiBaseUrl;
    this.authToken = authToken;
    this.eventSource = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const url = `${this.apiBaseUrl}/notifications/sse/stream/`;
    
    this.eventSource = new EventSource(url, {
      headers: {
        'Authorization': `Bearer ${this.authToken}`
      }
    });

    this.eventSource.onopen = () => {
      console.log('SSE connection opened');
      this.reconnectAttempts = 0;
    };

    this.eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleNotification(data);
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      this.handleReconnect();
    };

    // Handle custom event types
    this.eventSource.addEventListener('notification', (event) => {
      const data = JSON.parse(event.data);
      this.handleNotification(data);
    });

    this.eventSource.addEventListener('heartbeat', (event) => {
      // Connection is alive
      console.log('SSE heartbeat received');
    });
  }

  handleNotification(data) {
    // Emit event or update store
    // Example: Vue event bus or Pinia store
    console.log('New notification:', data);
    
    // Update notification count
    // Show notification toast
    // Update notification list
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      
      setTimeout(() => {
        console.log(`Reconnecting SSE (attempt ${this.reconnectAttempts})...`);
        this.connect();
      }, delay);
    } else {
      console.error('Max SSE reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}
```

### Vue Component Usage

```vue
<script setup>
import { onMounted, onUnmounted } from 'vue';
import { SSENotificationClient } from '@/utils/sse';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
let sseClient = null;

onMounted(() => {
  if (authStore.isAuthenticated) {
    sseClient = new SSENotificationClient(
      import.meta.env.VITE_API_BASE_URL,
      authStore.token
    );
    sseClient.connect();
  }
});

onUnmounted(() => {
  if (sseClient) {
    sseClient.disconnect();
  }
});
</script>
```

**Note:** EventSource doesn't support custom headers in all browsers. You may need to:
1. Pass token as query parameter: `/sse/stream/?token=...`
2. Or use a proxy endpoint that adds the header server-side

---

## 🔍 Troubleshooting

### Email Issues

**Problem:** "Authentication failed"
- ✅ Check that 2-Step Verification is enabled
- ✅ Verify App Password is correct (no spaces)
- ✅ Ensure `EMAIL_HOST_USER` matches your Gmail address

**Problem:** "Connection timeout"
- ✅ Check firewall/proxy settings
- ✅ Verify `EMAIL_PORT=587` (TLS) or `EMAIL_PORT=465` (SSL)
- ✅ Ensure `EMAIL_USE_TLS=True` for port 587

**Problem:** "SMTP server not found"
- ✅ Verify `EMAIL_HOST=smtp.gmail.com`
- ✅ Check network connectivity

### SSE Issues

**Problem:** "401 Unauthorized"
- ✅ Check authentication token is valid
- ✅ Verify user is logged in
- ✅ Check token expiration

**Problem:** "Connection closes immediately"
- ✅ Check server logs for errors
- ✅ Verify Redis is running (for event storage)
- ✅ Check user notification preferences

**Problem:** "No events received"
- ✅ Verify notifications are being created
- ✅ Check SSE delivery backend is enabled
- ✅ Verify user has notification preferences set

---

## 📊 Monitoring

### Check SSE Connections

```bash
# Check active SSE connections
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/notifications/sse/status/
```

### Check Email Configuration

```python
from django.conf import settings

print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
```

---

## ✅ Verification Checklist

- [ ] Gmail 2-Step Verification enabled
- [ ] App Password generated and saved
- [ ] `.env` file created with email credentials
- [ ] Email test successful
- [ ] SSE endpoint accessible
- [ ] Frontend SSE client implemented
- [ ] Notifications being delivered via SSE
- [ ] Email notifications working

---

## 🚀 Next Steps

1. **Test Email:** Run email test script
2. **Test SSE:** Connect frontend to SSE endpoint
3. **Replace Polling:** Remove 30-second polling, use SSE instead
4. **Monitor:** Check connection status and performance

---

**Last Updated:** December 2024  
**Status:** Ready for implementation ✅

