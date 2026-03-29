# Profile Settings Testing Guide

This guide provides step-by-step instructions to test the profile settings functionality.

## Prerequisites

1. **Backend running**: `python3 manage.py runserver 0.0.0.0:8000`
2. **Frontend running** (optional): `cd frontend && npm run dev`
3. **Database migrated**: `python3 manage.py migrate`

## Quick Test Script

If you have a test user, you can use this script:
```bash
python3 test_profile_settings.py
```

## Manual Testing with cURL

### Step 1: Login and Get Token

```bash
# Login to get access token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "password": "your_password",
    "remember_me": false
  }'
```

**Save the `access_token` from the response.**

### Step 2: Get Current User Profile

```bash
# Replace YOUR_TOKEN with the access token from Step 1
TOKEN="YOUR_TOKEN"

curl http://localhost:8000/api/v1/auth/user/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "bio": "User bio",
  "avatar": "avatars/universal.png",
  "avatar_url": "http://localhost:8000/media/avatars/universal.png",
  "country": "US",
  "state": "California",
  "role": "client",
  "is_suspended": false,
  "is_on_probation": false,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

### Step 3: Update User Profile

```bash
# Update profile fields
curl -X PATCH http://localhost:8000/api/v1/auth/user/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+1987654321",
    "bio": "Updated bio text",
    "country": "CA",
    "state": "Ontario"
  }'
```

**Expected Response:**
```json
{
  "message": "Profile updated successfully.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "phone_number": "+1987654321",
    "bio": "Updated bio text",
    "country": "CA",
    "state": "Ontario",
    ...
  }
}
```

### Step 4: Verify Profile Update

```bash
# Get profile again to verify update persisted
curl http://localhost:8000/api/v1/auth/user/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Verify that the updated fields match what you sent in Step 3.**

### Step 5: Get Profile Update Requests

```bash
# Get pending profile update requests
curl http://localhost:8000/api/v1/users/profile-update-requests/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "pending_requests": []
}
```

## Frontend Testing

### Step 1: Access Settings Page

1. Open browser to `http://localhost:3000` (or your frontend URL)
2. Login with your credentials
3. Navigate to `/account/settings` or click "Account Settings" in the dashboard

### Step 2: View Profile Tab

1. Click on the "Profile" tab
2. **Expected**: You should see:
   - Email (disabled)
   - Username field
   - First Name field
   - Last Name field
   - Phone Number field
   - Bio textarea
   - Country field
   - State/Province field
   - Avatar image (if available)

### Step 3: Update Profile

1. Fill in or modify the form fields:
   - Change first name to "Test"
   - Change last name to "User"
   - Add phone number: "+1234567890"
   - Add bio: "This is a test bio"
   - Add country: "US"
   - Add state: "California"

2. Click "Save Changes"

3. **Expected**:
   - Success message appears: "Profile updated successfully!"
   - Form fields show the updated values
   - No error messages

### Step 4: Verify Database Update

1. Open browser console (F12)
2. Check Network tab for the PATCH request to `/api/v1/auth/user/`
3. Verify response status is 200
4. Verify response contains updated user data

### Step 5: Refresh and Verify Persistence

1. Refresh the page (F5)
2. **Expected**: All updated fields should still show the new values
3. This confirms data is persisted in the database

## Testing Different User Roles

### Test as Client
```bash
# Login as client user
# Profile should include client-specific fields
```

### Test as Writer
```bash
# Login as writer user
# Profile should include writer-specific fields (bio, etc.)
```

### Test as Admin
```bash
# Login as admin user
# Profile should show admin profile structure
```

## Error Testing

### Test Invalid Data

```bash
# Try updating with invalid phone number
curl -X PATCH http://localhost:8000/api/v1/auth/user/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "invalid"
  }'
```

**Expected**: Should handle validation gracefully

### Test Unauthorized Access

```bash
# Try accessing without token
curl http://localhost:8000/api/v1/auth/user/
```

**Expected**: 401 Unauthorized

### Test Invalid Token

```bash
# Try with invalid token
curl http://localhost:8000/api/v1/auth/user/ \
  -H "Authorization: Bearer invalid_token"
```

**Expected**: 401 Unauthorized

## Checklist

- [ ] GET `/api/v1/auth/user/` returns profile data
- [ ] Profile data includes all expected fields
- [ ] PATCH `/api/v1/auth/user/` updates profile successfully
- [ ] Updated fields persist in database
- [ ] Frontend displays profile data correctly
- [ ] Frontend form updates profile successfully
- [ ] Success message appears after update
- [ ] Error handling works for invalid data
- [ ] Unauthorized access is blocked
- [ ] Profile update requests endpoint works

## Troubleshooting

### Issue: 500 Internal Server Error

**Check:**
1. Server logs: `python3 manage.py runserver` output
2. Database connection
3. User has UserProfile created

**Fix:**
```bash
# Create UserProfile if missing
python3 manage.py shell
```
```python
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()
user = User.objects.get(email='your_email@example.com')
UserProfile.objects.get_or_create(user=user)
```

### Issue: Fields Not Updating

**Check:**
1. Verify request is being sent correctly
2. Check server logs for errors
3. Verify UserProfile exists

### Issue: Avatar Not Displaying

**Check:**
1. Avatar URL is correct
2. Media files are being served
3. File exists in media directory

## Success Criteria

✅ All profile fields can be read from database
✅ All profile fields can be updated
✅ Updates persist in database
✅ Frontend displays all fields correctly
✅ Frontend can update all fields
✅ Error handling works correctly
✅ No 500 errors occur

