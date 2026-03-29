# Session Management with Idle Timeout - Implementation

## Overview

This document outlines the implementation of session management with idle timeout, including warning dialogs and automatic logout.

---

## ✅ Backend Implementation

### **1. Session Timeout Middleware**

**File**: `authentication/middleware/session_timeout.py`

- Tracks last activity timestamp for each user
- Automatically logs out users after idle timeout
- Adds session info to response headers
- Configurable timeout periods

### **2. Session Management API**

**File**: `authentication/views/session_management.py`

**Endpoints**:
- `GET /api/v1/auth/session/status/` - Get session status
- `POST /api/v1/auth/session/extend/` - Extend session
- `POST /api/v1/auth/session/logout/` - Manual logout

---

## ⚙️ Configuration

Add to `writing_system/settings.py`:

```python
# Session timeout settings (in seconds)
SESSION_IDLE_TIMEOUT = 30 * 60  # 30 minutes
SESSION_WARNING_TIME = 5 * 60   # 5 minutes before timeout

# Middleware
MIDDLEWARE = [
    # ... other middleware ...
    'authentication.middleware.session_timeout.SessionTimeoutMiddleware',
    # ... rest of middleware ...
]
```

---

## 🎨 Frontend Implementation

### **Features**

1. **Idle Detection**
   - Track user activity (mouse, keyboard, scroll)
   - Reset timer on activity

2. **Warning Dialog**
   - Show when 5 minutes remaining
   - Countdown timer
   - "Stay Logged In" button

3. **Auto Logout**
   - Automatic logout after idle timeout
   - Redirect to login page

4. **Session Status API**
   - Poll session status every 30 seconds
   - Update countdown display

---

## 📋 Implementation Steps

### **Backend**

1. ✅ Create middleware
2. ✅ Create session management views
3. ⏳ Add middleware to settings
4. ⏳ Register URLs
5. ⏳ Test endpoints

### **Frontend**

1. ⏳ Create session monitor service
2. ⏳ Create warning dialog component
3. ⏳ Add to main layout
4. ⏳ Test idle detection
5. ⏳ Test auto-logout

---

## 🔄 Workflow

1. User logs in → Session starts, last_activity set
2. User is active → Last activity updated on each request
3. User becomes idle → Timer counts down
4. 5 minutes remaining → Warning dialog appears
5. User clicks "Stay Logged In" → Session extended
6. Timeout reached → Auto logout, redirect to login

---

## 📊 API Response Examples

### **Session Status**
```json
{
  "is_active": true,
  "remaining_seconds": 1800,
  "idle_seconds": 0,
  "warning_threshold": 300,
  "should_warn": false,
  "timeout_seconds": 1800
}
```

### **Extend Session**
```json
{
  "message": "Session extended successfully",
  "remaining_seconds": 1800,
  "extended_at": 1700123456.789
}
```

---

**Status**: ⏳ **Implementation In Progress**

