# Test Users and URLs

## 🔐 Test User Credentials

**All users use the same password for easy testing:** `testpass123`

| Role | Email | Username | Password |
|------|-------|----------|----------|
| **Admin** | `test@admin.local` | `test_admin` | `testpass123` |
| **Superadmin** | `test@superadmin.local` | `test_superadmin` | `testpass123` |
| **Editor** | `test@editor.local` | `test_editor` | `testpass123` |
| **Writer** | `test@writer.local` | `test_writer` | `testpass123` |
| **Support** | `test@support.local` | `test_support` | `testpass123` |
| **Client** | `test@client.local` | `test_client` | `testpass123` |

---

## 🌐 Test URLs

### Frontend Login
```
http://localhost:5173/login
http://localhost:5175/login
```

### Dashboard URLs (After Login)

All roles will see their role-specific dashboard at:
```
http://localhost:5173/dashboard
http://localhost:5175/dashboard
```

### Quick Test Links

**Admin Dashboard:**
1. Go to: `http://localhost:5173/login`
2. Login with: `test@admin.local` / `testpass123`
3. You'll be redirected to: `http://localhost:5173/dashboard`

**Superadmin Dashboard:**
1. Go to: `http://localhost:5173/login`
2. Login with: `test@superadmin.local` / `testpass123`
3. You'll be redirected to: `http://localhost:5173/dashboard`

**Editor Dashboard:**
1. Go to: `http://localhost:5173/login`
2. Login with: `test@editor.local` / `testpass123`
3. You'll be redirected to: `http://localhost:5173/dashboard`

**Writer Dashboard:**
1. Go to: `http://localhost:5173/login`
2. Login with: `test@writer.local` / `testpass123`
3. You'll be redirected to: `http://localhost:5173/dashboard`

**Support Dashboard:**
1. Go to: `http://localhost:5173/login`
2. Login with: `test@support.local` / `testpass123`
3. You'll be redirected to: `http://localhost:5173/dashboard`

**Client Dashboard:**
1. Go to: `http://localhost:5173/login`
2. Login with: `test@client.local` / `testpass123`
3. You'll be redirected to: `http://localhost:5173/dashboard`

---

## 📋 How to Create Test Users

### Using Docker (Recommended)
```bash
cd /Users/awwy/writing_system_backend
bash create_test_users_docker.sh
```

### Alternative: Using Django Shell
```bash
docker-compose exec web python manage.py shell < create_test_users.py
```

### Manual Creation
If you prefer to create users manually via Django admin:
1. Go to: `http://localhost:8000/admin/`
2. Login with superadmin credentials
3. Navigate to Users section
4. Create users with the credentials above

---

## 🎯 What Each Dashboard Shows

### Admin Dashboard
- Summary stats (Total Orders, Revenue, Paid/Unpaid Orders)
- Charts (Yearly Orders, Earnings, Payment Status, Service Revenue)
- Monthly Orders Chart
- Quick actions (Orders, Users, Payments, Websites)
- Place Order button

### Superadmin Dashboard
- Same as Admin dashboard
- Additional superadmin-only features
- Multi-tenant management

### Editor Dashboard
- Stats: Assigned Tasks, Completed Reviews, Pending Tasks, Average Score
- Quick actions: My Tasks, Available Tasks, Performance
- Recent Tasks section

### Writer Dashboard
- Stats: Active Orders, Completed Orders, Pending Reviews, Earnings
- Quick actions: My Orders, Available Orders, Badges & Performance
- Recent Orders section

### Support Dashboard
- Stats: Open Tickets, Resolved Today, Pending Orders, Escalations
- Quick actions: Tickets, Order Management, Escalations
- Recent Tickets section

### Client Dashboard
- Wallet balance, Spend, Orders overview
- Quick actions: Start Order Wizard, My Orders, Wallet
- Recent Orders
- Notifications and Messages

---

## ✅ Verification

After running the script, verify users were created:
```bash
docker-compose exec web python manage.py shell -c "from users.models import User; print('\n'.join([f'{u.email} - {u.role}' for u in User.objects.filter(email__startswith='test@')]))"
```

---

## 📝 Notes

- All users are created with `is_active=True`
- Users with roles `writer`, `client`, and `admin` are assigned to a default "Test Website"
- The script will update existing users if they already exist
- All users share the same password (`testpass123`) for convenience during testing
- Celery connection errors during user creation are expected (emails are queued but Redis might not be running)

---

## 🚀 Quick Start

1. **Create users:**
   ```bash
   bash create_test_users_docker.sh
   ```

2. **Start frontend:**
   ```bash
   cd /Users/awwy/writing_system_frontend
   npm run dev
   ```

3. **Test login:**
   - Open: `http://localhost:5173/login`
   - Use any test user credentials from the table above
   - You'll see the role-specific dashboard!

