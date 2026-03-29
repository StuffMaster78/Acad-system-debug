# Complete API Documentation - Writing System Backend

## Overview

This backend is **fully API-based** and designed for decoupled frontend consumption. All endpoints follow REST principles, use JWT authentication, and include comprehensive OpenAPI/Swagger documentation.

**Base URL**: `/api/v1/`

---

## 🔐 Authentication & Authorization

### JWT Token-Based Authentication

All authenticated endpoints require a JWT Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/login/` | Login and get JWT tokens | No |
| POST | `/api/v1/auth/logout/` | Logout and invalidate session | Yes |
| POST | `/api/v1/auth/refresh-token/` | Refresh access token | No |
| POST | `/api/v1/auth/verify_2fa/` | Verify 2FA code | No |
| POST | `/api/v1/auth/account-unlock/` | Request account unlock | No |

### Login Request
```json
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

### Login Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "role": "client"
  },
  "session_id": "uuid-string",
  "expires_in": 3600
}
```

### Token Usage
```javascript
// All authenticated requests
fetch('/api/v1/orders/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

---

## 📚 Interactive API Documentation

### Swagger UI (Interactive)
**URL**: `http://localhost:8000/api/v1/docs/swagger/`
- Interactive API explorer
- Try endpoints directly
- Authorize with JWT tokens
- View request/response schemas

### ReDoc (Readable)
**URL**: `http://localhost:8000/api/v1/docs/redoc/`
- Clean, readable documentation
- Better for printing/sharing

### OpenAPI Schema (JSON/YAML)
**URL**: `http://localhost:8000/api/v1/schema/`
- Machine-readable schema
- Use with code generators (e.g., OpenAPI Generator)

---

## 🌐 Complete API Endpoints

### 1. Authentication (`/api/v1/auth/`)
```
POST   /api/v1/auth/login/                    # Login
POST   /api/v1/auth/logout/                   # Logout
POST   /api/v1/auth/refresh-token/            # Refresh token
POST   /api/v1/auth/verify_2fa/               # Verify 2FA
POST   /api/v1/auth/account-unlock/           # Request unlock
POST   /api/v1/auth/account-unlock/confirm/   # Confirm unlock

# Impersonation (Admin/Superadmin)
POST   /api/v1/auth/impersonate/              # Create impersonation token
POST   /api/v1/auth/impersonate/start/        # Start impersonation
POST   /api/v1/auth/impersonate/end/          # End impersonation
GET    /api/v1/auth/impersonate/status/       # Check impersonation status

# Session Management
GET    /api/v1/auth/user-sessions/            # List user sessions
DELETE /api/v1/auth/user-sessions/{id}/       # Revoke session
POST   /api/v1/auth/user-sessions/revoke-all/ # Revoke all sessions
```

### 2. Users (`/api/v1/users/`)
```
GET    /api/v1/users/                         # List users (admin)
POST   /api/v1/users/                         # Create user (admin)
GET    /api/v1/users/{id}/                    # Get user details
PUT    /api/v1/users/{id}/                    # Update user
DELETE /api/v1/users/{id}/                    # Delete user
GET    /api/v1/users/profile/                 # Get own profile
PUT    /api/v1/users/profile/                 # Update own profile
POST   /api/v1/users/{id}/impersonate/        # Impersonate user (admin)
DELETE /api/v1/users/{id}/impersonate/        # Stop impersonation

# Admin User Management
GET    /api/v1/users/admin/user-management/   # Admin user management
GET    /api/v1/users/admin/profile-requests/  # Profile update requests
```

### 3. Orders (`/api/v1/orders/`)
```
GET    /api/v1/orders/                        # List orders
POST   /api/v1/orders/                        # Create order
GET    /api/v1/orders/{id}/                   # Get order details
PUT    /api/v1/orders/{id}/                   # Update order
PATCH  /api/v1/orders/{id}/                   # Partial update
DELETE /api/v1/orders/{id}/                   # Delete order

# Order Actions
POST   /api/v1/orders/{id}/submit/            # Submit order (writer)
POST   /api/v1/orders/{id}/assign/            # Assign writer (admin)
POST   /api/v1/orders/{id}/reassign/          # Reassign writer
POST   /api/v1/orders/{id}/complete/          # Mark complete
POST   /api/v1/orders/{id}/cancel/            # Cancel order
GET    /api/v1/orders/{id}/pricing/           # Get pricing breakdown
POST   /api/v1/orders/{id}/apply_discount/    # Apply discount code
```

### 4. Payments (`/api/v1/order-payments/`)
```
GET    /api/v1/order-payments/                # List payments
POST   /api/v1/order-payments/                # Create payment
GET    /api/v1/order-payments/{id}/           # Get payment details
POST   /api/v1/order-payments/initiate/       # Initiate payment

# Payment Filtering
GET    /api/v1/order-payments/by_type/        # Filter by payment type
       ?payment_type=standard
       &order_id=123
       &special_order_id=456
       &class_purchase_id=789
       &installment_id=101

# Payment Actions
POST   /api/v1/order-payments/{id}/confirm/   # Confirm payment
POST   /api/v1/order-payments/{id}/fail/      # Mark as failed
POST   /api/v1/order-payments/{id}/refund/    # Process refund
```

### 5. Discounts (`/api/v1/discounts/`)
```
GET    /api/v1/discounts/                     # List discounts
POST   /api/v1/discounts/                     # Create discount (admin)
GET    /api/v1/discounts/{id}/                # Get discount details
PUT    /api/v1/discounts/{id}/                # Update discount
DELETE /api/v1/discounts/{id}/                # Delete discount

# Discount Actions
POST   /api/v1/discounts/validate/            # Validate discount code
POST   /api/v1/discounts/apply/               # Apply discount to order
GET    /api/v1/discounts/preview/             # Preview discount calculation
GET    /api/v1/discounts/config/              # Get discount config (admin)
PUT    /api/v1/discounts/config/              # Update discount config (admin)
```

### 6. Special Orders (`/api/v1/special-orders/`)
```
GET    /api/v1/special-orders/                # List special orders
POST   /api/v1/special-orders/                # Create special order
GET    /api/v1/special-orders/{id}/           # Get order details
PUT    /api/v1/special-orders/{id}/           # Update order
POST   /api/v1/special-orders/{id}/approve/   # Approve order (admin)
POST   /api/v1/special-orders/{id}/reject/    # Reject order

# Installments
GET    /api/v1/special-orders/{id}/installments/  # List installments
POST   /api/v1/special-orders/installments/{id}/pay/  # Pay installment
```

### 7. Class Management (`/api/v1/class-management/`)
```
# Bundles
GET    /api/v1/class-management/bundles/              # List bundles
POST   /api/v1/class-management/bundles/              # Create bundle
GET    /api/v1/class-management/bundles/{id}/         # Get bundle
POST   /api/v1/class-management/bundles/create_manual/  # Admin create bundle
POST   /api/v1/class-management/bundles/{id}/pay_deposit/  # Pay deposit
POST   /api/v1/class-management/bundles/{id}/configure_installments/  # Setup installments

# Purchases
GET    /api/v1/class-management/purchases/            # List purchases
POST   /api/v1/class-management/purchases/            # Create purchase

# Installments
GET    /api/v1/class-management/installments/         # List installments
POST   /api/v1/class-management/installments/{id}/pay/  # Pay installment

# Configurations
GET    /api/v1/class-management/configs/              # List configs (admin)
POST   /api/v1/class-management/configs/              # Create config (admin)
GET    /api/v1/class-management/configs/{id}/get_class_price/  # Get price

# Communication & Files
POST   /api/v1/class-management/bundles/{id}/create_thread/  # Create thread
GET    /api/v1/class-management/bundles/{id}/threads/  # List threads
POST   /api/v1/class-management/bundles/{id}/create_ticket/  # Create ticket
GET    /api/v1/class-management/bundles/{id}/tickets/  # List tickets
POST   /api/v1/class-management/bundles/{id}/upload_file/  # Upload file
GET    /api/v1/class-management/bundles/{id}/files/   # List files
```

### 8. Fines (`/api/v1/fines/`)
```
GET    /api/v1/fines/api/fines/               # List fines
POST   /api/v1/fines/api/fines/               # Create fine (admin)
GET    /api/v1/fines/api/fines/{id}/          # Get fine details
POST   /api/v1/fines/api/fines/issue/         # Issue fine (admin)
POST   /api/v1/fines/api/fines/{id}/waive/    # Waive fine (admin)
POST   /api/v1/fines/api/fines/{id}/void/     # Void fine (admin)
POST   /api/v1/fines/api/fines/{id}/dispute/  # Dispute fine (writer)
GET    /api/v1/fines/api/fines/available-types/  # Get available fine types

# Fine Appeals
GET    /api/v1/fines/api/fine-appeals/        # List appeals
POST   /api/v1/fines/api/fine-appeals/        # Create appeal
POST   /api/v1/fines/api/fine-appeals/{id}/review/  # Review appeal (admin)
POST   /api/v1/fines/api/fine-appeals/{id}/escalate/  # Escalate appeal

# Fine Type Configuration (Admin)
GET    /api/v1/fines/api/fine-types/          # List fine types
POST   /api/v1/fines/api/fine-types/          # Create fine type
PUT    /api/v1/fines/api/fine-types/{id}/     # Update fine type
DELETE /api/v1/fines/api/fine-types/{id}/     # Delete fine type
GET    /api/v1/fines/api/fine-types/available_types/  # Get available types

# Lateness Rules (Admin)
GET    /api/v1/fines/api/lateness-rules/      # List rules
POST   /api/v1/fines/api/lateness-rules/      # Create rule
GET    /api/v1/fines/api/lateness-rules/active_rule/  # Get active rule
```

### 9. Files (`/api/v1/order-files/`)
```
GET    /api/v1/order-files/                   # List files
POST   /api/v1/order-files/                   # Upload file
GET    /api/v1/order-files/{id}/              # Get file details
DELETE /api/v1/order-files/{id}/              # Delete file
GET    /api/v1/order-files/{id}/download/     # Get download URL
GET    /api/v1/order-files/{id}/signed-url/   # Get signed download URL

# Extra Service Files
GET    /api/v1/order-files/extra-service-files/  # List extra service files
POST   /api/v1/order-files/extra-service-files/  # Upload extra service file
```

### 10. Communications (`/api/v1/order-communications/`)
```
# Threads
GET    /api/v1/order-communications/threads/  # List threads
POST   /api/v1/order-communications/threads/  # Create thread
GET    /api/v1/order-communications/threads/{id}/  # Get thread

# Messages
GET    /api/v1/order-communications/threads/{id}/messages/  # List messages
POST   /api/v1/order-communications/threads/{id}/messages/  # Send message
PUT    /api/v1/order-communications/messages/{id}/          # Update message
DELETE /api/v1/order-communications/messages/{id}/          # Delete message
```

### 11. Tickets (`/api/v1/tickets/`)
```
GET    /api/v1/tickets/                       # List tickets
POST   /api/v1/tickets/                       # Create ticket
GET    /api/v1/tickets/{id}/                  # Get ticket details
PUT    /api/v1/tickets/{id}/                  # Update ticket
POST   /api/v1/tickets/{id}/assign/           # Assign ticket (admin)
POST   /api/v1/tickets/{id}/resolve/          # Resolve ticket
POST   /api/v1/tickets/{id}/reopen/           # Reopen ticket
POST   /api/v1/tickets/{id}/escalate/         # Escalate ticket

# Ticket Messages
GET    /api/v1/tickets/{id}/messages/         # List messages
POST   /api/v1/tickets/{id}/messages/         # Add message

# Ticket Attachments
POST   /api/v1/tickets/{id}/attachments/      # Upload attachment
GET    /api/v1/tickets/{id}/attachments/      # List attachments
```

### 12. Loyalty & Redemption (`/api/v1/loyalty-management/`)
```
# Redemption Items
GET    /api/v1/loyalty-management/redemption-items/       # Browse items
GET    /api/v1/loyalty-management/redemption-items/{id}/  # Get item details

# Redemption Requests
GET    /api/v1/loyalty-management/redemption-requests/    # View history
POST   /api/v1/loyalty-management/redemption-requests/    # Create request
GET    /api/v1/loyalty-management/redemption-requests/{id}/  # Get request
POST   /api/v1/loyalty-management/redemption-requests/{id}/approve/  # Approve (admin)
POST   /api/v1/loyalty-management/redemption-requests/{id}/reject/   # Reject (admin)

# Analytics (Admin)
GET    /api/v1/loyalty-management/analytics/              # Dashboard analytics
GET    /api/v1/loyalty-management/analytics/points_trend/ # Points trend
GET    /api/v1/loyalty-management/analytics/top_redemptions/  # Top items
GET    /api/v1/loyalty-management/analytics/tier_distribution/  # Tier distribution
```

### 13. Wallet (`/api/v1/wallet/`)
```
GET    /api/v1/wallet/                        # Get wallet balance
GET    /api/v1/wallet/transactions/           # List transactions
POST   /api/v1/wallet/load/                   # Load wallet
GET    /api/v1/wallet/transactions/{id}/      # Get transaction details
```

### 14. Blog Management (`/api/v1/blog_pages_management/`)
```
# Blog Posts
GET    /api/v1/blog_pages_management/blogs/   # List posts
POST   /api/v1/blog_pages_management/blogs/   # Create post
GET    /api/v1/blog_pages_management/blogs/{id}/  # Get post
PUT    /api/v1/blog_pages_management/blogs/{id}/  # Update post
DELETE /api/v1/blog_pages_management/blogs/{id}/  # Delete post

# Categories & Tags
GET    /api/v1/blog_pages_management/categories/  # List categories
GET    /api/v1/blog_pages_management/tags/     # List tags
GET    /api/v1/blog_pages_management/authors/  # List authors

# CMS Features
GET    /api/v1/blog_pages_management/pdf-sample-sections/  # PDF sections
POST   /api/v1/blog_pages_management/pdf-samples/{id}/download/  # Download PDF
GET    /api/v1/blog_pages_management/blog-revisions/  # Revisions
GET    /api/v1/blog_pages_management/blog-previews/{token}/  # Preview link

# Content Blocks & CTAs
GET    /api/v1/blog_pages_management/cta-blocks/  # CTA blocks
GET    /api/v1/blog_pages_management/content-blocks/  # Content blocks
```

### 15. Service Pages (`/api/v1/service-pages/`)
```
GET    /api/v1/service-pages/                 # List service pages
POST   /api/v1/service-pages/                 # Create page (admin)
GET    /api/v1/service-pages/{id}/            # Get page
PUT    /api/v1/service-pages/{id}/            # Update page
DELETE /api/v1/service-pages/{id}/            # Delete page

# PDF Samples
GET    /api/v1/service-pages/service-page-pdf-sample-sections/  # PDF sections
POST   /api/v1/service-pages/service-page-pdf-samples/{id}/download/  # Download
```

### 16. Notifications (`/api/v1/notifications/`)
```
GET    /api/v1/notifications/                 # List notifications
GET    /api/v1/notifications/{id}/            # Get notification
POST   /api/v1/notifications/{id}/mark-read/  # Mark as read
POST   /api/v1/notifications/mark-all-read/   # Mark all as read
GET    /api/v1/notifications/unread-count/    # Get unread count
```

### 17. Editor Management (`/api/v1/editor-management/`)
```
# Editor Tasks
GET    /api/v1/editor-management/tasks/       # List tasks
POST   /api/v1/editor-management/tasks/{id}/claim/  # Claim task
POST   /api/v1/editor-management/tasks/{id}/submit/  # Submit review
GET    /api/v1/editor-management/tasks/{id}/  # Get task details

# Editor Dashboard
GET    /api/v1/editor-management/dashboard/   # Dashboard stats
GET    /api/v1/editor-management/analytics/   # Editor analytics
GET    /api/v1/editor-management/performance/ # Performance metrics
```

### 18. Writer Management (`/api/v1/writer-management/`)
```
GET    /api/v1/writer-management/writers/     # List writers
GET    /api/v1/writer-management/writers/{id}/  # Get writer details
GET    /api/v1/writer-management/performance/  # Writer performance
```

### 19. Client Management (`/api/v1/client-management/`)
```
GET    /api/v1/client-management/clients/     # List clients
GET    /api/v1/client-management/clients/{id}/  # Get client details
```

### 20. Websites (`/api/v1/websites/`)
```
GET    /api/v1/websites/                      # List websites
GET    /api/v1/websites/{id}/                 # Get website details
```

### 21. Order Configs (`/api/v1/order-configs/`)
```
GET    /api/v1/order-configs/                 # List configs (admin)
POST   /api/v1/order-configs/                 # Create config (admin)
```

### 22. Pricing Configs (`/api/v1/pricing-configs/`)
```
GET    /api/v1/pricing-configs/               # List pricing configs
GET    /api/v1/pricing-configs/{id}/calculate_price/  # Calculate price
```

### 23. Refunds (`/api/v1/refunds/`)
```
GET    /api/v1/refunds/                       # List refunds
POST   /api/v1/refunds/                       # Create refund (admin)
GET    /api/v1/refunds/{id}/                  # Get refund details
POST   /api/v1/refunds/{id}/process/          # Process refund
```

### 24. Referrals (`/api/v1/referrals/`)
```
GET    /api/v1/referrals/                     # List referrals
POST   /api/v1/referrals/                     # Create referral
```

### 25. Mass Emails (`/api/v1/mass-emails/`)
```
GET    /api/v1/mass-emails/                   # List campaigns (admin)
POST   /api/v1/mass-emails/                   # Create campaign (admin)
```

---

## 🔑 Authentication Flow Examples

### Complete Login Flow
```javascript
// 1. Login
const loginResponse = await fetch('/api/v1/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
    remember_me: false
  })
});

const { access_token, refresh_token, user } = await loginResponse.json();

// 2. Store tokens securely
localStorage.setItem('accessToken', access_token);
localStorage.setItem('refreshToken', refresh_token);

// 3. Use token in requests
const ordersResponse = await fetch('/api/v1/orders/', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});
```

### Token Refresh Flow
```javascript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  
  const response = await fetch('/api/v1/auth/refresh-token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
  });
  
  if (response.ok) {
    const { access } = await response.json();
    localStorage.setItem('accessToken', access);
    return access;
  } else {
    // Refresh token expired, redirect to login
    window.location.href = '/login';
  }
}

// Auto-refresh on 401
async function apiCall(url, options = {}) {
  let accessToken = localStorage.getItem('accessToken');
  
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  if (response.status === 401) {
    // Token expired, refresh and retry
    accessToken = await refreshAccessToken();
    response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${accessToken}`
      }
    });
  }
  
  return response;
}
```

---

## 📦 Request/Response Formats

### Pagination
All list endpoints are paginated:
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/orders/?page=2",
  "previous": null,
  "results": [
    { /* item 1 */ },
    { /* item 2 */ }
  ]
}
```

