# Frontend Setup Guide - Quick Start

## ✅ API Availability Confirmation

**YES, the backend provides a complete REST API for decoupled frontend consumption.**

- ✅ **200+ API endpoints** across all modules
- ✅ **JWT authentication** for secure access
- ✅ **Swagger/OpenAPI documentation** (interactive)
- ✅ **TypeScript-friendly** (can generate typed clients)
- ✅ **RESTful design** with consistent response formats
- ✅ **Pagination support** for all list endpoints
- ✅ **File upload/download** support
- ✅ **Real-time notifications** ready

---

## 🚀 Getting Started

### 1. Access API Documentation

#### Swagger UI (Interactive)
```
http://localhost:8000/api/v1/docs/swagger/
```
- Try endpoints directly in browser
- Authorize with JWT tokens
- See request/response examples

#### ReDoc (Readable)
```
http://localhost:8000/api/v1/docs/redoc/
```

#### OpenAPI Schema (JSON)
```
http://localhost:8000/api/v1/schema/
```
Use this to generate typed clients!

---

### 2. Authentication Setup

#### Login Endpoint
```javascript
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "client"
  },
  "expires_in": 3600
}
```

#### Use Token in Requests
```javascript
fetch('/api/v1/orders/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

---

### 3. Generate TypeScript Client (Recommended)

```bash
# Install OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Generate TypeScript client
openapi-generator-cli generate \
  -i http://localhost:8000/api/v1/schema/ \
  -g typescript-axios \
  -o ./src/api \
  --additional-properties=supportsES6=true

# Or use fetch-based client
openapi-generator-cli generate \
  -i http://localhost:8000/api/v1/schema/ \
  -g typescript-fetch \
  -o ./src/api
```

**Usage:**
```typescript
import { Configuration, OrdersApi } from './api';

const config = new Configuration({
  accessToken: localStorage.getItem('accessToken'),
  basePath: 'http://localhost:8000/api/v1'
});

