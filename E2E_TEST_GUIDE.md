# End-to-End Testing Guide

This guide provides step-by-step instructions to test the complete user journeys for both frontend and backend.

## Prerequisites

1. **Backend running**: `python3 manage.py runserver 0.0.0.0:8000`
2. **Frontend running**: `cd writing_system_frontend && npm run dev`
3. **Database migrated**: `python3 manage.py migrate`

## Quick Test Script

Run the automated test script:
```bash
cd /Users/awwy/writing_system_backend
python3 test_e2e.py
```

## Manual Testing Checklist

### 1. Backend Health Checks

#### Test API Root
```bash
curl http://localhost:8000/api/v1/
```
**Expected**: JSON response with API information

#### Test Swagger Documentation
```bash
curl http://localhost:8000/api/v1/docs/swagger/
```
**Expected**: Swagger UI loads successfully

#### Test Django System Checks
```bash
python3 manage.py check
```
**Expected**: No errors, warnings are silenced

### 2. User Registration Flow

#### Test Registration Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```
**Expected**: 
- Status: 201 Created
- Response: `{"message": "Registration successful...", "user_id": ..., "email": "test@example.com"}`

#### Verify User in Database
```bash
python3 manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='test@example.com')
print(f"User created: {user.username} ({user.email}) - Role: {user.role}")
print(f"Website: {user.website}")
```

### 3. User Login Flow

#### Test Login Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "remember_me": false
  }'
```
**Expected**:
- Status: 200 OK
- Response contains:
  - `access_token` or `access`
  - `refresh_token` or `refresh`
  - `user` object with profile data

### 4. Protected Endpoint Access

#### Test Profile Endpoint (requires token)
```bash
# First, get token from login response above
TOKEN="your_access_token_here"

curl http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: 
- Status: 200 OK
- Response contains user profile data

### 5. Frontend Testing

#### Test Frontend Accessibility
1. Open browser to `http://localhost:5173` (or `http://localhost:5174`)
2. **Expected**: Vue.js app loads successfully

#### Test Registration Page
1. Navigate to `/signup`
2. Fill in registration form:
   - Username
   - Email
   - Password (min 8 characters)
   - Confirm Password
   - Accept Terms
3. Click "Sign Up"
4. **Expected**: 
   - Success message displayed
   - Redirects to login page after 1.5 seconds
   - User created in database

#### Test Login Page
1. Navigate to `/login`
2. Enter credentials from registration
3. Click "Sign In"
4. **Expected**:
   - Redirects to dashboard
   - Token stored in localStorage
   - User data displayed

#### Test Dashboard
1. After login, verify dashboard loads
2. **Expected**:
   - User role-based navigation visible
   - Dashboard stats display (if applicable)
   - No console errors

#### Test Protected Routes
1. Try accessing `/dashboard`, `/orders`, `/profile`
2. **Expected**: All accessible when logged in

#### Test Logout
1. Click logout button
2. **Expected**:
   - Redirects to login page
   - Token removed from localStorage
   - Cannot access protected routes

### 6. Admin Panel Testing

#### Test Admin Access
1. Navigate to `http://localhost:8000/admin`
2. Login with admin/superadmin credentials
3. **Expected**:
   - Admin panel loads
   - Can see all models
   - Can create/edit users, orders, etc.

#### Test User Creation from Admin
1. Go to Users → Add User
2. Create a new user (client/writer)
3. **Expected**:
   - User created successfully
   - Website auto-assigned if client/writer
   - Profile created automatically

### 7. API Endpoint Testing

#### Test Orders Endpoint
```bash
curl http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: List of orders (empty array if none)

#### Test Users Endpoint
```bash
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: User data

### 8. Error Handling Tests

#### Test Invalid Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@example.com",
    "password": "wrongpassword"
  }'
```
**Expected**: 
- Status: 400 Bad Request
- Error message about invalid credentials

#### Test Unauthorized Access
```bash
curl http://localhost:8000/api/v1/users/profile/
```
**Expected**: 
- Status: 401 Unauthorized
- Error message about authentication required

#### Test Invalid Token
```bash
curl http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer invalid_token"
```
**Expected**: 
- Status: 401 Unauthorized
- Error message about invalid token

### 9. Database Integrity Tests

#### Check Data Relationships
```python
python3 manage.py shell
```
```python
from django.contrib.auth import get_user_model
from client_management.models import ClientProfile
from writer_management.models.profile import WriterProfile
from websites.models import Website

User = get_user_model()

# Check users have websites
users_without_website = User.objects.filter(
    role__in=['client', 'writer'],
    website__isnull=True
)
print(f"Users without website: {users_without_website.count()}")

# Check profiles exist
clients = ClientProfile.objects.count()
writers = WriterProfile.objects.count()
print(f"Client profiles: {clients}")
print(f"Writer profiles: {writers}")
```

### 10. Performance Tests

#### Test Response Times
```bash
time curl -s http://localhost:8000/api/v1/ > /dev/null
```
**Expected**: < 1 second response time

#### Test Concurrent Requests
```bash
for i in {1..10}; do
  curl -s http://localhost:8000/api/v1/ > /dev/null &
done
wait
```
**Expected**: All requests complete successfully

## Common Issues & Solutions

### Backend Not Running
**Symptom**: Connection refused errors
**Solution**: 
```bash
cd /Users/awwy/writing_system_backend
python3 manage.py runserver 0.0.0.0:8000
```

### Frontend Not Running
**Symptom**: Cannot access http://localhost:5173
**Solution**:
```bash
cd /Users/awwy/writing_system_frontend
npm run dev
```

### CORS Errors
**Symptom**: Frontend cannot connect to backend
**Solution**: Check `CORS_ALLOWED_ORIGINS` in `settings.py` includes frontend URL

### Database Migration Issues
**Symptom**: ProgrammingError about missing columns
**Solution**:
```bash
python3 manage.py migrate
```

### Missing Website for User
**Symptom**: "Clients and writers must be assigned to a website"
**Solution**: 
- Ensure at least one active website exists
- Website is auto-assigned on user creation

## Test Results Summary

After running all tests, document:

- ✅ **Passed Tests**: List of successful tests
- ❌ **Failed Tests**: List of failed tests with error messages
- ⚠️ **Warnings**: Any warnings or issues that need attention
- 📝 **Notes**: Any observations or improvements needed

## Next Steps

1. Fix any failing tests
2. Address warnings
3. Optimize performance issues
4. Document any additional test cases needed

