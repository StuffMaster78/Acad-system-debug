# Testing with PostgreSQL - Complete Guide 🐘

## ✅ Configuration Complete

Your test setup is now configured to work with PostgreSQL. Here's how to use it:

---

## 🚀 Quick Start

### Run Tests with PostgreSQL

```bash
# Basic command
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# With fresh database
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"

# Specific test
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py -v"
```

---

## 🔧 How It Works

### Test Database Isolation

1. **Automatic Test Database Creation**
   - Django creates: `test_writingsondo` (separate from production)
   - Production DB (`writingsondo`) is never touched
   - Test database is automatically cleaned up

2. **Migrations Run Automatically**
   - All migrations run on test database
   - Content types are created properly
   - Corrupted content types are cleaned up

3. **Isolation Guaranteed**
   - Each test run uses the test database
   - No contamination of production data
   - Safe to run anytime

---

## 📋 Step-by-Step

### Step 1: Start Docker Containers

```bash
docker-compose up -d
```

### Step 2: Verify PostgreSQL is Running

```bash
docker-compose ps db
# Should show: Up and healthy
```

### Step 3: Run Tests

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

### Run All Tests
```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

### Run Specific Test
```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py::TestUserModel::test_user_creation -v"
```

### Run with Fresh Database
```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

### Run by Markers
```bash
# Unit tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m unit -v"

# Integration tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m integration -v"

# Exclude slow tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m 'not slow' -v"
```

### With Coverage
```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --cov=. --cov-report=html --cov-report=term -v"
```

---

## 🔍 Troubleshooting

### Issue: Content Type Integrity Error

**If you see**: `null value in column "name" of relation "django_content_type"`

**Solution**: This is now fixed in `conftest.py`. If it persists:

```bash
# Drop and recreate test database
docker-compose exec db psql -U awinorick -d postgres -c "DROP DATABASE IF EXISTS test_writingsondo;"
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

### Issue: Migration Dependencies

**Solution**:
```bash
# Run migrations manually first
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py migrate --settings=writing_system.settings_test"
```

### Issue: Permission Denied

**Solution**:
```bash
# Grant CREATE DATABASE permission
docker-compose exec db psql -U awinorick -d postgres -c "ALTER USER awinorick CREATEDB;"
```

---

## ✅ Verification

### Check Test Database Exists

```bash
docker-compose exec db psql -U awinorick -d postgres -c "\l" | grep test
# Should show: test_writingsondo
```

### Verify Configuration

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && python -c 'import os; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"writing_system.settings_test\"); import django; django.setup(); from django.conf import settings; db = settings.DATABASES[\"default\"]; print(f\"Engine: {db[\"ENGINE\"]}\"); print(f\"Name: {db[\"NAME\"]}\"); print(f\"Test Name: {db.get(\"TEST\", {}).get(\"NAME\", \"Not set\")}\")'"
```

---

## 📊 What's Fixed

1. ✅ **Test Database Configuration** - Properly configured in `settings_test.py`
2. ✅ **Content Type Cleanup** - Fixed in `conftest.py` to remove corrupted content types
3. ✅ **Database Isolation** - Test database (`test_writingsondo`) is separate from production
4. ✅ **Migrations** - Run automatically on test database
5. ✅ **SyntaxWarnings** - All 18 warnings fixed

---

## 🎯 Best Practices

1. **Always use `TEST_DB=postgres`** when you want PostgreSQL tests
2. **Use `--create-db`** if you suspect database issues
3. **Check test database exists** before running large test suites
4. **Use markers** to run specific test categories
5. **Production database is safe** - tests never touch it

---

## 📝 Quick Reference

```bash
# Run tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# Fresh database
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"

# Specific test
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py::TestUserModel::test_user_creation -v"

# With coverage
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --cov=. --cov-report=html -v"
```

---

## 🎉 Ready to Test!

Your PostgreSQL test setup is complete. Run:

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

**The test database is automatically created and isolated from production!** ✅

