# Frontend-Backend Integration Test Guide

This guide explains how to test the integration between the Vue.js frontend and Django backend.

## Quick Start

### 1. Start Backend and Frontend

**Backend:**
```bash
cd writing_system_backend
docker-compose up -d
```

**Frontend:**
```bash
cd writing_system_frontend
npm run dev
```

### 2. Run Integration Tests

**Backend Integration Test (Python):**
```bash
cd writing_system_backend
docker-compose exec web python test_frontend_backend_integration.py
```

**Or use the test runner:**
```bash
cd writing_system_backend
./run_integration_tests.sh
```

**Frontend Integration Test (JavaScript):**
```bash
cd writing_system_frontend
npm run dev
# Then open browser console and run:
# import { runIntegrationTest } from './test-integration.js'
# runIntegrationTest()
```

## Manual Testing

### Test Login Flow

1. **Backend API Test:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@test.com","password":"testpass123"}'
```

2. **Frontend Test:**
   - Open http://localhost:5173
   - Navigate to login page
   - Enter credentials and submit
   - Check browser console and network tab

### Test Registration Flow

1. **Backend API Test:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username":"test_user",
    "email":"test@example.com",
    "password":"TestPassword123!",
    "password2":"TestPassword123!",
    "role":"client"
  }'
```

2. **Frontend Test:**
   - Open http://localhost:5173/signup
   - Fill registration form
   - Submit and check for success/error

## Troubleshooting

### Login Returns 500 Error

**Check server logs:**
```bash
docker-compose logs web --tail 50
```

**Common issues:**
1. **Website is None**: User must be assigned to a website
   - Fix: Ensure test user has a website assigned
   - Check: `python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.first(); print(u.website)"`

2. **UserProfile missing**: User needs a profile
   - Fix: Profile should auto-create, but can manually create:
   - `python manage.py shell -c "from users.models import UserProfile; from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.first(); UserProfile.objects.get_or_create(user=u)"`

3. **Redis/Celery not running**: Non-critical, but can cause warnings
   - Fix: Start Redis: `docker-compose up -d redis`

### Frontend Cannot Connect to Backend

1. **Check CORS settings** in `writing_system/settings.py`
2. **Verify API URL** in frontend `.env` file:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   VITE_API_FULL_URL=http://localhost:8000/api/v1
   ```
3. **Check backend is running:**
   ```bash
   curl http://localhost:8000/api/v1/
   ```

### Registration Fails

1. **Check if endpoint exists:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/auth/register/ -H "Content-Type: application/json" -d '{}'
   ```

2. **Check user model constraints:**
   - Username must be unique
   - Email must be unique
   - Password must meet requirements

## Test Checklist

- [ ] Backend API is accessible
- [ ] Login endpoint works
- [ ] Registration endpoint works
- [ ] JWT tokens are generated correctly
- [ ] Authenticated requests work
- [ ] Frontend can connect to backend
- [ ] Frontend login form works
- [ ] Frontend registration form works
- [ ] Token is stored correctly in frontend
- [ ] Token is sent with authenticated requests

## Next Steps

After integration tests pass:
1. Test full user workflows (create order, submit, etc.)
2. Test role-based access control
3. Test error handling
4. Test edge cases (expired tokens, network errors, etc.)

