# API Rate Limiting Implementation Guide

## 🎯 Overview

A comprehensive rate limiting system has been implemented to protect the API from abuse, prevent DoS attacks, and ensure fair resource usage. The system provides multiple layers of rate limiting with different strategies for different endpoint types.

## 🏗️ Architecture

### Rate Limiting Components

1. **Throttling Classes** (`backend/core/throttling/rate_limiter.py`)
   - `BurstRateThrottle`: Short-term burst protection
   - `SustainedRateThrottle`: Long-term sustained limits
   - `WriteOperationThrottle`: Stricter limits for write operations
   - `ReadOperationThrottle`: More lenient limits for read operations
   - `IPRateThrottle`: IP-based limiting for anonymous users
   - `AdminRateThrottle`: Higher limits for admin users
   - `PublicEndpointThrottle`: Limits for public endpoints
   - `EndpointRateThrottle`: Per-endpoint specific limits

2. **Endpoint Configuration** (`backend/core/throttling/endpoint_config.py`)
   - Fine-grained control over specific endpoints
   - Different limits for authentication, payments, orders, etc.

3. **Monitoring** (`backend/core/throttling/monitoring.py`)
   - Tracks rate limit violations
   - Provides analytics and statistics
   - Logs violations for security analysis

4. **Admin API** (`backend/admin_management/views/rate_limiting.py`)
   - View rate limit statistics
   - Monitor violations
   - Clear statistics

## 📊 Rate Limit Tiers

### Default Limits (in `settings.py`)

| Scope | Rate | Description |
|-------|------|-------------|
| `user` | 5000/hour | General authenticated user limit (~83/min) |
| `anon` | 500/hour | Unauthenticated users (~8/min) |
| `burst` | 100/minute | Short-term burst protection |
| `sustained` | 10000/day | Long-term sustained limit |
| `write` | 200/hour | Write operations (POST, PUT, PATCH, DELETE) |
| `read` | 10000/hour | Read operations (GET, HEAD, OPTIONS) |
| `ip` | 1000/hour | Per IP address limit |
| `admin` | 20000/hour | Admin users (higher limits) |
| `public` | 200/hour | Public endpoints (no auth) |

### Endpoint-Specific Limits

| Endpoint | Rate | Scope |
|----------|------|-------|
| `/api/v1/auth/auth/login/` | 10/minute | `login` |
| `/api/v1/auth/auth/password-reset/` | 10/hour | `password_reset` |
| `/api/v1/orders/orders/` | 50/hour | `write` |
| `/api/v1/order-payments/payments/` | 30/hour | `write` |
| `/api/v1/orders/guest-orders/start/` | 20/hour | `public` |
| `/api/v1/admin/dashboard/` | 200/hour | `read` |

## 🔧 Configuration

### Settings (`backend/writing_system/settings.py`)

The rate limiting is configured in `REST_FRAMEWORK` settings:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'core.throttling.rate_limiter.BurstRateThrottle',
        'core.throttling.rate_limiter.SustainedRateThrottle',
        'core.throttling.rate_limiter.WriteOperationThrottle',
        'core.throttling.rate_limiter.IPRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        # ... rate configurations
    },
}
```

### Adding Endpoint-Specific Limits

Edit `backend/core/throttling/endpoint_config.py`:

```python
ENDPOINT_RATE_LIMITS = {
    '/api/v1/your-endpoint/': {
        'scope': 'write',
        'rate': '30/hour',
    },
}
```

## 📈 Monitoring

### Admin API Endpoints

All endpoints require admin authentication:

1. **Get Statistics**
   ```
   GET /api/v1/admin/rate-limiting/stats/
   Query params:
   - scope (str): Filter by scope
   - user_id (int): Filter by user ID
   - ip (str): Filter by IP
   - limit (int): Max violations to return
   ```

2. **Top Endpoints**
   ```
   GET /api/v1/admin/rate-limiting/top-endpoints/
   Query params:
   - limit (int): Number of top endpoints (default: 10)
   ```

3. **Top Users**
   ```
   GET /api/v1/admin/rate-limiting/top-users/
   Query params:
   - limit (int): Number of top users (default: 10)
   ```

4. **Top IPs**
   ```
   GET /api/v1/admin/rate-limiting/top-ips/
   Query params:
   - limit (int): Number of top IPs (default: 10)
   ```

5. **Clear Statistics**
   ```
   POST /api/v1/admin/rate-limiting/clear-stats/
   ```

### Response Headers

When rate limiting is active, responses include:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

### Rate Limit Exceeded Response

When a rate limit is exceeded, the API returns:

```json
{
  "detail": "Request was throttled. Expected available in X seconds."
}
```

Status code: `429 Too Many Requests`

## 🛡️ Security Features

1. **Multi-Layer Protection**
   - Burst protection (short-term)
   - Sustained limits (long-term)
   - Per-endpoint limits
   - IP-based limiting

2. **Role-Based Limits**
   - Admin users get higher limits
   - Regular users have standard limits
   - Anonymous users have stricter limits

3. **Operation-Based Limits**
   - Write operations (POST, PUT, PATCH, DELETE) are more restricted
   - Read operations (GET, HEAD, OPTIONS) are more lenient

4. **Monitoring & Logging**
   - All violations are logged
   - Statistics tracked in Redis cache
   - Admin dashboard for monitoring

## 🔍 Usage Examples

### Applying Rate Limits to a ViewSet

```python
from rest_framework import viewsets
from core.throttling.rate_limiter import WriteOperationThrottle

