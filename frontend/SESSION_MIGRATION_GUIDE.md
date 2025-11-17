# Session Management Migration Guide

## Problem
The application was making excessive requests to session management endpoints, causing 429 (Too Many Requests) errors.

## Solution Implemented

### 1. Global Session Management (App.vue)
The `App.vue` component now includes global session management that:
- Automatically polls session status every 60 seconds
- Handles rate limiting and caching
- Shows a warning banner when session is about to expire
- Allows manual session extension

### 2. Backend Improvements
- Custom throttle: 200 requests/hour (allows ~3 per minute)
- Increased cache time: 10 seconds for status endpoint
- Better error handling

## Finding and Fixing Existing Code

### Step 1: Search for Problematic Code

Run these searches in your codebase:

```bash
# Search for direct API calls
grep -r "session-management/extend" frontend/src/
grep -r "session-management/status" frontend/src/

# Search for axios calls to these endpoints
grep -r "axios.*extend" frontend/src/
grep -r "axios.*status" frontend/src/

# Search for polling intervals
grep -r "setInterval" frontend/src/ | grep -i "session\|extend\|status"
grep -r "setTimeout" frontend/src/ | grep -i "session\|extend\|status"
```

### Step 2: Common Patterns to Replace

#### Pattern 1: Direct Axios Calls
**Before:**
```javascript
// ❌ Don't do this
setInterval(async () => {
  try {
    await axios.get('/api/v1/auth/session-management/status/')
    await axios.post('/api/v1/auth/session-management/extend/')
  } catch (error) {
    console.error(error)
  }
}, 5000) // Too frequent!
```

**After:**
```javascript
// ✅ Use the composable (already in App.vue globally)
// Or import in specific components:
import { useSessionManagement } from '@/composables/useSessionManagement'

export default {
  setup() {
    const { sessionStatus, extendSession } = useSessionManagement({
      checkInterval: 60000 // 60 seconds
    })
    return { sessionStatus, extendSession }
  }
}
```

#### Pattern 2: Manual Polling
**Before:**
```javascript
// ❌ Don't do this
mounted() {
  this.checkSession()
  this.interval = setInterval(() => {
    this.checkSession()
  }, 10000) // Too frequent!
}

methods: {
  async checkSession() {
    const response = await axios.get('/api/v1/auth/session-management/status/')
    // ...
  }
}
```

**After:**
```javascript
// ✅ Use the composable
import { useSessionManagement } from '@/composables/useSessionManagement'

export default {
  setup() {
    // Automatically handles polling with rate limiting
    const { sessionStatus } = useSessionManagement()
    return { sessionStatus }
  }
}
```

#### Pattern 3: Multiple Components Polling
**Before:**
```javascript
// ❌ If multiple components are polling independently
// Component A
setInterval(() => axios.get('/api/v1/auth/session-management/status/'), 5000)

// Component B  
setInterval(() => axios.get('/api/v1/auth/session-management/status/'), 5000)
```

**After:**
```javascript
// ✅ Use the global instance in App.vue
// All components can access sessionStatus from the store or props
// Or use the composable which shares the same rate limiting
```

### Step 3: Remove Old Code

1. **Remove setInterval/setTimeout** that poll session endpoints
2. **Remove direct axios calls** to `/api/v1/auth/session-management/*`
3. **Remove manual session checking** code
4. **Keep** the composable usage in App.vue (already added)

### Step 4: Verify Fix

After making changes:

1. **Check browser console** - should see no 429 errors
2. **Check network tab** - session endpoints should be called max once per 10 seconds
3. **Check backend logs** - should see fewer throttling messages

## Testing

### Test Rate Limiting
1. Open browser DevTools → Network tab
2. Filter for "session-management"
3. Verify requests are spaced at least 10 seconds apart
4. Verify no 429 errors appear

### Test Session Extension
1. Wait for session warning to appear (if configured)
2. Click "Extend Session" button
3. Verify session is extended
4. Verify no 429 errors

## Common Issues

### Issue: Still Getting 429 Errors
**Solution:**
- Check if multiple components are using the composable independently
- Increase `checkInterval` to a larger value (e.g., 120000 for 2 minutes)
- Check if there's old code still polling that wasn't removed

### Issue: Session Status Not Updating
**Solution:**
- Status is cached for 10 seconds - wait a bit
- Check browser console for errors
- Verify authentication token is valid

### Issue: Warning Banner Not Showing
**Solution:**
- Check if `sessionStatus.should_warn` is true
- Verify the banner CSS is loaded
- Check browser console for errors

## Files Modified

1. ✅ `frontend/src/App.vue` - Added global session management
2. ✅ `frontend/src/composables/useSessionManagement.js` - Created composable
3. ✅ `authentication/views/session_management_viewset.py` - Updated backend throttling

## Next Steps

1. Search your codebase for the patterns mentioned above
2. Replace any found code with the composable
3. Test the application
4. Monitor backend logs for 429 errors

## Need Help?

If you find code that's calling these endpoints but aren't sure how to fix it:
1. Note the file path and line numbers
2. Share the code snippet
3. We can help convert it to use the composable

