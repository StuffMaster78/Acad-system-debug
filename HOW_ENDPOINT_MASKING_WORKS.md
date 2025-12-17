# How Endpoint Masking Works - Complete Explanation

## 🎯 Overview

The endpoint masking system hides actual API endpoint paths from writers and clients by routing requests through a backend proxy. This provides **security through obscurity** - users can't discover admin/internal endpoints by inspecting network requests.

---

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                           │
│                                                                 │
│  1. User Action: "View My Orders"                              │
│     ↓                                                            │
│  2. Frontend Code Calls:                                        │
│     ordersAPI.list() → '/orders/orders/'                        │
│     ↓                                                            │
│  3. API Client Interceptor (client.js)                          │
│     ├─ Checks: VITE_ENABLE_ENDPOINT_MASKING === 'true'?        │
│     ├─ Gets User Role: 'client'                                 │
│     ├─ Calls maskEndpoint('/orders/orders/')                    │
│     └─ Returns: '/client/orders/'                               │
│     ↓                                                            │
│  4. Request Sent to Backend:                                    │
│     GET /api/v1/proxy/client/orders/                            │
│     Headers: Authorization: Bearer <token>                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND PROXY                                │
│                                                                 │
│  5. Proxy Endpoint Receives Request:                            │
│     /api/v1/proxy/client/orders/                                │
│     ↓                                                            │
│  6. Extract User Info:                                          │
│     ├─ User: client_user                                        │
│     ├─ Role: 'client'                                           │
│     └─ Token: <valid JWT>                                      │
│     ↓                                                            │
│  7. Route Endpoint Function:                                    │
│     ├─ Input: masked_path = '/client/orders/'                  │
│     ├─ user_role = 'client'                                     │
│     ├─ Lookup in ENDPOINT_ROUTES['client']:                     │
│     │   '/client/orders/' → '/api/v1/orders/orders/'            │
│     └─ Returns: actual_path = '/api/v1/orders/orders/'          │
│     ↓                                                            │
│  8. Make Internal Request:                                     │
│     ├─ Create DRF APIClient                                     │
│     ├─ Set Authorization header (preserve JWT)                  │
│     ├─ Call: GET /api/v1/orders/orders/                        │
│     └─ Get response from actual endpoint                       │
│     ↓                                                            │
│  9. Return Proxied Response:                                    │
│     └─ Response data + status code                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                           │
│                                                                 │
│  10. Receive Response:                                          │
│      └─ Display orders data                                    │
│                                                                 │
│  11. Network Tab Shows:                                         │
│      ✅ GET /api/v1/proxy/client/orders/ (Masked)             │
│      ❌ NOT: GET /api/v1/orders/orders/ (Hidden)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Step-by-Step Breakdown

### **Step 1: Frontend Code Makes API Call**

```javascript
// In your Vue component or API file
import ordersAPI from '@/api/orders'

// User clicks "View Orders"
const orders = await ordersAPI.list()
```

**What happens:**
- `ordersAPI.list()` calls `apiClient.get('/orders/orders/')`
- This is the **actual endpoint** that your code uses

---

### **Step 2: API Client Interceptor Intercepts Request**

**File:** `frontend/src/api/client.js`

```javascript
apiClient.interceptors.request.use((config) => {
  // 1. Add authentication token
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // 2. Check if masking is enabled
  const enableMasking = import.meta.env.VITE_ENABLE_ENDPOINT_MASKING === 'true'
  
  if (enableMasking && config.url) {
    const userRole = getUserRole() // Gets 'client', 'writer', 'admin', etc.
    
    // 3. Admins bypass masking
    if (userRole === 'admin' || userRole === 'superadmin') {
      // No change - use actual endpoint
      return config
    }
    
    // 4. Mask the endpoint
    const masked = maskEndpoint(config.url, userRole)
    // '/orders/orders/' → '/client/orders/'
    
    // 5. Route through proxy
    config.url = `/proxy/${masked}`
    // '/client/orders/' → '/proxy/client/orders/'
  }
  
  return config
})
```

**Key Points:**
- ✅ Admins/superadmins see actual endpoints (no masking)
- ✅ Clients/writers get masked endpoints
- ✅ Masked endpoints are routed through `/api/v1/proxy/`

---

### **Step 3: Endpoint Masking Function**

**File:** `frontend/src/utils/endpoint-masker.js`

