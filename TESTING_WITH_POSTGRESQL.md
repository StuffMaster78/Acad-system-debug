# Testing with PostgreSQL Locally 🐘

## 🚀 Quick Start

### 1. Ensure Docker Containers are Running

```bash
# Check if containers are running
docker-compose ps

# Start if not running
docker-compose up -d
```

### 2. Run Tests with PostgreSQL

```bash
# Set TEST_DB=postgres and run tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# Or run specific test file
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py -v"

# With coverage
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --cov=. --cov-report=html -v"
```

### 3. Using Makefile

```bash
# Add to Makefile or run directly
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

---

## 🔧 Configuration

### Test Database Isolation

The test settings automatically create a **separate test database** to avoid contaminating your production database:

- **Production DB**: `writingsondo` (or your configured name)
- **Test DB**: `test_writingsondo` (automatically created)

This ensures:
- ✅ Production data is safe
- ✅ Tests run in isolation
- ✅ No data contamination

### Environment Variables

```bash
# Use PostgreSQL for tests
export TEST_DB=postgres

# Or use SQLite (faster, but limited)
export TEST_DB=sqlite
```

---

## 📋 Step-by-Step Guide

### Step 1: Verify Database Connection

```bash
# Check if PostgreSQL is accessible
docker-compose exec web python manage.py dbshell --settings=writing_system.settings_test
# Should connect to test database
```

### Step 2: Run Migrations on Test Database

```bash
# Run migrations (test database is created automatically)
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py migrate --settings=writing_system.settings_test"
```

### Step 3: Run Tests

```bash
# Run all tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# Run specific test
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py::TestUserModel::test_user_creation -v"

# Run with markers
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m unit -v"
```

---

## 🔍 Troubleshooting

### Issue 1: Database Connection Error

**Error**: `could not connect to server`

**Solution**:
```bash
# Ensure PostgreSQL container is running
docker-compose ps db

# Check database is healthy
docker-compose exec db pg_isready -U awinorick
```

### Issue 2: Permission Denied

**Error**: `permission denied to create database`

**Solution**:
```bash
# Ensure database user has CREATE DATABASE permission
docker-compose exec db psql -U awinorick -d postgres -c "ALTER USER awinorick CREATEDB;"
```

### Issue 3: Migration Dependencies

**Error**: `Migration dependencies reference nonexistent parent node`

**Solution**:
```bash
# Run migrations on test database first
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py migrate --settings=writing_system.settings_test --run-syncdb"
```

### Issue 4: Content Type Integrity Error

**Error**: `null value in column "name" of relation "django_content_type"`

**Solution**: This is fixed in `conftest.py` - it now properly creates content types. If you still see this:

```bash
# Recreate test database
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

---

## 🎯 Best Practices

### 1. Always Use Test Database

The configuration automatically creates a separate test database (`test_writingsondo`), so your production data is safe.

### 2. Clean Test Database

```bash
# Drop and recreate test database
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"
```

### 3. Run Migrations First

```bash
# Always run migrations before tests
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py migrate --settings=writing_system.settings_test && pytest -v"
```

### 4. Use Markers for Faster Tests

```bash
# Run only fast unit tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m 'unit and not slow' -v"

# Run integration tests separately
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m integration -v"
```

---

## 📊 Test Database Configuration

### Automatic Test Database Creation

When you run tests with `TEST_DB=postgres`, Django automatically:
1. Creates a test database: `test_writingsondo`
2. Runs all migrations
3. Creates content types
4. Sets up test fixtures
5. Cleans up after tests

### Manual Test Database Management

```bash
# Create test database manually
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py migrate --settings=writing_system.settings_test --run-syncdb"

# Drop test database
docker-compose exec db psql -U awinorick -d postgres -c "DROP DATABASE IF EXISTS test_writingsondo;"
```

---

## ✅ Verification

### Check Test Database is Created

```bash
# List databases
docker-compose exec db psql -U awinorick -d postgres -c "\l" | grep test
# Should show: test_writingsondo
```

### Verify Tests Use Test Database

```bash
# Run a test and check which database it uses
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py::TestUserModel::test_user_creation -v -s" | grep -i "database\|test_writingsondo"
```

---

## 🚀 Quick Commands Reference

```bash
# Run all tests with PostgreSQL
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"

# Run specific test file
docker-compose exec web bash -c "export TEST_DB=postgres && pytest tests/examples/test_example.py -v"

# Run with coverage
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --cov=. --cov-report=html -v"

# Run and create fresh database
docker-compose exec web bash -c "export TEST_DB=postgres && pytest --create-db -v"

# Run only unit tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -m unit -v"

# Run migrations first, then tests
docker-compose exec web bash -c "export TEST_DB=postgres && python manage.py migrate --settings=writing_system.settings_test && pytest -v"
```

---

## 📝 Notes

- **Test database is automatically created** - You don't need to create it manually
- **Production database is safe** - Tests use a separate `test_` prefixed database
- **Migrations run automatically** - pytest-django handles this
- **Content types are created** - Fixed in `conftest.py`

---

## 🎉 You're Ready!

Run your tests with PostgreSQL:

```bash
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

**Happy Testing! 🧪**

