# Tip Management API Documentation

## Overview

The Tip Management API provides endpoints for admins to track, analyze, and manage tips given to writers. This includes dashboard statistics, detailed tip listings, analytics, and earnings breakdowns.

**Base URL**: `/api/v1/admin-management/tips/`

**Authentication**: All endpoints require JWT authentication with admin or superadmin role.

---

## Endpoints

### 1. Dashboard Statistics

Get comprehensive tip statistics and earnings breakdown.

**Endpoint**: `GET /api/v1/admin-management/tips/dashboard/`

**Authentication**: Required (Admin/Superadmin)

**Query Parameters**:

| Parameter | Type | Required | Default | Description | Validation |
|-----------|------|----------|---------|-------------|------------|
| `days` | integer | No | 30 | Number of days for recent statistics | 1-365 (clamped) |

**Example Request**:
```http
GET /api/v1/admin-management/tips/dashboard/?days=30
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "summary": {
    "total_tips": 1250,
    "total_tip_amount": 125000.00,
    "total_writer_earnings": 37500.00,
    "total_platform_profit": 87500.00,
    "avg_tip_amount": 100.00,
    "avg_writer_percentage": 30.00
  },
  "recent_summary": {
    "days": 30,
    "total_tips": 150,
    "total_tip_amount": 15000.00,
    "total_writer_earnings": 4500.00,
    "total_platform_profit": 10500.00
  },
  "payment_status": {
    "completed": 1200,
    "pending": 30,
    "processing": 15,
    "failed": 5
  },
  "type_breakdown": [
    {
      "tip_type": "direct",
      "count": 800,
      "total_amount": 80000.00,
      "writer_earnings": 24000.00,
      "platform_profit": 56000.00
    },
    {
      "tip_type": "order",
      "count": 400,
      "total_amount": 40000.00,
      "writer_earnings": 12000.00,
      "platform_profit": 28000.00
    },
    {
      "tip_type": "class",
      "count": 50,
      "total_amount": 5000.00,
      "writer_earnings": 1500.00,
      "platform_profit": 3500.00
    }
  ],
  "payment_status_breakdown": [
    {
      "payment_status": "completed",
      "count": 1200,
      "total_amount": 120000.00
    },
    {
      "payment_status": "pending",
      "count": 30,
      "total_amount": 3000.00
    }
  ],
  "level_breakdown": [
    {
      "writer_level__name": "Senior",
      "count": 500,
      "total_amount": 50000.00,
      "writer_earnings": 17500.00,
      "platform_profit": 32500.00,
      "avg_percentage": 35.00
    },
    {
      "writer_level__name": "Intermediate",
      "count": 600,
      "total_amount": 60000.00,
      "writer_earnings": 18000.00,
      "platform_profit": 42000.00,
      "avg_percentage": 30.00
    }
  ]
}
```

**Response Fields**:

- `summary`: Overall statistics for all tips
  - `total_tips`: Total number of tips
  - `total_tip_amount`: Sum of all tip amounts
  - `total_writer_earnings`: Sum of writer earnings
  - `total_platform_profit`: Sum of platform profit
  - `avg_tip_amount`: Average tip amount
  - `avg_writer_percentage`: Average writer percentage

- `recent_summary`: Statistics for the last N days (specified by `days` parameter)
  - `days`: Number of days used for calculation
  - `total_tips`: Number of tips in the period
  - `total_tip_amount`: Sum of tip amounts in the period
  - `total_writer_earnings`: Sum of writer earnings in the period
  - `total_platform_profit`: Sum of platform profit in the period

- `payment_status`: Count of tips by payment status
  - `completed`: Tips with completed payments
  - `pending`: Tips with pending payments
  - `processing`: Tips with payments in progress
  - `failed`: Tips with failed payments

- `type_breakdown`: Breakdown by tip type (direct, order, class)
- `payment_status_breakdown`: Detailed breakdown by payment status
- `level_breakdown`: Breakdown by writer level

**Error Responses**:

- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User does not have admin/superadmin role
- `500 Internal Server Error`: Server error

---

### 2. List Tips

List all tips with filtering, pagination, and earnings breakdown.

**Endpoint**: `GET /api/v1/admin-management/tips/list_tips/`

**Authentication**: Required (Admin/Superadmin)

**Query Parameters**:

| Parameter | Type | Required | Default | Description | Validation |
|-----------|------|----------|---------|-------------|------------|
| `tip_type` | string | No | - | Filter by tip type | `direct`, `order`, `class` |
| `payment_status` | string | No | - | Filter by payment status | `pending`, `processing`, `completed`, `failed` |
| `writer_id` | integer | No | - | Filter by writer ID | - |
| `client_id` | integer | No | - | Filter by client ID | - |
| `date_from` | date | No | - | Filter tips from date | ISO 8601 format (YYYY-MM-DD) |
| `date_to` | date | No | - | Filter tips to date | ISO 8601 format (YYYY-MM-DD) |
| `limit` | integer | No | 50 | Number of results per page | 1-1000 (clamped) |
| `offset` | integer | No | 0 | Number of results to skip | >= 0 (clamped) |

