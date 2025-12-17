# Endpoint Masking Documentation

## Overview

Endpoint masking provides security through obscurity by hiding actual API endpoint paths from writers and clients. This makes it harder for users to discover admin/internal endpoints by inspecting the frontend code or network requests.

## How It Works

### Full Endpoint Masking with Backend Proxy

The endpoint masking system:
1. **Maps actual endpoints to masked ones** based on user role
2. **Transforms endpoints** in the API client before requests are made
3. **Routes requests through backend proxy** (`/api/v1/proxy/`) which internally calls actual endpoints
4. **Preserves functionality** while completely hiding actual endpoint structure from network requests

### Role-Based Masking

- **Clients**: See masked endpoints like `/client/orders/` instead of `/orders/orders/`
- **Writers**: See masked endpoints like `/writer/orders/` instead of `/writer-management/writer-orders/`
- **Admins/Superadmins**: See all endpoints unmasked (no masking)

### Example Mappings

**Client Role:**
- `/orders/orders/` → `/client/orders/`
- `/users/users/profile/` → `/client/profile/`
- `/referrals/referral-codes/my-code/` → `/client/referrals/code/`

**Writer Role:**
- `/writer-management/writer-orders/` → `/writer/orders/`
- `/writer-management/writer-payments/` → `/writer/payments/`
- `/writer-management/writer-profiles/me/` → `/writer/profile/`

## Configuration

### Enable/Disable Masking

Set environment variable in frontend `.env`:
```bash
# Enable full endpoint masking with backend proxy
VITE_ENABLE_ENDPOINT_MASKING=true

# Disable masking (use actual endpoints)
VITE_ENABLE_ENDPOINT_MASKING=false
```

When enabled:
- **Clients/Writers**: See masked endpoints like `/proxy/client/orders/` in network requests
- **Admins/Superadmins**: See actual endpoints (no masking)
- **Backend**: Proxy routes masked endpoints to actual endpoints internally

### Adding New Endpoint Mappings

Edit `frontend/src/utils/endpoint-masker.js`:

```javascript
const ENDPOINT_MAPPINGS = {
  client: {
    '/actual/endpoint/': '/client/masked/endpoint/',
    // Add more mappings...
  },
  writer: {
    '/actual/endpoint/': '/writer/masked/endpoint/',
    // Add more mappings...
  },
}
```

## Security Considerations

### Important Notes

1. **This is NOT a replacement for proper authentication/authorization**
   - Backend permissions are still enforced
   - This only provides obscurity, not security

2. **Full Network-Level Masking**
   - When `VITE_ENABLE_ENDPOINT_MASKING=true`, all requests go through `/api/v1/proxy/`
   - Network requests show masked endpoints (e.g., `/proxy/client/orders/`)
   - Actual endpoints are never exposed to clients/writers

3. **Admin endpoints are blocked**
   - Non-admin users attempting to access admin endpoints get 403 Forbidden
   - Backend proxy validates role-based access before routing

4. **Backend Proxy Implementation**
   - Proxy uses Django's test client to make internal requests
   - Preserves authentication and session
   - Handles all HTTP methods (GET, POST, PUT, PATCH, DELETE)

## Implementation Details

### Frontend

- **Location**: `frontend/src/utils/endpoint-masker.js`
- **Integration**: `frontend/src/api/client.js` (request interceptor)
- **Function**: `maskEndpoint(url, role)` - transforms endpoints based on role
- **Proxy Routing**: When masking enabled, routes through `/api/v1/proxy/{masked_path}`

### Backend

- **Proxy Endpoint**: `backend/core/endpoint_proxy.py`
- **URL Routing**: `backend/core/endpoint_proxy_urls.py`
- **Main URLs**: Added to `backend/writing_system/urls.py`

The proxy:
1. Accepts masked endpoints at `/api/v1/proxy/{masked_path}`
2. Validates user role and permissions
3. Routes to actual endpoints internally using Django's test client
4. Returns responses without exposing actual endpoint structure
5. Preserves authentication, headers, and query parameters

## Testing

To test endpoint masking:

1. **As a client/writer**: Check browser DevTools Network tab
   - Endpoints should appear masked in the code
   - Network requests may still show actual endpoints (depending on implementation)

2. **As an admin**: All endpoints should appear unmasked

3. **Verify functionality**: All API calls should work normally regardless of masking

## Troubleshooting

### Endpoints not masking

- Check `VITE_ENABLE_ENDPOINT_MASKING` environment variable
- Verify user role is set correctly in localStorage
- Check that endpoint is in the mapping for that role

### Endpoints breaking

- Ensure endpoint mapping preserves path structure (IDs, query params, etc.)
- Check browser console for errors
- Verify backend still accepts the actual endpoint

## Future Improvements

1. **Backend Proxy**: Implement full endpoint masking via backend proxy
2. **Dynamic Mappings**: Load endpoint mappings from backend configuration
3. **Obfuscation**: Further obfuscate endpoint names
4. **Rate Limiting**: Add rate limiting to masked endpoints

