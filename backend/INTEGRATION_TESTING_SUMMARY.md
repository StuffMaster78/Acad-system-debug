# Frontend-Backend Integration Testing Summary

## ✅ Created Test Suite

I've created a comprehensive integration testing suite for frontend-backend integration:

### Backend Tests
- **File**: `test_frontend_backend_integration.py`
- **Tests**:
  - API availability
  - User registration
  - User login
  - Authenticated requests
  - Order workflow

### Frontend Tests
- **File**: `writing_system_frontend/test-integration.js`
- **Tests**:
  - API connectivity
  - User registration
  - User login
  - Token-based authentication
  - Orders API

### Test Runner
- **File**: `run_integration_tests.sh`
- Automatically checks backend/frontend status and runs tests

### Documentation
- **File**: `INTEGRATION_TEST_GUIDE.md`
- Complete guide with troubleshooting steps

## 🚀 How to Run Tests

### Quick Test
```bash
cd writing_system_backend
./run_integration_tests.sh
```

### Manual Backend Test
```bash
cd writing_system_backend
docker-compose exec web python test_frontend_backend_integration.py
```

### Manual Frontend Test
1. Start frontend: `cd writing_system_frontend && npm run dev`
2. Open browser console
3. Run: `import { runIntegrationTest } from './test-integration.js'; runIntegrationTest()`

## 🔍 Debugging Login 500 Error

The login endpoint returns 500 errors. To debug:

### 1. Check Detailed Error (with improved logging)
```bash
curl -X POST http://localhost:8000/api/v1/auth/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@test.com","password":"testpass123"}'
```

The response will now include detailed error information in DEBUG mode.

### 2. Check Server Logs
```bash
docker-compose logs web --tail 100 | grep -A 20 "Login error"
```

### 3. Verify User Setup
```bash
docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
from websites.models import Website
User = get_user_model()
user = User.objects.filter(role='superadmin').first()
website = Website.objects.filter(is_active=True).first()
print(f'User: {user.username if user else None}')
print(f'User website: {user.website.name if user and user.website else None}')
print(f'Active website: {website.name if website else None}')
print(f'User profile exists: {hasattr(user, \"user_main_profile\") and user.user_main_profile is not None}')
"
```

### Common Issues and Fixes

#### Issue 1: Website is None
**Symptom**: `Cannot create login session: No website available`

**Fix**:
```python
# Assign website to user
from django.contrib.auth import get_user_model
from websites.models import Website
User = get_user_model()
user = User.objects.filter(role='superadmin').first()
website = Website.objects.filter(is_active=True).first()
if website:
    user.website = website
    user.save()
```

#### Issue 2: UserProfile Missing
**Symptom**: `AttributeError: 'User' object has no attribute 'user_main_profile'`

**Fix**: Profile should auto-create, but can manually create:
```python
from users.models import UserProfile
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
UserProfile.objects.get_or_create(user=user, defaults={'avatar': 'avatars/universal.png'})
```

#### Issue 3: Login Session Creation Fails
**Symptom**: Database constraint violation on LoginSession

**Fix**: Ensure website exists before login:
- The code now auto-assigns website if missing
- Check server logs for specific error

## 📋 Test Checklist

Run through this checklist to ensure everything works:

- [ ] Backend server is running (`docker-compose ps`)
- [ ] Frontend server is running (`npm run dev`)
- [ ] API root is accessible (`curl http://localhost:8000/api/v1/`)
- [ ] Login endpoint exists (`curl -X POST http://localhost:8000/api/v1/auth/auth/login/`)
- [ ] Test user exists and has website assigned
- [ ] Test user has UserProfile
- [ ] Test user password is known (`testpass123`)
- [ ] CORS is configured correctly
- [ ] Frontend can make requests to backend

## 🎯 Next Steps

1. **Run the integration tests** to identify specific failures
2. **Check the detailed error logs** from the improved error handling
3. **Fix any identified issues** based on error messages
4. **Test the full user journey**:
   - Registration → Login → Dashboard → Create Order → Submit Order

## 📝 Notes

- The improved error logging will now show detailed tracebacks in DEBUG mode
- All Celery/Redis connection errors are handled gracefully (won't block login)
- Website assignment is now automatic if missing
- UserProfile creation is automatic if missing

Run the tests and share the output to get specific fixes for any remaining issues!

