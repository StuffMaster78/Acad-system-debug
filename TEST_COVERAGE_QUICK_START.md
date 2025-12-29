# Test Coverage Quick Start - 95% Target

**Goal**: Achieve 95% test coverage  
**Time**: Start now!

---

## 🚀 Quick Commands

### Run Tests with 95% Coverage Requirement

```bash
# All tests (backend + frontend)
make test-coverage

# Backend only
make test-coverage-backend

# Frontend only
make test-coverage-frontend

# Check what needs more tests
make coverage-gaps
```

### View Coverage Reports

```bash
# Backend HTML report
open backend/htmlcov/index.html

# Frontend HTML report
open frontend/coverage/index.html
```

---

## 📊 Current Status

Run this to see current coverage:

```bash
make test-coverage
```

This will:
1. ✅ Run all tests
2. ✅ Generate coverage reports
3. ✅ Show coverage percentage
4. ❌ Fail if coverage < 95%

---

## 🎯 What's Configured

### Backend (pytest.ini)
- ✅ Coverage threshold: **95%**
- ✅ Fails if below 95%
- ✅ HTML reports generated
- ✅ XML reports for CI/CD

### Frontend (vitest.config.js)
- ✅ Coverage threshold: **95%**
- ✅ Fails if below 95%
- ✅ HTML reports generated
- ✅ LCOV reports for CI/CD

### CI/CD (.github/workflows/ci.yml)
- ✅ Enforces 95% coverage
- ✅ Blocks deployment if below 95%
- ✅ Uploads coverage reports

---

## 📝 Next Steps

1. **Run tests to see current coverage**:
   ```bash
   make test-coverage
   ```

2. **Check what needs testing**:
   ```bash
   make coverage-gaps
   ```

3. **Start writing tests**:
   - Focus on files with lowest coverage
   - Start with critical business logic
   - See `TEST_COVERAGE_PLAN.md` for priorities

4. **View coverage reports**:
   - Open HTML reports
   - See which lines are missing
   - Write tests for uncovered code

---

## 🔧 Troubleshooting

### Tests Fail with "Coverage too low"

**Solution**: Write more tests! Focus on:
1. Files with lowest coverage
2. Critical business logic
3. Error handling paths

### Coverage Not Increasing

**Check**:
- Are test files being discovered?
- Are files in `omit` list?
- Are tests actually running?

### Tests Too Slow

**Solution**:
- Use `pytest -n auto` for parallel execution
- Mock slow operations
- Use `--reuse-db` flag

---

## 📚 Full Documentation

- **Complete Plan**: `TEST_COVERAGE_PLAN.md`
- **Testing Guide**: `TESTING_GUIDE.md`
- **CI/CD Setup**: `CI_CD_IMPLEMENTATION.md`

---

**Let's hit 95%!** 🎯

