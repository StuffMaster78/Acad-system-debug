# Session Management Usage Guide

## Problem
The session management endpoints were being called too frequently, causing 429 (Too Many Requests) errors.

## Solution
Use the `useSessionManagement` composable which automatically handles:
- Rate limiting (10s cache for status, 30s minimum for extend)
- Error handling (graceful degradation on 429)
- Automatic polling (configurable interval)

## Quick Start

### 1. Import the Composable
```javascript
import { useSessionManagement } from '@/composables/useSessionManagement'
```

### 2. Use in Your Component
```javascript
export default {
  setup() {
    const { 
      sessionStatus,  // Current session status
      loading,        // Loading state
      error,          // Error message
      extendSession   // Manual extend function
    } = useSessionManagement({
      checkInterval: 60000,    // Check every 60 seconds (default)
      autoExtend: true,         // Auto-extend when needed (default)
      extendBeforeWarning: true // Extend before warning threshold (default)
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

### 3. Display Session Status (Optional)
```vue
<template>
  <div v-if="sessionStatus">
    <p>Session expires in: {{ Math.floor(sessionStatus.remaining_seconds / 60) }} minutes</p>
    <button v-if="sessionStatus.should_warn" @click="extendSession">
      Extend Session
    </button>
  </div>
</template>
```

## API Reference

### `useSessionManagement(options)`

#### Options
- `checkInterval` (number): Milliseconds between status checks. Default: `60000` (1 minute)
- `autoExtend` (boolean): Automatically extend session when warning threshold reached. Default: `true`
- `extendBeforeWarning` (boolean): Extend before warning threshold. Default: `true`

#### Returns
- `sessionStatus` (ref): Current session status object:
  ```javascript
  {
    is_active: true,
    remaining_seconds: 1800,
    idle_seconds: 0,
    warning_threshold: 300,
    should_warn: false,
    timeout_seconds: 1800
  }
  ```
- `loading` (ref): Boolean indicating if a request is in progress
- `error` (ref): Error message string or null
- `checkSession()`: Manually trigger a status check
- `extendSession()`: Manually extend the session
- `startPolling()`: Start automatic polling
- `stopPolling()`: Stop automatic polling

## Manual API Calls

If you need to call the endpoints directly (not recommended):

```javascript
import { getSessionStatus, extendSession } from '@/composables/useSessionManagement'

// Get status (cached for 10 seconds)
const status = await getSessionStatus()

// Extend session (throttled to max once per 30 seconds)
const result = await extendSession()
```

## Migration Guide

### Step 1: Find Old Code
Search your codebase for:
```bash
grep -r "session-management/extend" frontend/src/
grep -r "session-management/status" frontend/src/
```

### Step 2: Replace Direct Calls
Replace direct axios calls with the composable:

**Before:**
```javascript
// ❌ Old way
setInterval(async () => {
  try {
    await axios.get('/api/v1/auth/session-management/status/')
  } catch (error) {
    console.error(error)
  }
}, 5000)
```

**After:**
```javascript
// ✅ New way
import { useSessionManagement } from '@/composables/useSessionManagement'

export default {
  setup() {
    const { sessionStatus } = useSessionManagement({
      checkInterval: 60000 // Much less frequent
    })
    return { sessionStatus }
  }
}
```

### Step 3: Remove Manual Polling
Remove any `setInterval` or `setTimeout` calls that poll these endpoints.

## Best Practices

1. **Use the composable** instead of direct API calls
2. **Don't poll more than once per minute** - the composable defaults to 60 seconds
3. **Let auto-extend handle session extension** - don't manually extend unless necessary
4. **Handle errors gracefully** - the composable already does this, but check `error` ref if needed

## Troubleshooting

### Still Getting 429 Errors?
1. Check if you have multiple components using the composable - they share the same rate limits
2. Increase `checkInterval` to a larger value (e.g., 120000 for 2 minutes)
3. Disable `autoExtend` if you're manually extending elsewhere

### Session Status Not Updating?
- The status is cached for 10 seconds - wait a bit and try again
- Check browser console for errors
- Verify authentication token is valid

### Need More Frequent Updates?
- The backend allows 200 requests per hour (~3 per minute)
- Don't poll more frequently than every 20 seconds
- Consider using WebSockets for real-time updates (future enhancement)