### Error Response
```json
{
  "detail": "Error message here",
  "code": "ERROR_CODE",
  "field_errors": {
    "field_name": ["Error 1", "Error 2"]
  }
}
```

### Success Response
```json
{
  "id": 123,
  "status": "success",
  "data": { /* response data */ }
}
```

---

## 🔒 Permissions & Roles

### Role-Based Access

| Role | Description | Access Level |
|------|-------------|--------------|
| `client` | Client user | Own orders, payments, profile |
| `writer` | Writer user | Assigned orders, own profile, disputes |
| `editor` | Editor user | Assigned orders for editing |
| `admin` | Admin user | All data, can manage users, issue fines |
| `superadmin` | Superadmin | Full system access |

### Permission Checks
- Most endpoints automatically filter by user role
- Writers see only their orders
- Admins see all orders
- Fine-grained permissions per endpoint

---

## 📤 File Upload Example

```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileObject);
formData.append('order', orderId);
formData.append('category', categoryId);
formData.append('description', 'File description');

const response = await fetch('/api/v1/order-files/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
    // Don't set Content-Type for FormData
  },
  body: formData
});

const fileData = await response.json();
```

---

## 🔄 Real-time Updates (Optional)

If WebSocket/SSE is implemented:
```javascript
// EventSource for notifications
const eventSource = new EventSource(
  `/api/v1/notifications/stream/?token=${token}`
);

eventSource.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  // Handle notification
};
```

