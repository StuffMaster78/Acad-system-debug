# Vite Proxy Error Fix

## Problem
Vite proxy was experiencing `ECONNRESET` and `socket hang up` errors when polling endpoints:
- `/api/v1/auth/session-management/status/`
- `/api/v1/notifications_system/unread-count/`
- `/api/v1/users/users/update_online_status/`

## Root Causes
1. **Frequent Polling**: Frontend polling endpoints every 30 seconds
2. **No Timeout Configuration**: Vite proxy had no timeout settings
3. **No Error Handling**: Proxy errors weren't being handled gracefully
4. **Backend Load**: Endpoints weren't optimized for frequent polling

## Solutions Implemented

### 1. Vite Proxy Configuration (`frontend/vite.config.js`)
- Added 30-second timeout for requests
- Added proxy error handling
- Added request/response logging for debugging
- Enabled WebSocket proxying

### 2. Backend Endpoint Optimization

#### Session Status Endpoint (`authentication/views/session_management_viewset.py`)
- Added 5-second caching to reduce database load
- Added comprehensive error handling
- Returns safe defaults on errors (prevents 500s)

#### Unread Count Endpoint (`notifications_system/views/views_counters.py`)
- Added 10-second caching layer
- Improved error handling with graceful fallbacks
- Changed warning logs to debug logs for cache errors

#### Online Status Endpoint (`users/views/online_status.py`)
- Added 30-second cache to prevent excessive database writes
- Only updates DB if last update was > 30 seconds ago
- Added error handling

## Benefits
1. ✅ **Reduced Database Load**: Caching prevents excessive queries
2. ✅ **Better Error Handling**: Graceful degradation instead of 500 errors
3. ✅ **Improved Proxy Stability**: Timeout and error handling prevent connection resets
4. ✅ **Better Logging**: Debug logs help identify issues without cluttering production logs

## Testing
1. Monitor proxy logs for connection errors
2. Check that endpoints return cached responses when appropriate
3. Verify that errors don't cause 500 responses
4. Confirm polling continues to work despite occasional connection issues

## Next Steps (Optional)
1. Consider implementing exponential backoff in frontend polling
2. Add retry logic for failed requests
3. Consider using Server-Sent Events (SSE) instead of polling for real-time updates
4. Monitor cache hit rates to optimize cache durations

