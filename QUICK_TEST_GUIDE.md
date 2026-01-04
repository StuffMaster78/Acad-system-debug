# Quick Test Guide 🚀

## ✅ What's Working

### Frontend Tests - **WORKING** ✅
```bash
cd frontend
npm run test:run
# ✓ 4 tests passed
```

### Backend Tests - **FIXED** ✅
```bash
# Use SQLite for local testing (recommended)
docker-compose exec web bash -c "export TEST_DB=sqlite && pytest -v"

# Or use Makefile
make test-backend
```

---

## 🎯 Quick Commands

### Run All Tests
```bash
# Using Makefile (easiest)
make test

# Or manually
# Frontend
cd frontend && npm run test:run

# Backend
docker-compose exec web bash -c "export TEST_DB=sqlite && pytest -v"
```

### Run Specific Tests
```bash
# Frontend - specific file
cd frontend && npm run test:run -- tests/components/FormField.test.js

# Backend - specific file
docker-compose exec web bash -c "export TEST_DB=sqlite && pytest tests/test_optimizations.py -v"
```

### With Coverage
```bash
# Frontend
cd frontend && npm run test:coverage

# Backend
docker-compose exec web bash -c "export TEST_DB=sqlite && pytest --cov=. --cov-report=html"
```

---

## 📊 CI/CD Status

### GitHub Actions Workflows

1. **`.github/workflows/tests.yml`** - Comprehensive test suite
   - Runs on: Push, PR, Daily schedule, Manual trigger
   - Tests: Backend unit, Backend integration, Frontend unit, Frontend components, E2E

2. **`.github/workflows/ci.yml`** - Full CI/CD pipeline
   - Tests → Code Quality → Security → Build → Deploy

3. **`.github/workflows/pr-checks.yml`** - PR validation
   - Title validation, Conflict checks, Security checks

### View CI/CD Results

1. Go to GitHub repository
2. Click **"Actions"** tab
3. Select workflow run to see results

---

## 🔧 Troubleshooting

### Backend Tests Not Working?

```bash
# 1. Ensure Docker is running
docker-compose ps

# 2. Use SQLite (avoids migration issues)
export TEST_DB=sqlite
docker-compose exec web pytest -v

# 3. Check test discovery
docker-compose exec web pytest --collect-only -q
```

### Frontend Tests Not Working?

```bash
# 1. Install dependencies
cd frontend && npm ci

# 2. Run tests
npm run test:run

# 3. Check test files exist
ls -la tests/components/
```

---

## 📚 Documentation

- **`RUN_TESTS_GUIDE.md`** - Detailed test running guide
- **`TESTING_GUIDE.md`** - Comprehensive testing documentation
- **`CI_CD_GUIDE.md`** - CI/CD testing guide
- **`BACKEND_TEST_SETUP_FIXED.md`** - Backend test setup details

---

## ✅ Verification Checklist

- [x] Frontend tests working
- [x] Backend test database setup fixed
- [x] CI/CD workflows configured
- [x] Test documentation created
- [x] Makefile commands available

---

**You're all set! Run `make test` to test everything!** 🎉