**Example Request**:
```http
GET /api/v1/admin-management/tips/list_tips/?tip_type=order&payment_status=completed&limit=20&offset=0
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "count": 400,
  "results": [
    {
      "id": 1,
      "client": {
        "id": 10,
        "username": "client_user",
        "email": "client@example.com"
      },
      "writer": {
        "id": 5,
        "username": "writer_user",
        "email": "writer@example.com"
      },
      "tip_type": "order",
      "tip_amount": 100.00,
      "writer_earning": 30.00,
      "platform_profit": 70.00,
      "writer_percentage": 30.00,
      "payment_status": "completed",
      "sent_at": "2024-12-19T10:30:00Z",
      "order": {
        "id": 123,
        "order_number": "ORD-12345"
      },
      "website": {
        "id": 1,
        "name": "Example Website"
      }
    }
  ],
  "summary": {
    "total_tip_amount": 40000.00,
    "total_writer_earnings": 12000.00,
    "total_platform_profit": 28000.00
  }
}
```

**Response Fields**:

- `count`: Total number of tips matching the filters (before pagination)
- `results`: Array of tip objects with detailed information
  - `id`: Tip ID
  - `client`: Client information (id, username, email)
  - `writer`: Writer information (id, username, email)
  - `tip_type`: Type of tip (`direct`, `order`, `class`)
  - `tip_amount`: Total tip amount
  - `writer_earning`: Amount earned by writer
  - `platform_profit`: Amount earned by platform
  - `writer_percentage`: Percentage of tip going to writer
  - `payment_status`: Payment status (`pending`, `processing`, `completed`, `failed`)
  - `sent_at`: Timestamp when tip was sent
  - `order`: Order information (if tip_type is `order`)
  - `website`: Website information
- `summary`: Aggregated statistics for filtered results
  - `total_tip_amount`: Sum of tip amounts
  - `total_writer_earnings`: Sum of writer earnings
  - `total_platform_profit`: Sum of platform profit

**Error Responses**:

- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User does not have admin/superadmin role
- `400 Bad Request`: Invalid query parameter values
- `500 Internal Server Error`: Server error

---

### 3. Analytics

Get tip analytics with trends and breakdowns over time.

**Endpoint**: `GET /api/v1/admin-management/tips/analytics/`

**Authentication**: Required (Admin/Superadmin)

**Query Parameters**:

| Parameter | Type | Required | Default | Description | Validation |
|-----------|------|----------|---------|-------------|------------|
| `days` | integer | No | 90 | Number of days for analytics | 1-365 (clamped) |

**Example Request**:
```http
GET /api/v1/admin-management/tips/analytics/?days=90
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "period": {
    "days": 90,
    "date_from": "2024-09-20T00:00:00Z"
  },
  "trends": {
    "monthly": [
      {
        "month": "2024-09-01T00:00:00Z",
        "count": 100,
        "total_amount": 10000.00,
        "writer_earnings": 3000.00,
        "platform_profit": 7000.00
      },
      {
        "month": "2024-10-01T00:00:00Z",
        "count": 120,
        "total_amount": 12000.00,
        "writer_earnings": 3600.00,
        "platform_profit": 8400.00
      }
    ],
    "weekly": [
      {
        "week": "2024-12-09T00:00:00Z",
        "count": 25,
        "total_amount": 2500.00,
        "writer_earnings": 750.00,
        "platform_profit": 1750.00
      }
    ],
    "daily": [
      {
        "day": "2024-12-19T00:00:00Z",
        "count": 5,
        "total_amount": 500.00,
        "writer_earnings": 150.00,
        "platform_profit": 350.00
      }
    ]
  },
  "breakdowns": {
    "by_type": [
      {
        "tip_type": "direct",
        "count": 200,
        "total_amount": 20000.00,
        "writer_earnings": 6000.00,
        "platform_profit": 14000.00,
        "avg_amount": 100.00
      }
    ],
    "by_level": [
      {
        "writer_level__name": "Senior",
        "tip_count": 150,
        "total_tips": 15000.00,
        "total_writer_earnings": 5250.00,
        "total_platform_profit": 9750.00,
        "avg_percentage": 35.00
      }
    ]
  },
  "top_performers": {
    "writers": [
      {
        "writer__id": 5,
        "writer__username": "top_writer",
        "writer__email": "top@example.com",
        "tip_count": 50,
        "total_received": 1500.00,
        "avg_tip": 30.00
      }
    ],
    "clients": [
      {
        "client__id": 10,
        "client__username": "generous_client",
        "client__email": "client@example.com",
        "tip_count": 30,
        "total_sent": 3000.00
      }
    ]
  }
}
```