class MyViewSet(viewsets.ModelViewSet):
    throttle_classes = [WriteOperationThrottle]
    # ... rest of viewset
```

### Custom Throttle for Specific Action

```python
from rest_framework.decorators import action
from core.throttling.rate_limiter import BurstRateThrottle

class MyViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['post'], throttle_classes=[BurstRateThrottle])
    def custom_action(self, request):
        # This action has burst rate limiting
        pass
```

## 📝 Best Practices

1. **Production Settings**
   - Increase limits for production (current settings are development-friendly)
   - Monitor violations regularly
   - Adjust limits based on actual usage patterns

2. **Endpoint Configuration**
   - Use stricter limits for sensitive operations (payments, authentication)
   - Use more lenient limits for read-heavy endpoints (dashboards, listings)

3. **Monitoring**
   - Review top violated endpoints regularly
   - Investigate users/IPs with high violation rates
   - Adjust limits based on legitimate usage patterns

4. **Error Handling**
   - Frontend should handle 429 responses gracefully
   - Show user-friendly messages
   - Implement exponential backoff for retries

## 🚀 Production Recommendations

1. **Increase Limits**
   ```python
   'user': '10000/hour',  # Increase from 5000
   'anon': '1000/hour',   # Increase from 500
   'write': '500/hour',   # Increase from 200
   ```

2. **Enable Redis Caching**
   - Ensure Redis is properly configured
   - Monitor Redis memory usage
   - Set appropriate cache timeouts

3. **Monitoring Dashboard**
   - Create admin dashboard for rate limit stats
   - Set up alerts for excessive violations
   - Track trends over time

4. **Documentation**
   - Document rate limits in API documentation
   - Provide rate limit information to API consumers
   - Include rate limit headers in API responses

## 🐛 Troubleshooting

### Rate Limits Too Strict

1. Check current limits in `settings.py`
2. Review violation statistics via admin API
3. Adjust limits based on legitimate usage

### Rate Limits Not Working

1. Verify Redis is running and accessible
2. Check middleware order in `settings.py`
3. Verify throttle classes are in `DEFAULT_THROTTLE_CLASSES`
4. Check cache configuration

### False Positives

1. Review violation logs
2. Check if legitimate users are being limited
3. Adjust limits or add exceptions for specific users/IPs

## 📚 Related Files

- `backend/core/throttling/rate_limiter.py` - Throttling classes
- `backend/core/throttling/endpoint_config.py` - Endpoint-specific configs
- `backend/core/throttling/monitoring.py` - Monitoring utilities
- `backend/admin_management/views/rate_limiting.py` - Admin API
- `backend/writing_system/settings.py` - Configuration

## ✅ Implementation Status

- ✅ Multi-layer rate limiting
- ✅ Per-endpoint configuration
- ✅ IP-based limiting
- ✅ Role-based limits
- ✅ Operation-based limits
- ✅ Monitoring and logging
- ✅ Admin API for statistics
- ✅ Rate limit headers in responses

