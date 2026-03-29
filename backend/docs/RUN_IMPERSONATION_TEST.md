# How to Run Impersonation Test

## Prerequisites

1. **Start the Django server:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for server to be ready:**
   ```bash
   # Check server status
   docker-compose ps
   
   # Check server logs
   docker-compose logs web | tail -20
   
   # Test if server is responding
   curl http://localhost:8000/api/v1/
   ```

## Run the Test

### Option 1: Run inside Docker container (Recommended)
```bash
docker-compose exec web python test_impersonation.py
```

### Option 2: Run from host (requires server to be accessible)
```bash
# Make sure server is running and accessible
python3 test_impersonation.py
```

## Troubleshooting

### Connection Refused Error
If you see:
```
Connection refused: [Errno 111]
```

**Solution:**
1. Make sure Docker containers are running:
   ```bash
   docker-compose ps
   ```

2. If containers are not running, start them:
   ```bash
   docker-compose up -d
   ```

3. Wait a few seconds for the server to start, then check:
   ```bash
   docker-compose logs web | tail -20
   ```

4. Test server connectivity:
   ```bash
   curl http://localhost:8000/api/v1/
   ```

### Server Not Starting
If the server fails to start:
```bash
# Check logs
docker-compose logs web

# Rebuild if needed
docker-compose down
docker-compose build web
docker-compose up -d
```

### Test Users Not Found
The test will automatically create test users if they don't exist:
- `test_superadmin` (role: superadmin)
- `test_client` (role: client)

Make sure you have at least one active website in the database for users to be assigned to.

## Expected Output

You should see:
```
============================================================
  IMPERSONATION TESTING
============================================================

▶ Step 1: Setting up test users
✅ Using existing superadmin: test_superadmin (ID: 5)
✅ Using existing client: Awwyno (ID: 1)

▶ Step 2: Logging in as superadmin
✅ Logged in as superadmin. Token: ...

▶ Step 3: Creating impersonation token
✅ Created impersonation token: ...

▶ Step 4: Checking impersonation status (before)
✅ Impersonation status: False

▶ Step 5: Starting impersonation
✅ Started impersonation. Client token: ...

▶ Step 6: Checking impersonation status (during)
✅ Impersonation status: True

▶ Step 7: Verifying client session
✅ Current user: test_client (Role: client)

▶ Step 8: Ending impersonation
✅ Ended impersonation. Admin token restored: ...

▶ Step 9: Verifying admin session restored
✅ Current user: test_superadmin (Role: superadmin)

▶ Step 10: Checking impersonation logs
✅ Found X impersonation log entries

============================================================
ALL TESTS PASSED! ✅
============================================================
```

## Manual Testing

If you prefer to test manually using curl or API client, see `test_impersonation_manual.md`.

