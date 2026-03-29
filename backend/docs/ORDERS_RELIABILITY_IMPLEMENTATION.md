# Orders Reliability Implementation

This document describes the implementation of retry logic and reliability features to ensure orders are always loaded to the frontend, even in case of network issues or server errors.

## Overview

The system now includes:
1. **Exponential backoff retry logic** for API calls
2. **Connection status detection** and automatic retry on reconnect
3. **Composable for reliable order loading** with retry capabilities
4. **Enhanced error handling** with user-friendly feedback
5. **Visual indicators** for connection status and retry attempts

## Components

### 1. Retry Utility (`src/utils/retry.js`)

A comprehensive retry utility with exponential backoff:

- **`retryWithBackoff(fn, options)`**: Generic retry function with configurable options
- **`retryApiCall(apiCall, options)`**: Specialized for axios API calls
- **`createRetryableApiCall(apiCall, options)`**: Creates a retryable wrapper function
- **`isRetryableError(error)`**: Checks if an error should be retried

**Features:**
- Exponential backoff (configurable multiplier, max delay)
- Configurable retry conditions (default: network errors, 5xx, 429, 408)
- Retry callbacks for progress tracking
- Maximum retry limits to prevent infinite loops

### 2. Reliable Orders Composable (`src/composables/useReliableOrders.js`)

A Vue composable that provides reliable order loading:

**Exports:**
- `orders`: Reactive array of orders
- `loading`: Loading state
- `error`: Error state
- `retryCount`: Number of retries attempted
- `isRetrying`: Whether currently retrying
- `shouldShowRetry`: Computed property for UI
- `retryStatus`: Status message for retries
- `loadOrders(params, options)`: Load orders with retry
- `retry()`: Manually retry loading
- `refresh()`: Refresh orders

**Usage:**
```javascript
import { useReliableOrders } from '@/composables/useReliableOrders'

const { orders, loading, error, loadOrders, retry } = useReliableOrders()

// Load orders with automatic retry
await loadOrders({ status: 'available' }, { maxRetries: 3 })
```

### 3. Connection Status Composable (`src/composables/useConnectionStatus.js`)

Monitors network connection status and triggers events on reconnect:

**Exports:**
- `isOnline`: Reactive boolean for online status
- `wasOffline`: Whether connection was recently restored

**Features:**
- Listens to browser `online`/`offline` events
- Periodic connection checks (every 5 seconds)
- Dispatches `connection-restored` custom event when connection is restored
- Automatic cleanup on component unmount

### 4. Enhanced Dashboard (`src/views/dashboard/Dashboard.vue`)

The dashboard now includes:

**Retry Logic:**
- `fetchRecentOrders()`: Uses `retryApiCall` with 3 retries
- `fetchWriterDashboard()`: Uses `retryApiCall` for profile and orders
- All order-related API calls now have retry logic

**Connection Monitoring:**
- Visual offline indicator in header
- Automatic dashboard refresh when connection is restored
- Connection status composable integration

**Error Handling:**
- Graceful degradation (empty arrays instead of errors)
- User-friendly error messages
- Silent handling for expected errors (404, 500)

## Retry Strategy

### When to Retry

The system retries on:
- **Network errors** (no response from server)
- **5xx server errors** (500, 502, 503, etc.)
- **429 Too Many Requests** (rate limiting)
- **408 Request Timeout**

### Retry Configuration

Default settings:
- **Max retries**: 3
- **Initial delay**: 1000ms (1 second)
- **Max delay**: 10000ms (10 seconds)
- **Multiplier**: 2 (exponential backoff)

Retry delays:
- 1st retry: 1 second
- 2nd retry: 2 seconds
- 3rd retry: 4 seconds
- 4th retry: 8 seconds (capped at max delay)

### Custom Retry Logic

You can customize retry behavior:

```javascript
await retryApiCall(
  () => ordersAPI.list(params),
  {
    maxRetries: 5,
    initialDelay: 500,
    maxDelay: 5000,
    multiplier: 1.5,
    shouldRetry: (error) => {
      // Custom retry logic
      return error.response?.status === 503
    },
    onRetry: (attempt, maxRetries, delay, error) => {
      console.log(`Retry ${attempt}/${maxRetries} in ${delay}ms`)
    }
  }
)
```

## User Experience

### Visual Feedback

1. **Offline Indicator**: Red badge in dashboard header when offline
2. **Retry Progress**: Toast notifications during retry attempts
3. **Success Messages**: Confirmation when orders load after retries
4. **Error Messages**: Clear error messages if all retries fail

### Automatic Recovery

- **Connection Restoration**: Dashboard automatically refreshes when connection is restored
- **Silent Retries**: Retries happen automatically without user intervention
- **Graceful Degradation**: Empty state shown instead of error screens

## Backend Considerations

The backend (`orders/views/orders/base.py`) already includes:

1. **Error Handling**: `list()` method wrapped in try-except, returns empty paginated response on error
2. **Query Optimization**: Uses `select_related` and `prefetch_related` to prevent N+1 queries
3. **Pagination**: Limited pagination (max 500 items) to prevent performance issues

## Best Practices

1. **Use retry logic for critical data**: Orders, user profiles, dashboard stats
2. **Don't retry on 4xx errors**: These are client errors, not server issues
3. **Show user feedback**: Let users know when retries are happening
4. **Set reasonable limits**: Don't retry indefinitely
5. **Handle offline state**: Show appropriate UI when offline

## Testing

To test the retry logic:

1. **Network throttling**: Use browser DevTools to throttle network
2. **Server errors**: Temporarily cause 500 errors in backend
3. **Offline mode**: Toggle offline mode in browser
4. **Connection restoration**: Go offline, then come back online

## Future Enhancements

Potential improvements:
1. **Request queuing**: Queue failed requests and retry when online
2. **Service Worker**: Cache orders for offline access
3. **Optimistic updates**: Show cached data while fetching fresh data
4. **Retry analytics**: Track retry success rates
5. **Configurable retry policies**: Per-endpoint retry configuration

