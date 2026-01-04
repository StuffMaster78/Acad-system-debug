# How to Test with PostgreSQL Locally 🐘

## ✅ Configuration

Your test setup now reads credentials from the `.env` file automatically!

---

## 🚀 Quick Start

### Run Tests with PostgreSQL

```bash
# Simple command - uses credentials from .env file
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# Run specific test
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py -v"

# With fresh database
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

---

## 🔧 How It Works

### Credentials from .env File

The test settings now read from your `.env` file:
- `POSTGRES_DB_NAME` - Database name
- `POSTGRES_USER_NAME` - Database user
- `POSTGRES_PASSWORD` - Database password
- `DB_HOST` - Database host (defaults to "db")
- `DB_PORT` - Database port (defaults to 5432)

### Test Database Isolation

- **Production DB**: Uses name from `.env` (e.g., `writingsondo`)
- **Test DB**: Automatically creates `test_writingsondo`
- **Isolation**: Complete - production data is never touched

---

## 📋 Step-by-Step

### 1. Ensure .env File Exists

```bash
# Check .env file exists
ls -la backend/.env

# Should contain:
# POSTGRES_DB_NAME=writingsondo
# POSTGRES_USER_NAME=awinorick
# POSTGRES_PASSWORD=Nyakach2030
# DB_HOST=db
# DB_PORT=5432
```

### 2. Start Docker Containers

```bash
docker-compose up -d
```

### 3. Run Tests

```bash
# Run all tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# Run specific test file
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py -v"

# Run with coverage
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --cov=. --cov-report=html -v"
```

---

## 🎯 Common Commands

### Basic Test Run
```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

### Fresh Database
```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

### Specific Test
```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py::TestUserModel::test_user_creation -v"
```

### With Markers
```bash
# Unit tests only
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m unit -v"

# Integration tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m integration -v"
```

---

## 🔍 Troubleshooting

### Issue: Environment Variables Not Loading

**If credentials aren't being read from .env:**

```bash
# Verify .env file is in backend directory
ls -la backend/.env

# Check if variables are set in Docker
docker-compose exec web env | grep POSTGRES
```

### Issue: Database Connection Failed

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps db

# Test connection
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py dbshell --settings=writing_system.settings_test"
```

### Issue: Content Type Error

**If you see**: `null value in column "name" of relation "django_content_type"`

**Solution**: This is now fixed in `conftest.py`. If it persists:

```bash
# Drop and recreate test database
docker-compose exec db psql -U awinorick -d postgres -c "DROP DATABASE IF EXISTS test_writingsondo;"
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

---

## ✅ Verification

### Check Credentials are Loaded

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && python -c \"import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings_test'); import django; django.setup(); from django.conf import settings; db = settings.DATABASES['default']; print('Using DB:', db['NAME']); print('User:', db['USER']); print('Host:', db['HOST'])\""
```

### Check Test Database is Created

```bash
docker-compose exec db psql -U awinorick -d postgres -c "\l" | grep test
# Should show: test_writingsondo
```

---

## 📝 What's Configured

1. ✅ **Test settings read from .env** - Uses your actual credentials
2. ✅ **Test database isolation** - Creates `test_writingsondo` separate from production
3. ✅ **Content type fixes** - Corrupted content types are cleaned up
4. ✅ **Migrations run automatically** - On test database
5. ✅ **SyntaxWarnings fixed** - All 18 warnings eliminated

---

## 🎉 Ready to Test!

Your PostgreSQL test setup is complete and reads from `.env`:

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

**The test database is automatically created and isolated from production!** ✅

