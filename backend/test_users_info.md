# Test Users Credentials

All test users use the same password for easy testing: **`testpass123`**

## Test Users

### Admin
- **Email:** `test@admin.local`
- **Username:** `test_admin`
- **Password:** `testpass123`
- **Role:** `admin`

### Superadmin
- **Email:** `test@superadmin.local`
- **Username:** `test_superadmin`
- **Password:** `testpass123`
- **Role:** `superadmin`

### Editor
- **Email:** `test@editor.local`
- **Username:** `test_editor`
- **Password:** `testpass123`
- **Role:** `editor`

### Writer
- **Email:** `test@writer.local`
- **Username:** `test_writer`
- **Password:** `testpass123`
- **Role:** `writer`

### Support
- **Email:** `test@support.local`
- **Username:** `test_support`
- **Password:** `testpass123`
- **Role:** `support`

### Client
- **Email:** `test@client.local`
- **Username:** `test_client`
- **Password:** `testpass123`
- **Role:** `client`

---

## Test URLs

### Frontend URLs

**Login Page:**
```
http://localhost:5173/login
http://localhost:5175/login
```

**Dashboard URLs (after login):**
```
http://localhost:5173/dashboard
http://localhost:5175/dashboard
```

### Direct Dashboard URLs (Role-Specific)

**Admin Dashboard:**
```
http://localhost:5173/dashboard  (Login as test@admin.local)
```

**Superadmin Dashboard:**
```
http://localhost:5173/dashboard  (Login as test@superadmin.local)
```

**Editor Dashboard:**
```
http://localhost:5173/dashboard  (Login as test@editor.local)
```

**Writer Dashboard:**
```
http://localhost:5173/dashboard  (Login as test@writer.local)
```

**Support Dashboard:**
```
http://localhost:5173/dashboard  (Login as test@support.local)
```

**Client Dashboard:**
```
http://localhost:5173/dashboard  (Login as test@client.local)
```

---

## How to Create Test Users

### Option 1: Using Django Shell
```bash
cd /Users/awwy/writing_system_backend
python manage.py shell < create_test_users.py
```

### Option 2: Using Docker
```bash
docker-compose exec web python manage.py shell < create_test_users.py
```

### Option 3: Direct Python Execution
```bash
cd /Users/awwy/writing_system_backend
python create_test_users.py
```

---

## Quick Login Test

1. Open frontend: `http://localhost:5173/login` or `http://localhost:5175/login`
2. Enter email: `test@admin.local` (or any role email above)
3. Enter password: `testpass123`
4. Click Login
5. You'll be redirected to the role-specific dashboard

---

## Notes

- All users are created with `is_active=True`
- Users with roles `writer`, `client`, and `admin` are assigned to a default "Test Website"
- The script will update existing users if they already exist
- All users share the same password for convenience during testing

