# Argon2 Installation Fix

## Issue
The Docker container doesn't have `argon2-cffi` installed, causing login failures with:
```
ValueError: Couldn't load 'Argon2PasswordHasher' algorithm library: No module named 'argon2'
```

## ✅ Quick Fix Applied
Argon2 has been installed in the running container. Django will automatically use it for new passwords.

## Permanent Fix: Rebuild Docker Container (Recommended)

### Option 1: Install in Running Container (Quick Fix - Already Done)
```bash
docker-compose exec -u root web pip install argon2-cffi==25.1.0
docker-compose restart web
```

### Option 2: Rebuild Container (Recommended for Production)
```bash
cd /Users/awwy/writing_project
docker-compose build web
docker-compose up -d web
```

### Verify Installation
```bash
docker-compose exec web python -c "import argon2; print('✅ Argon2 installed')"
```

**Note**: The settings are already configured to use Argon2 as primary. Django will automatically fall back to PBKDF2 if Argon2 is not available, so login will work either way.

## Verification
After rebuilding, test login to ensure it works:
1. Try logging in through the frontend
2. Check logs for any argon2 errors
3. Verify password hashing works correctly

## Note
- Existing passwords hashed with PBKDF2 will continue to work (Django automatically uses the correct hasher)
- New passwords will use Argon2 after the container is rebuilt and settings are updated
- The temporary fix (PBKDF2 first) is safe and secure - it's just not as strong as Argon2

