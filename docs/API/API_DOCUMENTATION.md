# API Documentation

**Version**: 1.0  
**Base URL**: `https://yourdomain.com/api/v1/`  
**Last Updated**: December 2025

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [API Endpoints](#api-endpoints)
3. [Request/Response Formats](#requestresponse-formats)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Pagination](#pagination)
7. [Filtering & Sorting](#filtering--sorting)
8. [Examples](#examples)

---

## 🔐 Authentication

### Authentication Method

The API uses **JWT (JSON Web Token)** Bearer token authentication.

### Getting an Access Token

#### Login Endpoint

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

#### Response

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "client"
  }
}
```

### Using the Access Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refreshing Tokens

```http
POST /api/v1/auth/refresh-token/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 📡 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login/` | Login and get tokens | No |
| POST | `/auth/logout/` | Logout | Yes |
| POST | `/auth/refresh-token/` | Refresh access token | No |
| POST | `/auth/verify_2fa/` | Verify 2FA code | No |
| POST | `/auth/account-unlock/` | Request account unlock | No |

### User Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users/` | List users (admin) | Yes |
| GET | `/users/{id}/` | Get user details | Yes |
| GET | `/users/profile/` | Get own profile | Yes |
| PUT | `/users/profile/` | Update own profile | Yes |
| POST | `/users/{id}/impersonate/` | Impersonate user (admin) | Yes |

### Order Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/orders/` | List orders | Yes |
| POST | `/orders/` | Create order | Yes |
| GET | `/orders/{id}/` | Get order details | Yes |
| PUT | `/orders/{id}/` | Update order | Yes |
| POST | `/orders/{id}/pay/` | Pay for order | Yes |
| POST | `/orders/{id}/request-revision/` | Request revision | Yes |

### Client Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/client-management/dashboard/stats/` | Dashboard statistics | Yes (Client) |
| GET | `/client-management/dashboard/analytics/` | Analytics | Yes (Client) |
| GET | `/client-management/dashboard/enhanced-order-status/` | Enhanced order status | Yes (Client) |
| GET | `/client-management/dashboard/payment-reminders/` | Payment reminders | Yes (Client) |
| GET | `/client-management/dashboard/order-activity-timeline/` | Activity timeline | Yes (Client) |

### Writer Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/writer-management/dashboard/earnings/` | Earnings breakdown | Yes (Writer) |
| GET | `/writer-management/dashboard/workload-capacity/` | Workload capacity | Yes (Writer) |
| GET | `/writer-management/dashboard/calendar/` | Deadline calendar | Yes (Writer) |
| GET | `/writer-management/dashboard/payment-status/` | Payment status | Yes (Writer) |

### Editor Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/editor-management/profiles/dashboard/analytics/` | Task analytics | Yes (Editor) |
| GET | `/editor-management/profiles/dashboard/workload/` | Workload management | Yes (Editor) |
| GET | `/editor-management/profiles/dashboard/performance/` | Performance metrics | Yes (Editor) |

### Support Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/support-management/dashboard/tickets/` | Ticket dashboard | Yes (Support) |
| GET | `/support-management/dashboard/orders/` | Order management | Yes (Support) |
| GET | `/support-management/dashboard/escalations/` | Escalations | Yes (Support) |
| GET | `/support-management/dashboard/analytics/performance/` | Performance analytics | Yes (Support) |

### Admin Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin-management/dashboard/disputes/` | Dispute management | Yes (Admin) |
| GET | `/admin-management/dashboard/refunds/` | Refund management | Yes (Admin) |
| GET | `/admin-management/dashboard/reviews/` | Review moderation | Yes (Admin) |
| GET | `/admin-management/dashboard/advanced-analytics/` | Advanced analytics | Yes (Admin) |

### Superadmin Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/superadmin-management/tenants/list_tenants/` | List tenants | Yes (Superadmin) |
| POST | `/superadmin-management/tenants/create_tenant/` | Create tenant | Yes (Superadmin) |
| GET | `/superadmin-management/tenants/cross-tenant-analytics/` | Cross-tenant analytics | Yes (Superadmin) |

---

## 📥 Request/Response Formats

### Request Format

All requests should use `application/json` content type:

```http
Content-Type: application/json
```

### Response Format

All responses are in JSON format:

```json
{
  "data": {...},
  "message": "Success",
  "status": "success"
}
```

### Error Response Format

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "status": "error",
  "code": "ERROR_CODE"
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### Common Error Codes

- `AUTHENTICATION_REQUIRED` - Authentication token missing or invalid
- `PERMISSION_DENIED` - User doesn't have required permissions
- `VALIDATION_ERROR` - Request data validation failed
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED` - Too many requests

---

## 🚦 Rate Limiting

### Rate Limits

- **Default**: 1000 requests per hour per user
- **Authentication**: 5 login attempts per 15 minutes
- **API Endpoints**: Varies by endpoint

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

```json
{
  "error": "Rate limit exceeded",
  "detail": "You have exceeded the rate limit. Please try again later.",
  "retry_after": 3600
}
```

---

## 📄 Pagination

### Paginated Responses

```json
{
  "count": 100,
  "next": "https://api.example.com/orders/?page=2",
  "previous": null,
  "results": [...]
}
```

### Pagination Parameters

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

### Example

```http
GET /api/v1/orders/?page=2&page_size=50
```

---

## 🔍 Filtering & Sorting

### Filtering

Use query parameters to filter results:

```http
GET /api/v1/orders/?status=in_progress&is_paid=true
```

### Sorting

Use `ordering` parameter:

```http
GET /api/v1/orders/?ordering=-created_at
```

- Prefix with `-` for descending order
- Multiple fields: `ordering=status,-created_at`

### Search

Use `search` parameter:

```http
GET /api/v1/orders/?search=essay
```

---

## 💡 Examples

### Creating an Order

```javascript
const response = await fetch('/api/v1/orders/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    topic: 'Essay on Climate Change',
    paper_type_id: 1,
    academic_level_id: 2,
    number_of_pages: 5,
    client_deadline: '2025-12-31T23:59:59Z',
    order_instructions: 'Detailed instructions here...'
  })
});

const order = await response.json();
```

### Getting Dashboard Stats

```javascript
const response = await fetch('/api/v1/client-management/dashboard/stats/?days=30', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});

const stats = await response.json();
```

### Filtering Orders

```javascript
const response = await fetch('/api/v1/orders/?status=in_progress&ordering=-created_at&page=1&page_size=20', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});

const orders = await response.json();
```

---

## 📚 Additional Resources

- **Swagger UI**: `/api/v1/docs/swagger/`
- **ReDoc**: `/api/v1/docs/redoc/`
- **OpenAPI Schema**: `/api/v1/schema/`

---

**Last Updated**: December 2025

