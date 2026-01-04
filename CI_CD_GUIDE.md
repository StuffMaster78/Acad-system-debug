# CI/CD Testing Guide

## 🚀 Overview

Your project has comprehensive CI/CD pipelines set up using GitHub Actions. Tests run automatically on every push and pull request.

---

## 📋 CI/CD Workflows

### 1. **Comprehensive Test Suite** (`.github/workflows/tests.yml`)

This is the main test workflow that runs:

- **Backend Unit Tests** - Fast, isolated tests
- **Backend Integration Tests** - Database-dependent tests
- **Frontend Unit Tests** - Component and utility tests
- **Frontend Component Tests** - Vue component tests
- **E2E Integration Tests** - End-to-end workflow tests

**Triggers:**
- Push to `main`, `develop`, or `feature/**` branches
- Pull requests to `main` or `develop`
- Daily schedule (2 AM UTC)
- Manual trigger via GitHub Actions UI

### 2. **Full CI/CD Pipeline** (`.github/workflows/ci.yml`)

Complete pipeline including:
- Backend tests
- Frontend tests
- Code quality checks
- Security scanning
- Docker image builds
- Deployment to staging/production

### 3. **PR Checks** (`.github/workflows/pr-checks.yml`)

Validation checks for pull requests:
- PR title validation
- Merge conflict checks
- File size checks
- TODO/FIXME detection
- Console.log detection
- Hardcoded secrets detection
- Dependency security checks

---

## 🔍 How to View CI/CD Results

### On GitHub

1. **Go to your repository** on GitHub
2. **Click on "Actions"** tab
3. **Select a workflow run** to see:
   - Which tests passed/failed
   - Coverage reports
   - Test artifacts
   - Build logs

### Test Results

- **Backend**: Coverage reports in `backend/htmlcov/`
- **Frontend**: Coverage reports in `frontend/coverage/`
- **JUnit XML**: Test results in XML format for CI integration

### Coverage Reports

Coverage is automatically uploaded to:
- **Codecov** (if configured)
- **GitHub Actions Artifacts** (downloadable for 30 days)

---

## 🛠️ Running Tests Locally (Same as CI/CD)

### Backend Tests

```bash
# Run tests exactly as CI/CD does
docker-compose exec web pytest \
  --cov=. \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing \
  --junitxml=junit.xml \
  -v

# Or use the Makefile
make test-backend
make coverage-backend
```

### Frontend Tests

```bash
# Run tests exactly as CI/CD does
cd frontend
npm run test:ci

# Or with coverage
npm run test:coverage
```

---

## 📊 CI/CD Test Configuration

### Backend Test Environment

```yaml
# Services
- PostgreSQL 15
- Redis 7-alpine

# Python Version
- Python 3.11

# Test Settings
- DJANGO_SETTINGS_MODULE: writing_system.settings_test
- Coverage: 95% minimum
- Parallel execution enabled
```

### Frontend Test Environment

```yaml
# Node Version
- Node.js 18

# Test Settings
- Coverage: 80% minimum
- Vitest with jsdom
- JUnit XML output
```

---

## 🔧 Troubleshooting CI/CD Failures

### Backend Tests Failing

**Issue**: Database connection errors
```bash
# Check test database setup
docker-compose exec web python manage.py migrate --settings=writing_system.settings_test
```

**Issue**: Coverage too low
- Add more tests to increase coverage
- Or adjust threshold in `pytest.ini` (for development only)

### Frontend Tests Failing

**Issue**: Module not found
```bash
# Reinstall dependencies
cd frontend && npm ci
```

**Issue**: Test timeout
- Increase timeout in `vitest.config.js`
- Or mark slow tests with `@slow` marker

---

## 🎯 Manual CI/CD Trigger

### Via GitHub UI

1. Go to **Actions** tab
2. Select **"Comprehensive Test Suite"** workflow
3. Click **"Run workflow"**
4. Select branch and click **"Run workflow"**

### Via GitHub CLI

```bash
gh workflow run tests.yml
```

---

## 📈 Monitoring CI/CD

### GitHub Actions Dashboard

- **Workflow runs**: See all test runs
- **Status badges**: Display in README
- **Artifacts**: Download test results and coverage

### Codecov (Optional)

If you set up Codecov:
- Coverage trends over time
- Coverage reports per PR
- Coverage badges

---

## 🚀 Deployment Workflows

### Staging Deployment

- **Trigger**: Push to `main` branch
- **Workflow**: `.github/workflows/deploy-staging.yml`
- **Requires**: All tests passing

### Production Deployment

- **Trigger**: Manual via `workflow_dispatch`
- **Workflow**: `.github/workflows/deploy-production.yml`
- **Requires**: All tests passing + manual approval

---

## 📝 Best Practices

### Before Pushing

1. **Run tests locally**:
   ```bash
   make test
   ```

2. **Check coverage**:
   ```bash
   make coverage
   ```

3. **Fix linting issues**:
   ```bash
   make lint
   ```

### Commit Messages

Use conventional commits for better CI/CD integration:
- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Test changes
- `ci:` - CI/CD changes

---

## 🔐 Secrets Configuration

For CI/CD to work properly, configure these GitHub Secrets:

### Required Secrets

- `TEST_DB_USER` - Test database user
- `TEST_DB_PASSWORD` - Test database password
- `TEST_DB_NAME` - Test database name
- `TEST_SECRET_KEY` - Django secret key for tests

### Optional Secrets

- `CODECOV_TOKEN` - For Codecov integration
- `STAGING_HOST` - Staging server hostname
- `STAGING_SSH_KEY` - SSH key for staging
- `PRODUCTION_HOST` - Production server hostname
- `PRODUCTION_SSH_KEY` - SSH key for production

### Setting Secrets

1. Go to repository **Settings**
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret

---

## 📚 Additional Resources

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Pytest Documentation**: https://docs.pytest.org/
- **Vitest Documentation**: https://vitest.dev/
- **Codecov Documentation**: https://docs.codecov.com/

---

## ✅ Quick Checklist

- [ ] Tests run locally without errors
- [ ] Coverage meets minimum requirements
- [ ] GitHub Actions workflows are configured
- [ ] Secrets are set in GitHub repository
- [ ] Test badges are displayed in README
- [ ] CI/CD runs successfully on push

---

**Happy Testing! 🧪**