---

## 🛠️ Frontend Integration Tools

### TypeScript/JavaScript Client Generation

Use OpenAPI Generator to generate a typed client:

```bash
# Install OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Generate TypeScript client
openapi-generator-cli generate \
  -i http://localhost:8000/api/v1/schema/ \
  -g typescript-axios \
  -o ./src/api
```

### Example Generated Usage
```typescript
import { OrdersApi } from './api';

const ordersApi = new OrdersApi({
  accessToken: localStorage.getItem('accessToken'),
  basePath: 'http://localhost:8000/api/v1'
});

// Use typed API
const orders = await ordersApi.ordersList();
```

---

## 🌍 Multi-Tenant Support

The system is multi-tenant. Website context is automatically determined from:
1. Request headers (if configured)
2. User's associated website
3. Query parameters

---

## ⚡ Rate Limiting

API requests are rate-limited. Check response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

Handle rate limiting:
```javascript
const response = await fetch('/api/v1/orders/');
const remaining = parseInt(response.headers.get('X-RateLimit-Remaining'));

if (remaining === 0) {
  const reset = parseInt(response.headers.get('X-RateLimit-Reset'));
  const waitTime = reset * 1000 - Date.now();
  await new Promise(resolve => setTimeout(resolve, waitTime));
  // Retry request
}
```

