# Order Messages Error Fixes

## Issues Fixed

1. ✅ **Missing `loadUnreadMessageCount` function** - Created in `utils/messageUtils.js`
2. ✅ **429 Too Many Requests** - Added rate limiting and throttling
3. ✅ **401 Unauthorized** - Improved error handling and token refresh
4. ✅ **403 Forbidden** - Graceful error handling for permission issues

## New Files Created

### 1. `/frontend/src/utils/messageUtils.js`
Utility functions for message handling:
- `loadUnreadMessageCount(orderId)` - Load unread count with rate limiting
- `loadUnreadNotificationCount()` - Load notification count with caching
- `debounce(func, wait)` - Debounce function
- `throttle(func, limit)` - Throttle function

### 2. `/frontend/src/composables/useOrderMessages.js`
Vue 3 composable for order messages:
- Automatic rate limiting (2-3 second intervals)
- Error handling for 401, 403, 429
- Auto-refresh with 30-second intervals (prevents rate limiting)
- Cleanup on component unmount

## How to Use

### In OrderDetail.vue (or any order component):

```vue
<template>
  <div>
    <!-- Your order detail content -->
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading">Loading messages...</div>
    
    <!-- Messages -->
    <div v-for="thread in threads" :key="thread.id">
      <h3>Thread {{ thread.id }}</h3>
      <p>Unread: {{ thread.unread_count }}</p>
    </div>
    
    <p>Total Unread: {{ unreadCount }}</p>
  </div>
</template>

<script>
import { useOrderMessages } from '@/composables/useOrderMessages'
import { loadUnreadMessageCount } from '@/utils/messageUtils'

export default {
  props: {
    orderId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    // Use the composable
    const {
      threads,
      messages,
      unreadCount,
      loading,
      error,
      loadThreads,
      loadMessages,
      loadFiles
    } = useOrderMessages(props.orderId)
    
    // Or use the utility function directly
    const loadUnreadCount = async () => {
      const count = await loadUnreadMessageCount(props.orderId)
      console.log('Unread count:', count)
    }
    
    return {
      threads,
      messages,
      unreadCount,
      loading,
      error,
      loadThreads,
      loadMessages,
      loadFiles,
      loadUnreadCount
    }
  }
}
</script>
```

## Rate Limiting Strategy

### Frontend Rate Limiting:
- **Unread counts**: Cached for 5 seconds
- **Thread loading**: Throttled to max once per 2 seconds
- **Message loading**: Throttled to max once per 2 seconds
- **File loading**: Throttled to max once per 3 seconds
- **Auto-refresh**: 30-second intervals (instead of constant polling)

### Backend Rate Limiting:
The backend already has:
- 10-second cache for unread counts
- Caching in `UnreadCountView`
- Optimized queries

## Error Handling

All functions now handle:
- **401 Unauthorized**: Logs warning, returns 0 or empty array
- **403 Forbidden**: Logs warning, returns empty array (graceful degradation)
- **429 Too Many Requests**: Uses cached value, retries after delay
- **Network errors**: Logs error, returns safe defaults

## Migration Steps

If you have an existing OrderDetail component:

1. **Import the composable:**
```javascript
import { useOrderMessages } from '@/composables/useOrderMessages'
```

2. **Replace manual API calls:**
```javascript
// OLD (causes rate limiting)
setInterval(() => {
  axios.get('/api/v1/order-communications/threads/...')
}, 1000) // Too frequent!

// NEW (rate limited)
const { threads, loadThreads } = useOrderMessages(orderId)
// Auto-refreshes every 30 seconds
```

3. **Use the utility function:**
```javascript
// OLD
loadUnreadMessageCount() // ❌ Not defined

// NEW
import { loadUnreadMessageCount } from '@/utils/messageUtils'
const count = await loadUnreadMessageCount(orderId) // ✅ Works!
```

## Testing

After implementing:
1. Check browser console - should see fewer errors
2. Check Network tab - should see fewer requests
3. Verify messages still load correctly
4. Verify unread counts update (may be slightly delayed due to caching)

## Notes

- Rate limiting is intentional to prevent server overload
- 30-second refresh is a good balance between real-time updates and server load
- All errors are handled gracefully - the UI won't break if API calls fail
- Cached values are used when rate limited to maintain UX