const ordersApi = new OrdersApi(config);
const orders = await ordersApi.ordersList();
```

---

### 4. Manual API Client Setup

#### Axios Example
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token interceptor
api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const newToken = await refreshToken();
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return api.request(error.config);
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### Fetch Wrapper Example
```typescript
class ApiClient {
  private baseURL = '/api/v1';
  private accessToken: string | null = null;

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseURL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    this.accessToken = data.access_token;
    localStorage.setItem('accessToken', data.access_token);
    return data;
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const token = this.accessToken || localStorage.getItem('accessToken');
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers
      }
    });

    if (response.status === 401) {
      // Token expired, refresh
      await this.refreshToken();
      return this.request(endpoint, options);
    }

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    const response = await fetch(`${this.baseURL}/auth/refresh-token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    const data = await response.json();
    this.accessToken = data.access;
    localStorage.setItem('accessToken', data.access);
    return data.access;
  }
}

export const api = new ApiClient();
```

---

### 5. React Hook Example

```typescript
// hooks/useAuth.ts
import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      // Verify token by fetching user profile
      api.request('/users/profile/')
        .then(data => setUser(data))
        .catch(() => {
          localStorage.removeItem('accessToken');
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const data = await api.login(email, password);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    await api.request('/auth/logout/', { method: 'POST' });
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  return { user, loading, login, logout };
}
```

```typescript
// hooks/useOrders.ts
import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function useOrders(filters = {}) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(filters).toString();
    api.request(`/orders/?${params}`)
      .then(data => setOrders(data.results))
      .catch(setError)
      .finally(() => setLoading(false));
  }, [JSON.stringify(filters)]);

  return { orders, loading, error };
}
```

---

## 📦 Key API Endpoints Quick Reference

### Authentication
```
POST   /api/v1/auth/login/         Login
POST   /api/v1/auth/logout/        Logout
POST   /api/v1/auth/refresh-token/ Refresh token
```

### Orders
```
GET    /api/v1/orders/             List orders
POST   /api/v1/orders/             Create order
GET    /api/v1/orders/{id}/        Get order
PUT    /api/v1/orders/{id}/        Update order
POST   /api/v1/orders/{id}/submit/ Submit order
```

### Payments
```
GET    /api/v1/order-payments/     List payments
POST   /api/v1/order-payments/initiate/  Initiate payment
```

### Discounts
```
POST   /api/v1/discounts/validate/ Validate code
POST   /api/v1/discounts/apply/    Apply discount
GET    /api/v1/discounts/preview/  Preview discount
```

### Fines
```
GET    /api/v1/fines/api/fines/    List fines (writer)
POST   /api/v1/fines/api/fines/issue/  Issue fine (admin)
POST   /api/v1/fines/api/fines/{id}/dispute/  Dispute fine
```

### Files
```
POST   /api/v1/order-files/        Upload file
GET    /api/v1/order-files/{id}/download/  Download file
```

**See `COMPLETE_API_DOCUMENTATION.md` for full endpoint list.**

---

## 🔒 Security Best Practices

1. **Token Storage**
   - ❌ Don't use `localStorage` (XSS risk)
   - ✅ Use `httpOnly` cookies (if backend supports)
   - ✅ Use secure storage (React Native SecureStore, etc.)

2. **Token Refresh**
   - Automatically refresh before expiry
   - Handle refresh token expiration

3. **HTTPS Only**
   - Always use HTTPS in production
   - Never send tokens over HTTP

4. **Input Validation**
   - Validate on frontend before sending
   - Don't trust frontend validation alone

---

## 🎨 Example: Complete Order Flow

```typescript
// 1. Create order
const order = await api.request('/orders/', {
  method: 'POST',
  body: JSON.stringify({
    topic: 'Research Paper',
    description: '10-page paper on AI',
    deadline: '2024-01-15T10:00:00Z',
    // ... other fields
  })
});

// 2. Apply discount (optional)
const discountPreview = await api.request('/discounts/preview/', {
  method: 'POST',
  body: JSON.stringify({
    order_id: order.id,
    discount_code: 'NEWYEAR2024'
  })
});

// 3. Apply discount
await api.request('/discounts/apply/', {
  method: 'POST',
  body: JSON.stringify({
    order_id: order.id,
    discount_code: 'NEWYEAR2024'
  })
});

// 4. Initiate payment
const payment = await api.request('/order-payments/initiate/', {
  method: 'POST',
  body: JSON.stringify({
    order_id: order.id,
    payment_method: 'wallet'
  })
});

// 5. Upload files
const formData = new FormData();
formData.append('file', fileObject);
formData.append('order', order.id);

await api.request('/order-files/', {
  method: 'POST',
  body: formData
});
```

---

## 🐛 Debugging

### Enable CORS (if needed)
Backend should have CORS configured. If frontend is on different domain:
```python
# In Django settings.py (already configured)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "https://your-frontend-domain.com"
]
```

### Check API Response
```javascript
const response = await fetch('/api/v1/orders/');
console.log('Status:', response.status);
console.log('Headers:', Object.fromEntries(response.headers));
const data = await response.json();
console.log('Data:', data);
```

---

## 📚 Additional Resources

1. **Complete API Docs**: `COMPLETE_API_DOCUMENTATION.md`
2. **Frontend Integration Guide**: `FRONTEND_INTEGRATION_GUIDE.md`
3. **Swagger UI**: `http://localhost:8000/api/v1/docs/swagger/`
4. **OpenAPI Schema**: `http://localhost:8000/api/v1/schema/`

---

## ✨ Next Steps

1. ✅ Start backend: `docker-compose up` or `python manage.py runserver`
2. ✅ Visit Swagger UI: `http://localhost:8000/api/v1/docs/swagger/`
3. ✅ Generate TypeScript client from OpenAPI schema
4. ✅ Set up API client in your frontend
5. ✅ Test authentication flow
6. ✅ Start building!

**The backend is fully ready for frontend integration!** 🎉

