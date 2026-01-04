# Testing Guide

## Overview

This guide covers testing for both backend (Django/Python) and frontend (Vue.js/JavaScript) components of the writing system.

---

## Backend Testing

### Setup

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations for test database
python manage.py migrate --settings=writing_system.settings_test
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest orders/tests/test_services/test_create_order_service.py

# Run tests with markers
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m api                    # API endpoint tests
pytest -m "not slow"            # Exclude slow tests

# Run with coverage
pytest --cov=. --cov-report=html

# Run in parallel (faster)
pytest -n auto

# Run with verbose output
pytest -v

# Run specific test
pytest path/to/test_file.py::TestClass::test_method
```

### Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_optimizations.py      # Optimization tests
│   └── test_api_endpoints.py      # API endpoint tests
├── orders/tests/
│   ├── test_services/              # Service layer tests
│   ├── test_advanced/              # Advanced test scenarios
│   └── test_utils/                 # Utility tests
└── conftest.py                      # Shared fixtures
```

### Test Markers

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (require database)
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests

### Writing Tests

```python
import pytest
from django.test import TestCase
from rest_framework.test import APIClient

@pytest.mark.unit
class TestMyFeature(TestCase):
    """Test my feature."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
    
    def test_feature_works(self):
        """Test that feature works correctly."""
        response = self.client.get('/api/endpoint/')
    assert response.status_code == 200
```

### Coverage Requirements

- **Minimum Coverage**: 95%
- **Coverage Reports**: Generated in `htmlcov/` directory
- **Coverage Formats**: HTML, XML, JSON, Terminal

---

## Frontend Testing

### Setup

```bash
# Install dependencies
cd frontend
npm ci

# Run tests
npm run test
```

### Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test:run tests/components/MyComponent.test.js

# Run tests by category
npm run test:unit          # Unit tests
npm run test:components    # Component tests
npm run test:composables   # Composable tests
npm run test:api           # API tests

# Run tests in UI mode
npm run test:ui
```

### Test Structure

```
frontend/
├── tests/
│   ├── setup.js                    # Test setup
│   ├── utils/
│   │   ├── test-utils.js          # Test utilities
│   │   └── api-mocks.js           # API mocking
│   ├── components/                 # Component tests
│   ├── composables/                # Composable tests
│   └── api/                        # API tests
└── vitest.config.js                # Vitest configuration
```

### Writing Tests

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders correctly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        title: 'Test Title'
      }
    })
    
    expect(wrapper.text()).toContain('Test Title')
  })
})
```

### Coverage Requirements

- **Minimum Coverage**: 80% (lines, functions, branches, statements)
- **Coverage Reports**: Generated in `coverage/` directory
- **Coverage Formats**: HTML, JSON, LCOV

---

## CI/CD Integration

### GitHub Actions Workflows

1. **`.github/workflows/tests.yml`** - Comprehensive test suite
   - Backend unit tests
   - Backend integration tests
   - Frontend unit tests
   - Frontend component tests
   - E2E tests

2. **`.github/workflows/ci.yml`** - Full CI/CD pipeline
   - Tests
   - Code quality checks
   - Security scanning
   - Docker builds
   - Deployment

3. **`.github/workflows/pr-checks.yml`** - PR validation
   - Code review checklist
   - Dependency checks
   - Security checks

### Running Tests in CI

Tests run automatically on:
- Push to `main`, `develop`, or `feature/**` branches
- Pull requests
- Daily schedule (2 AM UTC)
- Manual trigger via `workflow_dispatch`

### Test Results

- **Artifacts**: Test results and coverage reports are uploaded as artifacts
- **Codecov**: Coverage reports are uploaded to Codecov
- **Summary**: Test summary is posted to GitHub Actions summary

---

## Using Makefile

### Quick Commands

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Generate coverage reports
make coverage

# Run linters
make lint

# Clean generated files
make clean
```

### Available Make Targets

- `test` - Run all tests
- `test-backend` - Run backend tests
- `test-frontend` - Run frontend tests
- `coverage` - Generate coverage reports
- `lint` - Run all linters
- `install` - Install all dependencies
- `clean` - Clean generated files

See `make help` for full list of targets.

---

## Test Utilities

### Backend Fixtures

Located in `backend/conftest.py`:

- `db_with_website` - Database with default website
- `website` - Test website fixture
- `mock_request_session` - Mock session object
- User fixtures (admin, client, writer, etc.)

### Frontend Mocks

Located in `frontend/tests/utils/api-mocks.js`:

- `mockApiClient` - Mocked API client
- `createMockResponse` - Create mock API responses
- `createMockError` - Create mock API errors
- `mockLocalStorage` - Mock localStorage
- `mockRouter` - Mock Vue Router
- `mockRoute` - Mock Vue Route

---

## Best Practices

### Backend

1. **Use fixtures** from `conftest.py` for common setup
2. **Mark tests** appropriately (unit, integration, api, etc.)
3. **Test edge cases** and error conditions
4. **Use factories** for test data creation
5. **Keep tests isolated** - each test should be independent
6. **Use descriptive names** for test methods
7. **Test both success and failure paths**

### Frontend

1. **Mock external dependencies** (API calls, router, etc.)
2. **Test user interactions** (clicks, form submissions, etc.)
3. **Test component rendering** with different props
4. **Test error states** and loading states
5. **Use test utilities** for common operations
6. **Keep tests focused** - one assertion per test when possible
7. **Test accessibility** where applicable

---

## Troubleshooting

### Backend Tests

**Issue**: Database connection errors
```bash
# Ensure test database is set up
python manage.py migrate --settings=writing_system.settings_test
```

**Issue**: Import errors
```bash
# Ensure you're in the backend directory
cd backend
# Ensure virtual environment is activated
source venv/bin/activate  # or your venv path
```

**Issue**: Migration errors
```bash
# Reset test database
pytest --create-db
```

### Frontend Tests

**Issue**: Module not found
```bash
# Reinstall dependencies
npm ci
```

**Issue**: jsdom errors
```bash
# Ensure jsdom is installed
npm install --save-dev jsdom
```

**Issue**: Coverage not generating
```bash
# Ensure coverage provider is installed
npm install --save-dev @vitest/coverage-v8
```

---

## Coverage Reports

### Backend Coverage

- **Location**: `backend/htmlcov/index.html`
- **Command**: `make coverage-backend`
- **Minimum**: 95%

### Frontend Coverage

- **Location**: `frontend/coverage/index.html`
- **Command**: `make coverage-frontend`
- **Minimum**: 80%

---

## Continuous Integration

Tests run automatically on:
- ✅ Every push to main/develop
- ✅ Every pull request
- ✅ Daily at 2 AM UTC
- ✅ Manual trigger

All test results and coverage reports are available in GitHub Actions artifacts.

---

## Next Steps

1. **Increase test coverage** to meet minimum requirements
2. **Add E2E tests** for critical user flows
3. **Add performance tests** for optimized endpoints
4. **Add security tests** for authentication/authorization
5. **Set up test coverage badges** in README
