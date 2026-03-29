# Frontend Integration Guide

> **✅ YES! This backend is fully API-based and designed for decoupled frontend consumption.**

## API Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

All API endpoints are prefixed with `/api/v1/`

## 🎯 Quick Start for Frontend Developers

1. **Interactive API Docs**: Visit `http://localhost:8000/api/v1/docs/swagger/`
2. **Full API Documentation**: See `COMPLETE_API_DOCUMENTATION.md`
3. **Authentication**: JWT Bearer tokens (see below)
4. **Schema Download**: `http://localhost:8000/api/v1/schema/` (generate TypeScript clients)

## Authentication

### JWT Authentication

```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'client@example.com',
    password: 'password123'
  })
});

const data = await response.json();
const accessToken = data.access;  // or data.token depending on endpoint
const refreshToken = data.refresh;

// Use token in subsequent requests
const apiCall = await fetch('http://localhost:8000/api/v1/orders/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

### Token Refresh
```javascript
const refreshResponse = await fetch('http://localhost:8000/api/v1/auth/token/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: refreshToken })
});
```

## API Documentation

### Swagger UI
- **URL**: `http://localhost:8000/api/v1/docs/swagger/`
- **Features**: Interactive API explorer, try endpoints directly
- **Authentication**: Click "Authorize" button, enter `Bearer <token>`

### ReDoc
- **URL**: `http://localhost:8000/api/v1/docs/redoc/`
- **Features**: Clean, readable documentation

## Key API Endpoints

### Authentication
```
POST   /api/v1/auth/login/           # Login
POST   /api/v1/auth/register/        # Register
POST   /api/v1/auth/token/refresh/   # Refresh token
POST   /api/v1/auth/logout/          # Logout
POST   /api/v1/auth/password/reset/  # Password reset
```

### User Management
```
GET    /api/v1/users/profile/              # Get own profile
PUT    /api/v1/users/profile/              # Update profile
GET    /api/v1/users/{id}/                 # Get user (if permitted)
POST   /api/v1/users/{id}/impersonate/     # Impersonate user (admin/superadmin)
DELETE /api/v1/users/{id}/impersonate/     # Stop impersonation (admin/superadmin)
```

### Orders
```
GET    /api/v1/orders/                     # List orders
POST   /api/v1/orders/                     # Create order
GET    /api/v1/orders/{id}/                # Get order
PUT    /api/v1/orders/{id}/                # Update order
POST   /api/v1/orders/{id}/pay/            # Pay for order
```

### Payments
```
GET    /api/v1/order-payments/             # List payments
POST   /api/v1/order-payments/initiate/    # Initiate payment
GET    /api/v1/order-payments/by_type/     # Filter by payment type
  ?payment_type=standard
  &order_id=123
  &special_order_id=456
  &class_purchase_id=789
  &installment_id=101
```

### Loyalty & Redemption
```
GET    /api/v1/loyalty-management/redemption-items/        # Browse redemption items
POST   /api/v1/loyalty-management/redemption-requests/     # Create redemption request
GET    /api/v1/loyalty-management/redemption-requests/     # View redemption history
GET    /api/v1/loyalty-management/analytics/               # Analytics (admin)
GET    /api/v1/loyalty-management/analytics/points_trend/  # Points trend
GET    /api/v1/loyalty-management/analytics/top_redemptions/ # Top items
```

### Class Management
```
GET    /api/v1/class-management/bundles/                   # List class bundles
POST   /api/v1/class-management/bundles/create_manual/     # Admin create bundle
POST   /api/v1/class-management/bundles/{id}/pay_deposit/  # Pay deposit
POST   /api/v1/class-management/bundles/{id}/configure_installments/ # Setup installments
```

### Files
```
POST   /api/v1/order-files/                  # Upload file
GET    /api/v1/order-files/{id}/download/    # Download file (signed URL)
```

## Response Formats

### Success Response
```json
{
  "id": 123,
  "status": "completed",
  "data": { ... }
}
```

### Error Response
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "field_errors": {
    "field_name": ["Error for this field"]
  }
}
```

### Pagination
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/orders/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

## Impersonation Flow

### Admin Impersonates Client
```javascript
// 1. Admin creates impersonation token (optional, or use direct endpoint)
const tokenResponse = await fetch('/api/v1/auth/impersonate/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    target_user_id: 456
  })
});

// 2. Or use direct impersonate endpoint
const impersonateResponse = await fetch('/api/v1/users/456/impersonate/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  }
});

// 3. Session now acts as target user
// All subsequent requests use target user's permissions

