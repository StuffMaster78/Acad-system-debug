# Manual Impersonation Testing Guide

## Prerequisites
1. Server running: `docker-compose up`
2. Admin user with `superadmin` or `admin` role
3. Target user (client or writer) to impersonate

## Test Workflow

### Step 1: Login as Admin
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password"
  }'
```

Save the `access_token` from the response.

### Step 2: Create Impersonation Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/impersonate/create_token/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_user": CLIENT_USER_ID
  }'
```

Save the `token` from the response.

### Step 3: Check Status (Before Impersonation)
```bash
curl -X GET http://localhost:8000/api/v1/auth/impersonate/status/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Should return: `{"is_impersonating": false, "impersonator": null}`

### Step 4: Start Impersonation
```bash
curl -X POST http://localhost:8000/api/v1/auth/impersonate/start/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_IMPERSONATION_TOKEN"
  }'
```

Save the new `access_token` from the response (this is for the client user).

### Step 5: Check Status (During Impersonation)
```bash
curl -X GET http://localhost:8000/api/v1/auth/impersonate/status/ \
  -H "Authorization: Bearer CLIENT_TOKEN_FROM_STEP_4"
```

Should return:
```json
{
  "is_impersonating": true,
  "impersonator": {
    "id": ADMIN_ID,
    "username": "admin",
    "email": "admin@example.com",
    "role": "superadmin"
  }
}
```

### Step 6: Verify Client Session
```bash
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer CLIENT_TOKEN_FROM_STEP_4"
```

Should return the client's profile (not admin's).

### Step 7: End Impersonation
```bash
curl -X POST http://localhost:8000/api/v1/auth/impersonate/end/ \
  -H "Authorization: Bearer CLIENT_TOKEN_FROM_STEP_4"
```

Save the new `access_token` from the response (this should be the admin token again).

### Step 8: Verify Admin Session Restored
```bash
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer ADMIN_TOKEN_FROM_STEP_7"
```

Should return the admin's profile.

## Using Python Script

Run the automated test:
```bash
docker-compose exec web python test_impersonation.py
```

## Expected Behavior

1. ✅ Admin can create impersonation token for clients/writers
2. ✅ Admin can start impersonation using token
3. ✅ Status endpoint correctly reports impersonation state
4. ✅ During impersonation, user appears as target user
5. ✅ Admin can end impersonation
6. ✅ After ending, admin is restored to original session
7. ✅ Impersonation logs are created in database
8. ✅ Permissions are enforced (admins can't impersonate other admins)

## Security Checks

- ❌ Admin cannot impersonate themselves
- ❌ Admin cannot impersonate other admins (unless superadmin)
- ❌ Regular users cannot create impersonation tokens
- ❌ Tokens expire after 1 hour
- ❌ Tokens can only be used once (if configured)

