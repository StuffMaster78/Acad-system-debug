# Start Conversation Endpoint

**New endpoint for easily starting conversations for orders**

---

## 🎯 Overview

Added a simplified endpoint to start a conversation thread for an order. This makes it easy for the frontend "Start Conversation" button to work.

---

## 📍 Endpoint

**POST** `/api/v1/order-communications/communication-threads/start-for-order/`

### Request Body

```json
{
    "order_id": 123
}
```

### Response (Success - 201 Created)

```json
{
    "detail": "Conversation thread created successfully.",
    "thread": {
        "id": 456,
        "order": 123,
        "thread_type": "order",
        "participants": [1, 2],
        "is_active": true,
        "created_at": "2024-12-20T10:30:00Z",
        ...
    }
}
```

### Response (Thread Already Exists - 200 OK)

```json
{
    "detail": "Conversation thread already exists for this order.",
    "thread": {
        "id": 456,
        "order": 123,
        ...
    }
}
```

### Response (Error - 400 Bad Request)

```json
{
    "detail": "order_id is required."
}
```

### Response (Error - 404 Not Found)

```json
{
    "detail": "Order not found."
}
```

### Response (Error - 403 Forbidden)

```json
{
    "detail": "You do not have permission to start a conversation for this order."
}
```

---

## 🔐 Permissions

The endpoint automatically checks permissions:

- **Admins/Superadmins/Support**: Can start conversations for any order ✅
- **Clients**: Can start conversations for their own orders ✅
- **Writers**: Can start conversations for orders assigned to them ✅
- **Others**: Cannot start conversations ❌

---

## ✨ Features

1. **Automatic Participant Setup**
   - Automatically includes the current user
   - Automatically includes the order's client (if different from user)
   - Automatically includes the assigned writer (if different from user)

2. **Duplicate Prevention**
   - Checks if a thread already exists for the order
   - Returns existing thread if found (instead of creating duplicate)

3. **Permission Checking**
   - Validates user has permission to start conversation
   - Validates order exists and is accessible

4. **Error Handling**
   - Clear error messages for all failure cases
   - Proper HTTP status codes

---

## 💻 Frontend Usage Example

### Vue.js Example

```javascript
// In your OrderDetail.vue component
async startConversation() {
    try {
        const response = await this.$api.post(
            '/order-communications/communication-threads/start-for-order/',
            {
                order_id: this.order.id
            }
        );
        
        if (response.data.thread) {
            // Navigate to the conversation thread
            this.$router.push({
                name: 'OrderMessages',
                params: {
                    orderId: this.order.id,
                    threadId: response.data.thread.id
                }
            });
        }
    } catch (error) {
        if (error.response?.status === 403) {
            this.$toast.error('You do not have permission to start a conversation for this order.');
        } else if (error.response?.status === 404) {
            this.$toast.error('Order not found.');
        } else {
            this.$toast.error('Failed to start conversation. Please try again.');
        }
    }
}
```

### React Example

```javascript
const startConversation = async (orderId) => {
    try {
        const response = await api.post(
            '/order-communications/communication-threads/start-for-order/',
            { order_id: orderId }
        );
        
        if (response.data.thread) {
            // Navigate to conversation
            navigate(`/orders/${orderId}/messages/${response.data.thread.id}`);
        }
    } catch (error) {
        console.error('Failed to start conversation:', error);
        // Handle error
    }
};
```

---

## 🔄 Alternative: Check if Thread Exists First

You can also check if a thread exists before showing the "Start Conversation" button:

```javascript
// Check if thread exists
async checkThreadExists(orderId) {
    try {
        const response = await this.$api.get(
            `/order-communications/communication-threads/?order=${orderId}`
        );
        
        if (response.data.results && response.data.results.length > 0) {
            // Thread exists - show "View Conversation" button
            return response.data.results[0];
        } else {
            // No thread - show "Start Conversation" button
            return null;
        }
    } catch (error) {
        console.error('Error checking thread:', error);
        return null;
    }
}
```

---

## 📝 Implementation Details

**File:** `communications/views.py`  
**Method:** `CommunicationThreadViewSet.start_for_order()`  
**Service:** Uses `ThreadService.create_thread()` for thread creation

---

## ✅ Testing

Test the endpoint:

```bash
# Start conversation for order 123
curl -X POST http://localhost:8000/api/v1/order-communications/communication-threads/start-for-order/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 123}'
```

---

## 🎉 Benefits

1. **Simplified API** - Just pass `order_id`, everything else is automatic
2. **Better UX** - Frontend doesn't need to figure out participants
3. **Permission Safe** - Built-in permission checking
4. **Idempotent** - Returns existing thread if one already exists
5. **Error Handling** - Clear error messages for all cases

---

**Last Updated:** December 2024  
**Status:** ✅ Ready to use

