# Running Tests Locally - Quick Guide

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

Since your project uses Docker, tests should be run inside the Docker containers.

#### Backend Tests

```bash
# Run all backend tests
docker-compose exec web pytest

# Run specific test file
docker-compose exec web pytest tests/test_optimizations.py

# Run with coverage
docker-compose exec web pytest --cov=. --cov-report=html

# Run specific test
docker-compose exec web pytest orders/tests/test_services/test_create_order_service.py::TestCreateOrderService::test_method_name

# Run tests with markers
docker-compose exec web pytest -m unit
docker-compose exec web pytest -m integration
docker-compose exec web pytest -m "not slow"
```

#### Frontend Tests

```bash
# Run all frontend tests
cd frontend
npm run test:run

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm run test:run -- tests/components/FormField.test.js
```

### Option 2: Using Makefile

```bash
# Run all tests
make test

# Backend only
make test-backend

# Frontend only
make test-frontend

# With coverage
make coverage
```

---

## 📋 Step-by-Step Guide

### 1. Ensure Docker Containers are Running

```bash
# Check status
docker-compose ps

# Start if not running
docker-compose up -d
```

### 2. Run Backend Tests

```bash
# Simple test run
docker-compose exec web pytest -v

# With specific settings
docker-compose exec web pytest --settings=writing_system.settings_test -v

# Run a specific test file
docker-compose exec web pytest orders/tests/test_services/test_create_order_service.py -v
```

### 3. Run Frontend Tests

```bash
cd frontend

# Install dependencies (if not done)
npm ci

# Run tests
npm run test:run

# Run with UI (interactive)
npm run test:ui
```

---

## 🔍 Common Issues and Solutions

### Issue 1: Database Migration Errors

**Error**: `django.db.utils.IntegrityError: null value in column "name"`

**Solution**:
```bash
# Run migrations in test database
docker-compose exec web python manage.py migrate --settings=writing_system.settings_test
```

### Issue 2: Test File Not Found

**Error**: `ERROR: file or directory not found`

**Solution**: 
- Make sure you're using the correct path inside Docker (working directory is `/app`)
- Use relative paths from the backend directory: `tests/test_file.py` not `backend/tests/test_file.py`

### Issue 3: Frontend Tests Not Found

**Error**: `No test files found`

**Solution**:
- Make sure test files end with `.test.js` or `.spec.js`
- Check that test files are in the `tests/` directory
- Run: `npm run test:run -- tests/components/FormField.test.js`

### Issue 4: Coverage Too Low

**Error**: `FAIL Required test coverage of 95% not reached`

**Solution**:
- This is expected if you're running all tests including untested code
- Run specific test files: `pytest specific_test_file.py`
- Or adjust coverage threshold in `pytest.ini` for development

---

## 📊 Viewing Test Results

### Backend Coverage Report

```bash
# Generate HTML coverage report
docker-compose exec web pytest --cov=. --cov-report=html

# View in browser (on host machine)
open backend/htmlcov/index.html
```

### Frontend Coverage Report

```bash
cd frontend
npm run test:coverage

# View in browser
open frontend/coverage/index.html
```

---

## 🎯 Recommended Test Commands

### For Development

```bash
# Quick test run (fast)
docker-compose exec web pytest -m "not slow" -v

# Watch mode for frontend
cd frontend && npm run test:watch
```

### For CI/CD

```bash
# Full test suite with coverage
docker-compose exec web pytest --cov=. --cov-report=xml --cov-report=html -v

# Frontend with coverage
cd frontend && npm run test:ci
```

---

## 📝 Test Examples

### Running a Specific Test

```bash
# Backend
docker-compose exec web pytest orders/tests/test_services/test_create_order_service.py::TestCreateOrderService::test_create_order_success -v

# Frontend
cd frontend && npm run test:run -- tests/components/FormField.test.js
```

### Running Tests by Marker

```bash
# Unit tests only
docker-compose exec web pytest -m unit -v

# Integration tests
docker-compose exec web pytest -m integration -v

# API tests
docker-compose exec web pytest -m api -v

# Exclude slow tests
docker-compose exec web pytest -m "not slow" -v
```

---

## 🛠️ Troubleshooting

### Reset Test Database

```bash
# Recreate test database
docker-compose exec web python manage.py migrate --settings=writing_system.settings_test --run-syncdb
```

### Clear Test Cache

```bash
# Remove pytest cache
docker-compose exec web rm -rf .pytest_cache
docker-compose exec web rm -rf htmlcov
```

### Check Test Configuration

```bash
# Verify pytest configuration
docker-compose exec web pytest --collect-only

# List all available tests
docker-compose exec web pytest --collect-only -q
```

---

## 📚 Additional Resources

- See `TESTING_GUIDE.md` for comprehensive testing documentation
- See `Makefile` for all available test commands (`make help`)
- Check `.github/workflows/tests.yml` for CI/CD test configuration

---

## ✅ Quick Verification

Run these commands to verify everything is set up:

```bash
# 1. Check Docker containers
docker-compose ps

# 2. Check pytest installation
docker-compose exec web pytest --version

# 3. Check frontend test setup
cd frontend && npm run test:run -- --version

# 4. Run a simple test
docker-compose exec web pytest tests/examples/test_example.py -v
```

---

**Happy Testing! 🧪**

