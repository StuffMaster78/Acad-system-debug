# Order Messages - Usage Guide

## Quick Fix for OrderMessages.vue

If you have an `OrderMessages.vue` component, update it to use the new API:

### 1. Import the API functions:

```javascript
import { listThreads, startThreadForOrder } from '@/api/communications'
// OR use the composable:
import { useOrderMessages } from '@/composables/useOrderMessages'
```

### 2. Replace `listThreads` calls:

**OLD (causes 429 errors):**
```javascript
// ❌ Too frequent, no rate limiting
const response = await axios.get(`/api/v1/order-communications/communication-threads/?order=${orderId}`)
```

**NEW (with rate limiting):**
```javascript
// ✅ Rate limited, cached, handles errors
const response = await listThreads(orderId)
const threads = response.data.results || response.data || []
```

### 3. Add thread creation:

```javascript
// Start a new conversation
const createThread = async () => {
  try {
    const response = await startThreadForOrder(orderId)
    if (response.data.thread) {
      // Thread created successfully
      console.log('Thread created:', response.data.thread)
      // Reload threads
      await loadThreads()
    }
  } catch (error) {
    console.error('Failed to create thread:', error.message)
  }
}
```

### 4. Use the composable (Recommended):

```vue
<template>
  <div>
    <!-- Error message -->
    <div v-if="error" class="error">{{ error }}</div>
    
    <!-- Loading state -->
    <div v-if="loading">Loading messages...</div>
    
    <!-- No threads - show start button -->
    <div v-if="!loading && threads.length === 0">
      <button @click="handleStartConversation" :disabled="creatingThread" class="btn btn-primary">
        <span v-if="creatingThread">Creating...</span>
        <span v-else>Start Conversation</span>
      </button>
    </div>
    
    <!-- Threads list -->
    <div v-else>
      <div v-for="thread in threads" :key="thread.id" class="thread-item">
        <h3>Thread {{ thread.id }}</h3>
        <p>Unread: {{ thread.unread_count }}</p>
        <button @click="loadMessages(thread.id)">View Messages</button>
      </div>
    </div>
    
    <!-- Messages -->
    <div v-if="messages.length > 0">
      <div v-for="message in messages" :key="message.id">
        {{ message.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { useOrderMessages } from '@/composables/useOrderMessages'

export default {
  props: {
    orderId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const {
      threads,
      messages,
      unreadCount,
      loading,
      error,
      creatingThread,
      loadThreads,
      loadMessages,
      createThread,
      sendThreadMessage
    } = useOrderMessages(props.orderId)
    
    const handleStartConversation = async () => {
      try {
        await createThread()
        // Thread created, will automatically reload
      } catch (err) {
        // Error is already set in error ref
        console.error('Failed to start conversation:', err)
      }
    }
    
    return {
      threads,
      messages,
      unreadCount,
      loading,
      error,
      creatingThread,
      loadThreads,
      loadMessages,
      createThread,
      sendThreadMessage,
      handleStartConversation
    }
  }
}
</script>
```

## API Functions Available

### `/frontend/src/api/communications.js`

1. **`listThreads(orderId, options)`** - List threads with rate limiting
2. **`startThreadForOrder(orderId)`** - Create a new thread
3. **`getThreadMessages(threadId, options)`** - Get messages in a thread
4. **`sendMessage(threadId, message, options)`** - Send a message
5. **`markThreadAsRead(threadId)`** - Mark thread as read
6. **`clearThreadsCache()`** - Clear cached threads

## Rate Limiting Features

- ✅ **5-second cache** for thread lists
- ✅ **Automatic retry** on 429 errors
- ✅ **Cached responses** returned when rate limited
- ✅ **Throttled requests** (max once per 5 seconds)
- ✅ **30-second auto-refresh** instead of constant polling

## Error Handling

All functions handle:
- **401 Unauthorized** - Returns user-friendly error
- **403 Forbidden** - Returns permission error
- **429 Too Many Requests** - Uses cache, retries after delay
- **Network errors** - Returns safe defaults

## Testing

After updating your component:
1. Check browser console - should see fewer errors
2. Check Network tab - should see fewer requests
3. Try creating a thread - should work without 429 errors
4. Messages should load correctly with rate limiting