---

## 📋 Common Query Parameters

### Filtering
```
GET /api/v1/orders/?status=completed&client_id=123
```

### Search
```
GET /api/v1/orders/?search=research%20paper
```

### Ordering
```
GET /api/v1/orders/?ordering=-created_at
```

### Pagination
```
GET /api/v1/orders/?page=2&page_size=50
```

---

## ✅ Best Practices

### 1. Token Management
- Store tokens securely (httpOnly cookies recommended)
- Implement automatic token refresh
- Clear tokens on logout

### 2. Error Handling
```javascript
async function handleApiError(response) {
  if (!response.ok) {
    const error = await response.json();
    
    if (response.status === 401) {
      // Token expired - refresh
      await refreshAccessToken();
      throw new Error('Please retry');
    } else if (response.status === 403) {
      // Permission denied
      throw new Error('You do not have permission');
    } else if (response.status === 400) {
      // Validation error
      const fieldErrors = error.field_errors || {};
      throw new ValidationError(error.detail, fieldErrors);
    } else {
      throw new Error(error.detail || 'An error occurred');
    }
  }
  return response.json();
}
```

### 3. Request Interceptors (Axios)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

// Add token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const newToken = await refreshAccessToken();
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return api.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

---

## 🧪 Testing APIs

### Using Swagger UI
1. Navigate to `http://localhost:8000/api/v1/docs/swagger/`
2. Click "Authorize" button
3. Enter: `Bearer <your-token>`
4. Test any endpoint interactively

