# Running Tests with PostgreSQL Locally 🐘

## ✅ Quick Start

### Basic Command

```bash
# Run all tests with PostgreSQL
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# Run specific test
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py -v"

# Run with fresh database
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

---

## 🔧 Setup

### 1. Ensure PostgreSQL is Running

```bash
# Check PostgreSQL container
docker-compose ps db

# Should show: Up and healthy
```

### 2. Verify Database Access

```bash
# Test database connection
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py dbshell --settings=writing_system.settings_test"
```

### 3. Run Tests

```bash
# Simple test run
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

---

## 📋 How It Works

### Test Database Isolation

When you run tests with `TEST_DB=postgres`:

1. **Django automatically creates** a separate test database: `test_writingsondo`
2. **Runs all migrations** on the test database
3. **Creates content types** properly (fixed in `conftest.py`)
4. **Runs your tests** in isolation
5. **Cleans up** after tests complete

**Your production database (`writingsondo`) is never touched!**

---

## 🎯 Common Commands

### Run All Tests

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

### Run Specific Test File

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py -v"
```

### Run Specific Test

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py::TestUserModel::test_user_creation -v"
```

### Run with Coverage

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --cov=. --cov-report=html -v"
```

### Run with Fresh Database

```bash
# Drops and recreates test database
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

### Run by Markers

```bash
# Unit tests only
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m unit -v"

# Integration tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m integration -v"

# Exclude slow tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m 'not slow' -v"
```

---

## 🔍 Troubleshooting

### Issue: Content Type Integrity Error

**Error**: `null value in column "name" of relation "django_content_type"`

**Solution**: This is now fixed in `conftest.py`. If you still see it:

```bash
# Drop test database and recreate
docker-compose exec db psql -U awinorick -d postgres -c "DROP DATABASE IF EXISTS test_writingsondo;"
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

### Issue: Migration Dependencies

**Error**: `Migration dependencies reference nonexistent parent node`

**Solution**:
```bash
# Run migrations manually first
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py migrate --settings=writing_system.settings_test"
```

### Issue: Permission Denied

**Error**: `permission denied to create database`

**Solution**:
```bash
# Grant CREATE DATABASE permission
docker-compose exec db psql -U awinorick -d postgres -c "ALTER USER awinorick CREATEDB;"
```

### Issue: Database Connection Failed

**Error**: `could not connect to server`

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps db

# Check health
docker-compose exec db pg_isready -U awinorick
```

---

## ✅ Verification

### Check Test Database is Created

```bash
# List all databases
docker-compose exec db psql -U awinorick -d postgres -c "\l" | grep test
# Should show: test_writingsondo
```

### Verify Test Database Configuration

```bash
# Check which database tests will use
docker-compose exec web bash -c "export TEST_DB=postgres && python -c 'import os; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"writing_system.settings_test\"); import django; django.setup(); from django.conf import settings; print(\"Test DB:\", settings.DATABASES[\"default\"].get(\"TEST\", {}).get(\"NAME\"))'"
# Should show: test_writingsondo
```

---

## 📊 Test Database Details

- **Production DB**: `writingsondo` (never touched by tests)
- **Test DB**: `test_writingsondo` (automatically created)
- **Isolation**: Complete - tests never affect production data
- **Cleanup**: Test database persists between runs (faster)
- **Fresh Start**: Use `--create-db` flag to recreate

---

## 🚀 Best Practices

1. **Always use `TEST_DB=postgres`** when you want PostgreSQL tests
2. **Use `--create-db`** if you suspect database corruption
3. **Run migrations first** if you see migration errors
4. **Check test database exists** before running large test suites
5. **Use markers** to run specific test categories

---

## 📝 Example Workflow

```bash
# 1. Start containers
docker-compose up -d

# 2. Verify PostgreSQL is running
docker-compose ps db

# 3. Run tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# 4. Check results
# Tests should pass with PostgreSQL!
```

---

## 🎉 You're Ready!

Your tests are now configured to work with PostgreSQL. Just run:

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

**The test database (`test_writingsondo`) is automatically created and isolated from your production database!**