**Response Fields**:

- `period`: Analytics period information
  - `days`: Number of days analyzed
  - `date_from`: Start date of the period

- `trends`: Time-based trends
  - `monthly`: Monthly aggregation (all months in period)
  - `weekly`: Weekly aggregation (last 12 weeks)
  - `daily`: Daily aggregation (last 30 days)

- `breakdowns`: Categorical breakdowns
  - `by_type`: Breakdown by tip type
  - `by_level`: Breakdown by writer level

- `top_performers`: Top performers
  - `writers`: Top 10 writers by total earnings
  - `clients`: Top 10 clients by total tips sent

**Error Responses**:

- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User does not have admin/superadmin role
- `500 Internal Server Error`: Server error

---

### 4. Earnings

Get detailed earnings breakdown for completed tips.

**Endpoint**: `GET /api/v1/admin-management/tips/earnings/`

**Authentication**: Required (Admin/Superadmin)

**Query Parameters**:

| Parameter | Type | Required | Default | Description | Validation |
|-----------|------|----------|---------|-------------|------------|
| `date_from` | date | No | - | Filter earnings from date | ISO 8601 format (YYYY-MM-DD) |
| `date_to` | date | No | - | Filter earnings to date | ISO 8601 format (YYYY-MM-DD) |

**Example Request**:
```http
GET /api/v1/admin-management/tips/earnings/?date_from=2024-01-01&date_to=2024-12-31
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "overall": {
    "total_tips": 1000,
    "total_tip_amount": 100000.00,
    "total_writer_earnings": 30000.00,
    "total_platform_profit": 70000.00,
    "avg_tip_amount": 100.00,
    "avg_writer_percentage": 30.00,
    "platform_profit_percentage": 70.00
  },
  "by_level": [
    {
      "writer_level__name": "Senior",
      "tip_count": 400,
      "total_tips": 40000.00,
      "writer_earnings": 14000.00,
      "platform_profit": 26000.00,
      "avg_percentage": 35.00
    }
  ],
  "by_type": [
    {
      "tip_type": "direct",
      "tip_count": 600,
      "total_tips": 60000.00,
      "writer_earnings": 18000.00,
      "platform_profit": 42000.00
    }
  ],
  "monthly": [
    {
      "month": "2024-01-01T00:00:00Z",
      "tip_count": 80,
      "total_tips": 8000.00,
      "writer_earnings": 2400.00,
      "platform_profit": 5600.00
    }
  ]
}
```

**Response Fields**:

- `overall`: Overall earnings statistics (only completed tips)
  - `total_tips`: Total number of completed tips
  - `total_tip_amount`: Sum of tip amounts
  - `total_writer_earnings`: Sum of writer earnings
  - `total_platform_profit`: Sum of platform profit
  - `avg_tip_amount`: Average tip amount
  - `avg_writer_percentage`: Average writer percentage
  - `platform_profit_percentage`: Platform profit as percentage of total

- `by_level`: Earnings breakdown by writer level
- `by_type`: Earnings breakdown by tip type
- `monthly`: Monthly earnings (last 12 months)

**Error Responses**:

- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User does not have admin/superadmin role
- `400 Bad Request`: Invalid date format
- `500 Internal Server Error`: Server error

---

## Authentication

All endpoints require JWT Bearer token authentication:

```http
Authorization: Bearer <access_token>
```

Get access token via `/api/v1/auth/login/` endpoint.

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

### Common Error Codes

- `authentication_failed`: Invalid or missing authentication token
- `permission_denied`: User does not have required permissions
- `validation_error`: Invalid input parameters
- `not_found`: Resource not found
- `server_error`: Internal server error

---

## Rate Limiting

API endpoints are rate-limited. Check response headers for rate limit information:

- `X-RateLimit-Limit`: Maximum number of requests allowed
- `X-RateLimit-Remaining`: Number of requests remaining
- `X-RateLimit-Reset`: Time when rate limit resets

---

## Multi-Tenancy

All endpoints automatically filter results by the admin's website context. Admins can only view tips for their assigned website. Superadmins can view tips across all websites.

---

## Notes

1. **Date Formats**: All date parameters should be in ISO 8601 format (YYYY-MM-DD)
2. **Pagination**: Maximum limit is 1000 records per request
3. **Filtering**: Multiple filters can be combined (AND logic)
4. **Performance**: Large date ranges may result in slower responses
5. **Currency**: All monetary values are in the website's base currency

---

## Interactive Documentation

For interactive API documentation, visit:
- **Swagger UI**: `/api/v1/docs/swagger/`
- **ReDoc**: `/api/v1/docs/redoc/`

Both interfaces allow you to:
- Explore all endpoints
- Test endpoints directly
- View request/response schemas
- Authorize with JWT tokens

