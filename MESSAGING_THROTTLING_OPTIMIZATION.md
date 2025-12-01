# Messaging Throttling Optimization

**Date**: December 2025  
**Status**: ✅ **Complete**

---

## 🎯 Overview

Optimized the messaging system to reduce throttling issues by implementing shared caching, request deduplication, increased backend limits, and coordinated refresh intervals.

---

## ✅ Changes Made

### 1. ✅ Increased Backend Throttle Limits

**Location**: `backend/communications/throttles.py` and `backend/communications/views.py`

**Changes**:
- `CommunicationMessageThrottle`: **20/minute → 60/minute** (3x increase)
- `CommunicationThreadThrottle`: **15/minute → 60/minute** (4x increase)
- `MessageThrottle`: **10/min → 30/min** (3x increase)
- `OrderMessageThrottle`: **20/minute → 60/minute** (3x increase)

**Rationale**:
- Messaging is a core feature that users interact with frequently
- 20/minute is too restrictive for active conversations
- 60/minute allows for natural conversation flow without hitting limits

---

### 2. ✅ Created Shared Messages Store

**Location**: `frontend/src/stores/messages.js`

**Features**:
- **Centralized Cache**: Single source of truth for threads and messages
- **Request Deduplication**: Prevents multiple simultaneous requests for same data
- **Smart Caching**: 10-second cache for threads, 5-second cache for messages
- **Error Handling**: Returns cached data on errors when available
- **Coordinated Refreshes**: Single refresh interval shared across components

**Benefits**:
- Eliminates duplicate API calls
- Reduces server load
- Prevents throttling from multiple components
- Faster response times (uses cache)

---

### 3. ✅ Updated Components to Use Shared Store

**Updated Components**:
- `useOrderMessages.js` - Uses shared cache
- `Messages.vue` - Uses shared cache and refresh
- `OrderMessagesTabbed.vue` - Uses shared cache and refresh
- `ThreadViewModal.vue` - Uses shared cache

**Changes**:
- Removed individual throttling functions
- Use shared `getThreads()` and `getThreadMessages()` functions
- Coordinated refresh intervals (only one active)
- Cache invalidation on updates

---

### 4. ✅ Optimized Refresh Intervals

**Before**:
- Multiple components each with 30-second intervals
- 5-second throttle for threads
- 3-second throttle for messages
- No coordination between components

**After**:
- Single shared refresh interval (30 seconds)
- 10-second cache for threads
- 5-second cache for messages
- Coordinated across all components
- Thread view modal: 10 seconds (increased from 5)

---

## 📊 Performance Improvements

### Request Reduction

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| **3 components open** | 9 requests/30s | 1 request/30s | **89% reduction** |
| **Thread + Messages** | 2 requests/3s | 1 request/5s | **70% reduction** |
| **Multiple tabs** | 3 requests/5s | 1 request/10s | **83% reduction** |

### Throttle Limit Increases

| Endpoint | Before | After | Increase |
|----------|--------|-------|----------|
| Messages | 20/min | 60/min | **3x** |
| Threads | 15/min | 60/min | **4x** |
| General Messages | 10/min | 30/min | **3x** |

---

## 🔧 Technical Implementation

### Shared Cache Structure

```javascript
// Threads cache
{
  data: [],
  lastFetch: timestamp,
  fetching: boolean,
  cacheTime: 10000ms
}

// Messages cache (per thread)
{
  data: { threadId: [] },
  lastFetch: { threadId: timestamp },
  fetching: { threadId: boolean },
  cacheTime: 5000ms
}
```

### Request Deduplication

```javascript
// If request is in progress, wait for it instead of making new request
if (threadsCache.fetching) {
  return new Promise((resolve) => {
    // Wait for ongoing request
  })
}
```

### Coordinated Refresh

```javascript
// Only one refresh interval active at a time
startSharedRefresh(callback, 30000)
// Automatically stops previous interval
```

---

## 🎯 Benefits

### For Users
- ✅ **No More Throttling Errors**: Higher limits prevent 429 errors
- ✅ **Faster Loading**: Cache provides instant responses
- ✅ **Smoother Experience**: Coordinated refreshes prevent conflicts
- ✅ **Better Performance**: Fewer API calls = faster app

### For System
- ✅ **Reduced Server Load**: 70-89% fewer requests
- ✅ **Better Scalability**: Shared cache reduces database queries
- ✅ **Lower Costs**: Fewer API calls = lower infrastructure costs
- ✅ **Improved Reliability**: Cache provides fallback on errors

---

## 📝 Usage

### Using the Shared Store

```javascript
import messagesStore from '@/stores/messages'

// Get threads (uses cache)
const threads = await messagesStore.getThreads()

// Force refresh
const threads = await messagesStore.getThreads(true)

// Get messages for thread
const messages = await messagesStore.getThreadMessages(threadId)

// Invalidate cache
messagesStore.invalidateThreadsCache()
messagesStore.invalidateThreadMessagesCache(threadId)

// Start shared refresh
const intervalId = messagesStore.startSharedRefresh(() => {
  // Refresh callback
}, 30000)
```

---

## 🚀 Future Improvements

### Potential Enhancements

1. **SSE Integration** (Recommended)
   - Use Server-Sent Events for real-time updates
   - Eliminate polling entirely
   - Push updates from server to client
   - Already implemented for notifications

2. **WebSocket Support** (Optional)
   - For bidirectional real-time communication
   - More complex but provides instant updates
   - Only needed if real-time typing indicators are critical

3. **Optimistic Updates**
   - Update UI immediately on send
   - Sync with server in background
   - Better perceived performance

---

## ✅ Summary

The messaging system now has:

✅ **Higher Throttle Limits** - 3-4x increase for better UX  
✅ **Shared Cache** - Prevents duplicate requests  
✅ **Request Deduplication** - One request per data type  
✅ **Coordinated Refreshes** - Single interval across components  
✅ **Smart Caching** - 10s threads, 5s messages  
✅ **Error Resilience** - Returns cached data on errors  

**Throttling issues should be significantly reduced, and the messaging system should feel much more responsive!**

---

**Last Updated**: December 2025  
**Status**: ✅ **Complete and Ready for Use**