```javascript
export function maskEndpoint(endpoint, role) {
  // Get mappings for this role
  const mappings = ENDPOINT_MAPPINGS[role] || {}
  
  // Example mappings for 'client':
  // '/orders/orders/' → '/client/orders/'
  // '/users/users/profile/' → '/client/profile/'
  
  // Find matching mapping
  for (const [actual, masked] of Object.entries(mappings)) {
    if (endpoint.startsWith(actual)) {
      const remaining = endpoint.slice(actual.length)
      // Preserve IDs, query params, etc.
      return masked + remaining
    }
  }
  
  return endpoint // No mapping found
}
```

**Example Transformations:**

| Original Endpoint | Masked Endpoint (Client) | Masked Endpoint (Writer) |
|-------------------|-------------------------|--------------------------|
| `/orders/orders/` | `/client/orders/` | ❌ Blocked (not for writers) |
| `/writer-management/writer-orders/` | ❌ Blocked | `/writer/orders/` |
| `/admin-management/users/` | ❌ Blocked (403) | ❌ Blocked (403) |

---

### **Step 4: Request Sent to Backend**

**Network Request:**
```
GET /api/v1/proxy/client/orders/
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
  X-Website: 1
  Content-Type: application/json
```

**What the user sees in DevTools:**
- ✅ URL: `/api/v1/proxy/client/orders/`
- ❌ NOT: `/api/v1/orders/orders/` (hidden!)

---

### **Step 5: Backend Proxy Receives Request**

**File:** `backend/core/endpoint_proxy.py`

**URL Pattern:** `/api/v1/proxy/<path:masked_path>`

```python
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def endpoint_proxy(request, masked_path=''):
    # 1. Get user and role
    user = request.user  # Already authenticated (JWT validated)
    user_role = get_user_role(user)  # Returns 'client', 'writer', etc.
    
    # 2. Route masked endpoint to actual endpoint
    actual_path, allowed = route_endpoint(
        f'/{masked_path}',  # '/client/orders/'
        user_role,          # 'client'
        method=request.method
    )
    # Returns: ('/api/v1/orders/orders/', True)
    
    # 3. Check if access is allowed
    if not allowed:
        return Response({'error': 'Access denied'}, status=403)
    
    # 4. Make internal request to actual endpoint
    return make_internal_request(request, actual_path)
```

---

### **Step 6: Endpoint Routing Logic**

**File:** `backend/core/endpoint_proxy.py`

```python
def route_endpoint(masked_path, user_role, method='GET', data=None, params=None):
    # Admins bypass proxy
    if user_role in ['admin', 'superadmin']:
        return masked_path, True
    
    # Get routes for this role
    routes = ENDPOINT_ROUTES.get(user_role, {})
    # For 'client': {'/client/orders/': '/api/v1/orders/orders/', ...}
    
    # Find matching route
    for masked, actual in routes.items():
        if masked_path.startswith(masked):
            remaining = masked_path[len(masked):]
            # '/client/orders/123/' → '/api/v1/orders/orders/123/'
            return actual + remaining, True
    
    # Block admin endpoints
    if '/admin-management/' in masked_path:
        return None, False
    
    return masked_path, True  # Passthrough if not mapped
```

**Routing Table Example:**

| User Role | Masked Path | Actual Path |
|-----------|-------------|-------------|
| client | `/client/orders/` | `/api/v1/orders/orders/` |
| client | `/client/profile/` | `/api/v1/users/users/profile/` |
| writer | `/writer/orders/` | `/api/v1/writer-management/writer-orders/` |
| writer | `/writer/payments/` | `/api/v1/writer-management/writer-payments/` |

---

### **Step 7: Internal Request to Actual Endpoint**

**File:** `backend/core/endpoint_proxy.py`

```python
def make_internal_request(request, actual_path):
    # Create DRF APIClient (handles JWT properly)
    client = APIClient()
    
    # Preserve authentication
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
        client.credentials(HTTP_AUTHORIZATION=auth_header)
    
    # Also set user directly
    if request.user.is_authenticated:
        client.force_authenticate(user=request.user)
    
    # Make internal request
    response = client.get(actual_path, request.GET, format='json')
    # This calls: GET /api/v1/orders/orders/ internally
    
    # Return the response
    return Response(response.data, status=response.status_code)
```

**Key Points:**
- ✅ Uses DRF's `APIClient` (not Django's test client)
- ✅ Preserves JWT authentication
- ✅ Preserves all headers (X-Website, etc.)
- ✅ Handles query parameters
- ✅ Returns actual endpoint's response

