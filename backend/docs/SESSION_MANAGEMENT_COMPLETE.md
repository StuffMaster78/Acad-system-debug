# Session Management with Idle Timeout - Implementation Complete

## ✅ Implementation Summary

A comprehensive session management system with idle timeout has been implemented, including warning dialogs and automatic logout.

---

## 🎯 Features Implemented

### **1. Backend - Session Timeout Middleware**
- **File**: `authentication/middleware/session_timeout.py`
- Tracks last activity timestamp for each user
- Automatically logs out users after idle timeout (default: 30 minutes)
- Adds session info to response headers
- Configurable timeout periods

### **2. Backend - Session Management API**
- **File**: `authentication/views/session_management_viewset.py`
- Enhanced existing ViewSet with idle timeout endpoints

**Endpoints**:
- `GET /api/v1/auth/session-management/status/` - Get session status
- `POST /api/v1/auth/session-management/extend/` - Extend session (reset idle timer)
- `POST /api/v1/auth/session-management/logout/` - Manual logout

### **3. Frontend - Session Manager Service**
- **File**: `src/services/sessionManager.js`
- Monitors session status every 30 seconds
- Tracks user activity (mouse, keyboard, scroll, touch)
- Automatically extends session on activity
- Shows warning when 5 minutes remaining
- Handles auto-logout

### **4. Frontend - Warning Dialog Component**
- **File**: `src/components/common/SessionTimeoutWarning.vue`
- Professional warning modal
- Countdown timer display
- Progress bar visualization
- "Stay Logged In" and "Logout Now" buttons

### **5. Frontend - Dashboard Integration**
- **File**: `src/layouts/DashboardLayout.vue`
- Integrated session monitoring
- Auto-starts on mount
- Auto-stops on unmount
- Handles logout callback

---

## ⚙️ Configuration

### **Backend Settings** (`writing_system/settings.py`)

```python
# Session idle timeout settings (in seconds)
SESSION_IDLE_TIMEOUT = 30 * 60  # 30 minutes (default)
SESSION_WARNING_TIME = 5 * 60   # 5 minutes before timeout (default)

# Middleware (already added)
MIDDLEWARE = [
    # ...
    'authentication.middleware.session_timeout.SessionTimeoutMiddleware',
    # ...
]
```

### **Environment Variables** (Optional)

```bash
SESSION_IDLE_TIMEOUT=1800  # 30 minutes in seconds
SESSION_WARNING_TIME=300    # 5 minutes in seconds
```

---

## 🔄 Workflow

1. **User Logs In** → Session starts, `last_activity` timestamp set
2. **User is Active** → Last activity updated on each request/activity
3. **User Becomes Idle** → Timer counts down
4. **5 Minutes Remaining** → Warning dialog appears with countdown
5. **User Clicks "Stay Logged In"** → Session extended, timer reset
6. **Timeout Reached** → Auto logout, redirect to login

---

## 📊 API Response Examples

### **Session Status**
```json
GET /api/v1/auth/session-management/status/

{
  "is_active": true,
  "remaining_seconds": 1800,
  "idle_seconds": 0,
  "warning_threshold": 300,
  "should_warn": false,
  "timeout_seconds": 1800,
  "last_activity": 1700123456.789
}
```

### **Extend Session**
```json
POST /api/v1/auth/session-management/extend/

{
  "message": "Session extended successfully",
  "remaining_seconds": 1800,
  "extended_at": 1700123456.789
}
```

---

## 🎨 Frontend Features

### **Warning Dialog**
- **Title**: "Your Session is About to Expire!"
- **Message**: "Your session will be logged out in X minutes Y seconds."
- **Countdown**: Real-time countdown display
- **Progress Bar**: Visual progress indicator
- **Actions**:
  - "Stay Logged In" - Extends session
  - "Logout Now" - Immediate logout

### **Activity Tracking**
- Monitors: mouse, keyboard, scroll, touch events
- Automatically extends session on activity
- No manual intervention needed for active users

---

## 🧪 Testing

### **Test Idle Timeout**
1. Log in to the system
2. Leave the page idle for 25 minutes
3. Warning dialog should appear at 25 minutes (5 min remaining)
4. Countdown should show remaining time
5. Click "Stay Logged In" to extend
6. Or wait for auto-logout at 30 minutes

### **Test Activity Tracking**
1. Log in to the system
2. Use the system normally (click, type, scroll)
3. Session should automatically extend
4. No warning should appear if active

---

## 📋 Files Created/Modified

### **Backend**
- ✅ `authentication/middleware/session_timeout.py` (created)
- ✅ `authentication/middleware/__init__.py` (created)
- ✅ `authentication/views/session_management_viewset.py` (enhanced)
- ✅ `writing_system/settings.py` (added middleware and settings)

### **Frontend**
- ✅ `src/services/sessionManager.js` (created)
- ✅ `src/components/common/SessionTimeoutWarning.vue` (created)
- ✅ `src/layouts/DashboardLayout.vue` (integrated)

---

## ✅ Status

**Backend**: ✅ **Complete**
- Middleware implemented
- API endpoints ready
- Settings configured

**Frontend**: ✅ **Complete**
- Session manager service ready
- Warning dialog component ready
- Dashboard integration complete

**Ready for Testing**: ✅ **Yes**

---

## 🚀 Next Steps

1. **Test the system**:
   - Log in and leave idle
   - Verify warning appears
   - Test "Stay Logged In" button
   - Test auto-logout

2. **Customize timeouts** (if needed):
   - Update `SESSION_IDLE_TIMEOUT` in settings
   - Update `SESSION_WARNING_TIME` in settings

3. **Optional enhancements**:
   - Add session timeout indicator in header
   - Add "Extend Session" button in user menu
   - Add session history/logging

---

**Status**: ✅ **Implementation Complete - Ready for Testing!**

