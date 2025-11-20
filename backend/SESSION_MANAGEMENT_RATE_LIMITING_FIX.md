# Session Management Rate Limiting Fix

## Problem
The frontend was making excessive requests to `/api/v1/auth/session-management/extend/` and `/api/v1/auth/session-management/status/`, causing rate limiting errors (429) with wait times of 1500+ seconds.

## Root Cause
- Frontend components were polling these endpoints too frequently (possibly every few seconds)
- No rate limiting or throttling on the frontend side
- Backend rate limits were too strict for legitimate polling use cases

## Solution

### 1. Frontend Rate Limiting
Created `frontend/src/composables/useSessionManagement.js` with:
- **Status endpoint**: Cached for 10 seconds (prevents requests more than once per 10 seconds)
- **Extend endpoint**: Minimum 30 seconds between requests
- **Polling interval**: Default 60 seconds (1 minute) between checks
- Automatic error handling for 429 responses (returns cached data)

### 2. Backend Improvements
The backend already has:
- 5-second cache for status endpoint
- Safe error handling

### 3. Usage

#### In Vue Components:
```javascript
import { useSessionManagement } from '@/composables/useSessionManagement'

export default {
  setup() {
    const { sessionStatus, loading, error, extendSession } = useSessionManagement({
      checkInterval: 60000, // Check every 60 seconds (default)
      autoExtend: true // Automatically extend when needed
    })
    
    return {
      sessionStatus,
      loading,
      error,
      extendSession
    }
  }
}
```

#### Manual API Calls:
```javascript
import { getSessionStatus, extendSession } from '@/composables/useSessionManagement'

// Get status (automatically cached for 10 seconds)
const status = await getSessionStatus()

// Extend session (automatically throttled to max once per 30 seconds)
const result = await extendSession()
```

## Implementation Steps

1. **Update components that call session endpoints** to use the new composable
2. **Remove any direct axios calls** to these endpoints
3. **Replace setInterval/setTimeout polling** with the composable's built-in polling

## Finding Components That Need Updates

Search for:
- `session-management/extend`
- `session-management/status`
- `axios.*session`
- `setInterval.*session`

## Quick Fix: Update Existing Code

### Before (Problematic):
```javascript
// ❌ Don't do this - causes rate limiting
setInterval(async () => {
  await axios.get('/api/v1/auth/session-management/status/')
  await axios.post('/api/v1/auth/session-management/extend/')
}, 5000) // Every 5 seconds - too frequent!
```

### After (Fixed):
```javascript
// ✅ Use the composable instead
import { useSessionManagement } from '@/composables/useSessionManagement'

export default {
  setup() {
    // Automatically handles rate limiting and caching
    const { sessionStatus, extendSession } = useSessionManagement({
      checkInterval: 60000, // Every 60 seconds
      autoExtend: true
    })
    
    return { sessionStatus, extendSession }
  }
}
```

## Expected Behavior After Fix

- Status checks: Maximum once per 10 seconds (cached)
- Session extends: Maximum once per 30 seconds
- Polling: Once per 60 seconds (configurable)
- No more 429 errors for legitimate use
- Graceful degradation when rate limited (returns cached data)

## Backend Rate Limit Configuration

If you need to adjust backend rate limits, check:
- `REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']` in settings.py
- ViewSet-level throttle classes if configured

The default DRF throttling is usually:
- Anonymous: 100/hour
- User: 1000/hour

For session management endpoints, consider:
- User: 200/hour (allows ~3 requests per minute, which is reasonable for polling)

