# Quick Profile Settings Test Guide

## ✅ What We've Implemented

1. **Backend Endpoints:**
   - `GET /api/v1/auth/auth/user/` - Get current user profile (reads from database)
   - `PATCH /api/v1/auth/auth/user/` - Update user profile (saves to database)
   - `GET /api/v1/users/users/profile-update-requests/` - Get pending update requests

2. **Frontend Component:**
   - `writing_system_frontend/src/views/account/Settings.vue` - Complete profile settings page with all fields
   - `writing_system_frontend/src/api/auth.js` - Updated with `getCurrentUser()` and `updateProfile()` methods

3. **Backend Serializers:**
   - Enhanced to include UserProfile fields (phone_number, bio, avatar, country, state)
   - Works for all user roles (Client, Writer, Editor, Support, Admin, Superadmin)

## 🧪 Manual Testing Steps

### Step 1: Login and Get Token

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@client.local",
    "password": "testpass123",
    "remember_me": false
  }'
```

**Save the `access_token` from response.**

### Step 2: Get Current Profile

```bash
# Replace YOUR_TOKEN with the access token
TOKEN="YOUR_TOKEN"

curl "http://localhost:8000/api/v1/auth/auth/user/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Expected:** Profile data with all fields (email, username, first_name, last_name, phone_number, bio, country, state, avatar_url, etc.)

### Step 3: Update Profile

```bash
curl -X PATCH "http://localhost:8000/api/v1/auth/auth/user/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "bio": "This is my updated bio",
    "country": "US",
    "state": "California"
  }' | python3 -m json.tool
```

**Expected:** 
```json
{
  "message": "Profile updated successfully.",
  "user": {
    "id": 15,
    "email": "test@client.local",
    "username": "test_client",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "bio": "This is my updated bio",
    "country": "US",
    "state": "California",
    ...
  }
}
```

### Step 4: Verify Update Persisted

```bash
# Get profile again
curl "http://localhost:8000/api/v1/auth/auth/user/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Verify:** All updated fields should show the new values.

### Step 5: Get Profile Update Requests

```bash
curl "http://localhost:8000/api/v1/users/users/profile-update-requests/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Expected:**
```json
{
  "pending_requests": []
}
```

## 🎨 Frontend Testing

1. **Start Frontend:**
   ```bash
   cd /Users/awwy/writing_system_frontend
   npm run dev
   ```
   
   **Note:** The frontend is located in `writing_system_frontend` directory (separate from the backend).

2. **Access Settings:**
   - Go to: `http://localhost:5173` or `http://localhost:3000` (check your Vite dev server output)
   - Login with: `test@client.local` / `testpass123`
   - Navigate to: `/account/settings`

3. **Test Profile Tab:**
   - ✅ All fields should be visible and populated:
     - Email (disabled)
     - Username
     - First Name
     - Last Name
     - Phone Number
     - Bio (with character counter)
     - Country
     - State/Province
     - Avatar (if available)
   - ✅ Update any field
   - ✅ Click "Save Changes"
   - ✅ See success message
   - ✅ Refresh page - data should persist
   - ✅ Loading state shows while fetching profile

## ✅ Success Criteria

- [x] Profile data loads from database
- [x] All fields are displayed (email, username, first_name, last_name, phone, bio, country, state, avatar)
- [x] Profile updates save to database
- [x] Updates persist after page refresh
- [x] No 500 errors
- [x] Proper error handling
- [x] Loading states work correctly
- [x] Avatar images display correctly
- [x] Form validation and character limits work

## 🔍 What to Check

1. **Backend:**
   - Profile data includes UserProfile fields
   - Updates save to both User and UserProfile models
   - Response includes updated data

2. **Frontend:**
   - Form loads with current data from database
   - All fields are editable (except email)
   - Success/error messages appear
   - Data persists after refresh
   - Loading indicator shows while fetching profile
   - Avatar URL is constructed correctly (handles relative/absolute paths)
   - Bio character counter works (500 char limit)
   - Responsive design works on mobile devices

## 📝 Notes

- **Frontend Location:** The frontend code is in `/Users/awwy/writing_system_frontend` (separate directory from backend)
- **Backend Endpoints:**
  - The endpoint path is `/api/v1/auth/auth/user/` (not `/api/v1/auth/user/`)
  - Profile update requests endpoint is at `/api/v1/users/users/profile-update-requests/`
- **Authentication:** All endpoints require authentication (Bearer token)
- **UserProfile:** UserProfile fields are automatically created if they don't exist
- **API Methods:** The frontend uses `authApi.getCurrentUser()` and `authApi.updateProfile()` from `/src/api/auth.js`
- **Response Handling:** The frontend handles both nested (Client/Writer/Editor/Support) and flat (Admin/Superadmin) response structures