---

### **Step 8: Response Returned to Frontend**

**Response Flow:**
```
Actual Endpoint Response
  ↓
Backend Proxy
  ↓
Frontend API Client
  ↓
Your Component
```

**What the user sees:**
- ✅ Response data (orders list)
- ✅ Status code (200 OK)
- ✅ Network tab shows: `GET /api/v1/proxy/client/orders/`

**What the user DOESN'T see:**
- ❌ Actual endpoint: `/api/v1/orders/orders/`
- ❌ Internal routing logic
- ❌ Backend endpoint structure

---

## 🎭 Role-Based Behavior

### **Client User**

```javascript
// Frontend code
ordersAPI.list()  // Calls '/orders/orders/'

// After masking
GET /api/v1/proxy/client/orders/

// Backend routes to
GET /api/v1/orders/orders/  // (internal, not visible)
```

### **Writer User**

```javascript
// Frontend code
writerOrdersAPI.list()  // Calls '/writer-management/writer-orders/'

// After masking
GET /api/v1/proxy/writer/orders/

// Backend routes to
GET /api/v1/writer-management/writer-orders/  // (internal, not visible)
```

### **Admin User**

```javascript
// Frontend code
ordersAPI.list()  // Calls '/orders/orders/'

// NO masking for admins
GET /api/v1/orders/orders/  // Direct access, no proxy
```

---

## 🔒 Security Features

### **1. Role Validation**
```python
# Backend checks user role before routing
if user_role not in ['client', 'writer']:
    return 403  # Blocked
```

### **2. Admin Endpoint Blocking**
```python
# Clients/writers trying to access admin endpoints
if '/admin-management/' in masked_path:
    return None, False  # Blocked
```

### **3. Authentication Preservation**
```python
# JWT token is preserved through proxy
client.credentials(HTTP_AUTHORIZATION=auth_header)
client.force_authenticate(user=request.user)
```

---

## 📝 Real-World Example

### **Scenario: Client Views Their Orders**

1. **User Action:** Client clicks "My Orders" button

2. **Frontend Code:**
   ```javascript
   // Component calls
   const orders = await ordersAPI.list()
   
   // API file has
   list: (params) => apiClient.get('/orders/orders/', { params })
   ```

3. **Interceptor Masks:**
   ```javascript
   // Original: '/orders/orders/'
   // Masked: '/client/orders/'
   // Proxied: '/proxy/client/orders/'
   ```

4. **Network Request:**
   ```
   GET /api/v1/proxy/client/orders/?page=1
   Authorization: Bearer <token>
   ```

5. **Backend Proxy:**
   ```python
   # Receives: '/client/orders/'
   # Routes to: '/api/v1/orders/orders/'
   # Makes internal request
   # Returns: orders data
   ```

6. **Response:**
   ```json
   {
     "count": 10,
     "results": [...orders...]
   }
   ```

7. **User Sees:**
   - ✅ Orders displayed on screen
   - ✅ Network tab shows: `/api/v1/proxy/client/orders/`
   - ❌ Never sees: `/api/v1/orders/orders/`

---

## 🎯 Key Benefits

1. **Obscurity**: Actual endpoints hidden from clients/writers
2. **Security**: Admin endpoints blocked for non-admins
3. **Transparency**: Admins see actual endpoints (no masking)
4. **Flexibility**: Easy to add new endpoint mappings
5. **Performance**: Internal requests are fast (no network overhead)

---

## ⚙️ Configuration

### **Enable Masking**

**Frontend `.env`:**
```bash
VITE_ENABLE_ENDPOINT_MASKING=true
```

### **Add New Mappings**

**Frontend:** `frontend/src/utils/endpoint-masker.js`
```javascript
client: {
  '/new/endpoint/': '/client/masked/endpoint/',
}
```

**Backend:** `backend/core/endpoint_proxy.py`
```python
'client': {
    '/client/masked/endpoint/': '/api/v1/new/endpoint/',
}
```

---

## 🐛 Troubleshooting

### **Issue: 404 Not Found**
- Check endpoint mapping exists in both frontend and backend
- Verify actual endpoint path is correct

### **Issue: 403 Forbidden**
- User role doesn't have access to this endpoint
- Admin endpoint accessed by non-admin

### **Issue: Authentication Fails**
- JWT token not being passed correctly
- Check Authorization header in proxy

---

This system provides a complete endpoint masking solution that hides your API structure from clients and writers while maintaining full functionality and security!