### Using cURL
```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"password"}' \
  | jq -r '.access_token')

# Use token
curl -X GET http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 API Response Examples

### Order Response
```json
{
  "id": 123,
  "client": 5,
  "topic": "Research Paper",
  "description": "10-page research paper",
  "total_price": "150.00",
  "status": "in_progress",
  "assigned_writer": 10,
  "deadline": "2024-01-15T10:00:00Z",
  "created_at": "2024-01-01T10:00:00Z",
  "submitted_at": null,
  "discount_applied": {
    "code": "NEWYEAR2024",
    "amount": "15.00"
  }
}
```

### Payment Response
```json
{
  "id": 456,
  "order": 123,
  "payment_type": "standard",
  "amount": "150.00",
  "status": "completed",
  "transaction_id": "txn_abc123",
  "payment_method": "wallet",
  "created_at": "2024-01-01T10:00:00Z",
  "payment_identifiers": {
    "order_id": 123,
    "special_order_id": null,
    "class_purchase_id": null
  }
}
```

### Fine Response
```json
{
  "id": 789,
  "order": 123,
  "fine_type": "late_submission",
  "fine_type_config": 2,
  "fine_type_name": "Late Submission",
  "amount": "15.00",
  "reason": "Auto-issued lateness fine: 2.5h late",
  "status": "issued",
  "has_appeal": false,
  "can_dispute": true,
  "imposed_at": "2024-01-15T12:30:00Z"
}
```

---

## 🔗 API Endpoints Summary

**Total API Endpoints**: 200+ endpoints across 25+ modules

**Main Categories**:
- Authentication & Authorization
- User Management
- Order Management
- Payment Processing
- Discount Management
- Special Orders
- Class Management
- File Management
- Communications
- Tickets & Support
- Fines & Disputes
- Loyalty & Redemption
- Wallet Management
- Blog & Content Management
- Editor Management
- Writer Management
- Notifications
- Analytics

---

## 📖 Next Steps

1. **Explore Swagger UI**: `http://localhost:8000/api/v1/docs/swagger/`
2. **Generate TypeScript Client**: Use OpenAPI schema to generate typed client
3. **Test Endpoints**: Use Swagger UI to test authentication and endpoints
4. **Frontend Integration**: Implement API client with automatic token refresh

---

## 🆘 Support

- **API Documentation**: `http://localhost:8000/api/v1/docs/swagger/`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/schema/`
- **ReDoc**: `http://localhost:8000/api/v1/docs/redoc/`

All endpoints are fully documented with request/response schemas, examples, and authentication requirements.