// 4. Stop impersonation
await fetch('/api/v1/users/456/stop_impersonation/', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${adminToken}` }
});
```

**Note**: Impersonation is already implemented. Admins/superadmins can:
- Use `/api/v1/users/{id}/impersonate/` to start
- Use `/api/v1/users/{id}/stop_impersonation/` to end
- Session automatically tracks impersonator

## Error Handling

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Structure
```json
{
  "detail": "Error message here",
  "code": "ERROR_CODE",
  "field_errors": {
    "field1": ["Error 1", "Error 2"]
  }
}
```

### Example Error Handling
```javascript
try {
  const response = await fetch('/api/v1/orders/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    if (response.status === 400) {
      // Validation errors
      Object.keys(error.field_errors || {}).forEach(field => {
        console.error(`${field}: ${error.field_errors[field].join(', ')}`);
      });
    } else if (response.status === 401) {
      // Token expired, refresh
      await refreshToken();
      // Retry request
    } else {
      console.error(error.detail);
    }
    throw new Error(error.detail || 'Request failed');
  }
  
  const data = await response.json();
  return data;
} catch (error) {
  console.error('API Error:', error);
  throw error;
}
```

## Rate Limiting

API requests are rate-limited. Check response headers:

```javascript
const response = await fetch('/api/v1/orders/');
const remaining = response.headers.get('X-RateLimit-Remaining');
const reset = response.headers.get('X-RateLimit-Reset');

if (remaining === '0') {
  // Rate limit reached, wait until reset time
  const waitTime = new Date(reset * 1000) - Date.now();
  await new Promise(resolve => setTimeout(resolve, waitTime));
}
```

## Multi-Tenant Support

The system is multi-tenant. Website context is determined from:
1. Request headers (if configured)
2. User's associated website
3. Query parameters

## File Uploads

### Upload File
```javascript
const formData = new FormData();
formData.append('file', fileObject);
formData.append('order', orderId);
formData.append('category', categoryId);

const response = await fetch('/api/v1/order-files/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
    // Don't set Content-Type for FormData
  },
  body: formData
});
```

### Download File (Signed URL)
```javascript
const response = await fetch('/api/v1/order-files/123/download/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const data = await response.json();
// data.url contains signed URL (valid for limited time)
window.open(data.url);
```

## WebSocket/SSE (Real-time)

For real-time notifications (if implemented):
```javascript
const eventSource = new EventSource('/api/v1/notifications/stream/?token=' + token);

eventSource.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  // Handle notification
};
```

## Best Practices

### 1. Token Management
- Store tokens securely (httpOnly cookies or secure storage)
- Refresh tokens before expiry
- Handle token expiration gracefully

### 2. Request Interceptors
```javascript
// Axios example
axios.interceptors.request.use(config => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Token expired, refresh and retry
      await refreshToken();
      return axios.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

### 3. Error Boundaries
Wrap API calls in error boundaries to handle failures gracefully.

### 4. Loading States
Show loading indicators during API calls.

### 5. Optimistic Updates
Update UI optimistically, revert on error.

### 6. Caching
Cache frequently accessed data (user profile, orders list).

### 7. Pagination
Always handle paginated responses for list endpoints.

## Example Frontend Integration (React)

```javascript
// hooks/useApi.js
import { useState, useEffect } from 'react';

export function useApi(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    
    fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    })
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, [url]);
  
  return { data, loading, error };
}

// Usage
function OrdersList() {
  const { data, loading, error } = useApi('/api/v1/orders/');
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {data.results.map(order => (
        <OrderCard key={order.id} order={order} />
      ))}
    </div>
  );
}
```

## TypeScript Types (Example)

```typescript
interface Order {
  id: number;
  client: number;
  topic: string;
  description: string;
  total_cost: number;
  status: 'pending' | 'in_progress' | 'completed';
  created_at: string;
}

interface Payment {
  id: number;
  order?: number;
  payment_type: 'standard' | 'special_installment' | 'class_payment' | 'wallet_loading';
  amount: string;
  status: 'pending' | 'completed' | 'failed';
  transaction_id: string;
}

interface RedemptionItem {
  id: number;
  name: string;
  category_name: string;
  points_required: number;
  redemption_type: 'discount' | 'cash' | 'product' | 'service' | 'voucher';
  is_available: boolean;
  can_redeem?: {
    can_redeem: boolean;
    message: string;
  };
}
```

## Testing Endpoints

### Using Swagger UI
1. Navigate to `http://localhost:8000/api/v1/docs/swagger/`
2. Click "Authorize" button
3. Enter: `Bearer <your-token>`
4. Click "Try it out" on any endpoint
5. Fill in parameters and execute

### Using cURL
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"client@test.com","password":"password"}'

# Get orders (use token from login)
curl -X GET http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Patterns

### Pagination
```javascript
async function fetchAllOrders() {
  let url = '/api/v1/orders/';
  let allOrders = [];
  
  while (url) {
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    allOrders = [...allOrders, ...data.results];
    url = data.next;
  }
  
  return allOrders;
}
```

### File Upload with Progress
```javascript
function uploadFile(file, onProgress) {
  const formData = new FormData();
  formData.append('file', file);
  
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        onProgress(percentComplete);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 201) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error('Upload failed'));
      }
    });
    
    xhr.open('POST', '/api/v1/order-files/');
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(formData);
  });
}
```

## Environment Configuration

### Development
```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### Production
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.yourdomain.com/api/v1';
```

## Security Considerations

1. **Never store tokens in localStorage** (XSS risk) - use httpOnly cookies or secure storage
2. **Always use HTTPS** in production
3. **Validate all user input** on frontend before sending
4. **Sanitize display data** to prevent XSS
5. **Handle errors gracefully** without exposing sensitive info
6. **Rate limit** client-side requests
7. **Token expiration** - implement automatic refresh

## Support

- **API Documentation**: `http://localhost:8000/api/v1/docs/swagger/`
- **Schema**: `http://localhost:8000/api/v1/schema/`
- **Error Codes**: Check response `detail` field for specific error messages

