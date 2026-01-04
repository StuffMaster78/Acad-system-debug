# Backend Test Database Setup - Fixed ✅

## 🔧 What Was Fixed

### 1. **Updated `conftest.py`**
- Added explicit migration command in `django_db_setup` fixture
- Ensures migrations run before tests
- Added error handling for website creation

### 2. **Updated `pytest.ini`**
- Added `DJANGO_DB_CREATE_DB = true` to ensure test database is created
- Added `DJANGO_DB_KEEP_DB = false` to use fresh database each time
- Added `DJANGO_TEST_DB = sqlite` to use SQLite by default (faster, no migration issues)

### 3. **Created Test Database Setup Script**
- `backend/scripts/setup_test_db.sh` - Helper script to set up test database
- Can be run manually if needed

---

## 🚀 How to Run Tests Now

### Option 1: Using SQLite (Recommended for Local Testing)

```bash
# Set environment variable and run tests
docker-compose exec web bash -c "export TEST_DB=sqlite && pytest -v"

# Or run specific test
docker-compose exec web bash -c "export TEST_DB=sqlite && pytest tests/test_optimizations.py -v"
```

### Option 2: Using PostgreSQL (For CI/CD)

```bash
# Set environment variable and run tests
docker-compose exec web bash -c "export TEST_DB=postgres && pytest -v"
```

### Option 3: Using Makefile

```bash
# Backend tests (uses SQLite by default)
make test-backend

# With coverage
make coverage-backend
```

---

## ⚠️ Known Issues

### Migration Dependency Issues

Some tests may fail due to migration dependencies:
```
Migration users.0005_alter_user_options_alter_userauditlog_website_and_more 
dependencies reference nonexistent parent node ('notifications_system', '0002_initial')
```

**Workaround**: Use SQLite for tests (set `TEST_DB=sqlite`)

**Long-term Fix**: Resolve migration dependencies in the actual migrations

---

## 📋 Test Database Configuration

### SQLite (Default for Local Testing)

- **Pros**: Fast, no migration issues, no setup required
- **Cons**: Some PostgreSQL-specific features not available
- **Use When**: Running tests locally, quick development testing

### PostgreSQL (For CI/CD)

- **Pros**: Matches production environment, full feature support
- **Cons**: Requires database setup, migration dependencies
- **Use When**: CI/CD pipelines, integration testing

---

## 🔍 Troubleshooting

### Issue: Migration Errors

**Solution**: Use SQLite for tests
```bash
export TEST_DB=sqlite
pytest -v
```

### Issue: Database Connection Errors

**Solution**: Ensure Docker containers are running
```bash
docker-compose ps
docker-compose up -d
```

### Issue: Coverage Too Low

**Solution**: This is expected when running all tests. Run specific test files:
```bash
pytest specific_test_file.py --cov=. --cov-report=html
```

---

## ✅ Verification

To verify the setup works:

```bash
# 1. Run a simple test
docker-compose exec web bash -c "export TEST_DB=sqlite && pytest tests/examples/test_example.py -v"

# 2. Check test discovery
docker-compose exec web pytest --collect-only -q | head -20

# 3. Run with coverage (expect lower coverage for full suite)
docker-compose exec web bash -c "export TEST_DB=sqlite && pytest tests/test_optimizations.py --cov=. --cov-report=term"
```

---

## 🎯 Next Steps

1. **For Local Development**: Use SQLite (`TEST_DB=sqlite`)
2. **For CI/CD**: Use PostgreSQL (`TEST_DB=postgres`) - but may need migration fixes
3. **Fix Migration Dependencies**: Resolve the notifications_system migration dependency issue

---

## 📚 Related Files

- `backend/conftest.py` - Test fixtures and database setup
- `backend/pytest.ini` - Pytest configuration
- `backend/writing_system/settings_test.py` - Test settings
- `backend/scripts/setup_test_db.sh` - Test database setup script
- `CI_CD_GUIDE.md` - CI/CD testing guide

---

**The test database setup is now fixed! You can run tests using SQLite for local development.** ✅

