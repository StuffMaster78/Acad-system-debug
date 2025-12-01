# Testing Guide - Writing System Platform

**Version**: 1.0  
**Last Updated**: December 2025  
**Status**: Production Ready

---

## 🎯 Overview

This guide provides comprehensive instructions for writing, running, and maintaining tests in the Writing System Platform. We follow strict QA standards with a focus on:

- **Coverage**: Minimum 70% code coverage required
- **Quality**: All tests must pass before merging
- **Speed**: Fast feedback loops with parallel test execution
- **Maintainability**: Clear, readable, and well-documented tests

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Test Types](#test-types)
5. [Best Practices](#best-practices)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Backend Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/examples/test_example.py

# Run tests by marker
pytest -m unit
pytest -m api
pytest -m integration
```

### Frontend Tests

```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run with UI
npm run test:ui
```

---

## 🔧 Backend Testing

### Framework

- **pytest**: Primary testing framework
- **pytest-django**: Django integration
- **pytest-cov**: Coverage reporting
- **factory_boy**: Test data generation
- **Faker**: Realistic fake data

### Test Structure

```
backend/
├── conftest.py              # Shared fixtures
├── pytest.ini              # Pytest configuration
├── tests/
│   ├── __init__.py
│   ├── factories.py         # Test data factories
│   ├── examples/            # Example tests
│   └── [app_name]/          # App-specific tests
│       ├── test_models.py
│       ├── test_views.py
│       ├── test_serializers.py
│       └── test_services.py
└── [app_name]/
    └── tests.py             # Legacy tests (being migrated)
```

### Writing Backend Tests

#### 1. Unit Tests (Fast, Isolated)

```python
import pytest
from tests.factories import ClientUserFactory

@pytest.mark.unit
class TestUserModel:
    def test_user_creation(self, website):
        user = ClientUserFactory(website=website)
        assert user.id is not None
        assert user.email is not None
```

#### 2. API Tests (Integration)

```python
import pytest
from rest_framework import status

@pytest.mark.api
@pytest.mark.integration
class TestOrderAPI:
    def test_create_order(self, authenticated_client, client_user):
        url = '/api/v1/orders/orders/'
        data = {
            'title': 'Test Order',
            'pages': 5,
            # ... other fields
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
```

#### 3. Using Fixtures

```python
# Use pre-configured fixtures
def test_with_client(authenticated_client, client_user):
    # authenticated_client is already set up with JWT token
    response = authenticated_client.get('/api/v1/orders/orders/')
    assert response.status_code == 200
```

#### 4. Using Factories

```python
from tests.factories import OrderFactory, ClientUserFactory

def test_order_creation(website):
    client = ClientUserFactory(website=website)
    order = OrderFactory(client=client, website=website)
    assert order.client == client
```

### Available Fixtures

- `website`: Test website instance
- `client_user`, `writer_user`, `admin_user`, etc.: Role-specific users
- `api_client`: Unauthenticated API client
- `authenticated_client`: Authenticated client user API client
- `authenticated_writer_client`: Authenticated writer API client
- `authenticated_admin_client`: Authenticated admin API client
- `client_token`, `writer_token`, `admin_token`: JWT tokens

### Test Markers

Use markers to categorize and filter tests:

```python
@pytest.mark.unit          # Fast, isolated unit tests
@pytest.mark.integration   # Integration tests (require DB)
@pytest.mark.api           # API endpoint tests
@pytest.mark.slow          # Slow-running tests
@pytest.mark.auth          # Authentication tests
@pytest.mark.payment       # Payment system tests
@pytest.mark.order         # Order management tests
@pytest.mark.writer        # Writer management tests
@pytest.mark.client        # Client management tests
@pytest.mark.admin         # Admin management tests
@pytest.mark.e2e           # End-to-end tests
@pytest.mark.performance  # Performance tests
@pytest.mark.security      # Security tests
```

### Running Specific Tests

```bash
# Run only unit tests
pytest -m unit

# Run only API tests
pytest -m api

# Run tests for specific app
pytest orders/tests.py

# Run specific test
pytest tests/examples/test_example.py::TestOrderAPI::test_create_order

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## 🎨 Frontend Testing

### Framework

- **Vitest**: Fast unit test framework
- **@vue/test-utils**: Vue component testing utilities
- **jsdom**: DOM simulation for browser environment
- **@vitest/coverage-v8**: Coverage reporting

### Test Structure

```
frontend/
├── vitest.config.js        # Vitest configuration
├── tests/
│   ├── setup.js            # Test environment setup
│   ├── utils/
│   │   └── test-utils.js   # Test utilities
│   ├── examples/            # Example tests
│   └── components/         # Component tests
│       └── **/*.test.js
└── src/
    └── components/
        └── **/*.vue
```

### Writing Frontend Tests

#### 1. Component Tests

```javascript
import { describe, it, expect } from 'vitest'
import { mountComponent } from '../utils/test-utils'
import YourComponent from '@/components/YourComponent.vue'

describe('YourComponent', () => {
  it('should render correctly', () => {
    const wrapper = mountComponent(YourComponent, {
      props: {
        title: 'Test Title'
      }
    })
    
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Test Title')
  })
})
```

#### 2. Testing Interactions

```javascript
import { nextTick } from 'vue'

it('should handle button click', async () => {
  const handleClick = vi.fn()
  const wrapper = mountComponent(YourComponent, {
    props: {
      onClick: handleClick
    }
  })
  
  await wrapper.find('button').trigger('click')
  await nextTick()
  
  expect(handleClick).toHaveBeenCalledTimes(1)
})
```

#### 3. Testing API Calls

```javascript
import { createMockAxios, createMockOrder } from '../utils/test-utils'

it('should fetch and display data', async () => {
  const mockData = createMockOrder()
  const mockAxios = createMockAxios()
  mockAxios.get.mockResolvedValue({ data: mockData })
  
  const wrapper = mountComponent(YourComponent, {
    global: {
      mocks: {
        $axios: mockAxios
      }
    }
  })
  
  await nextTick()
  
  expect(mockAxios.get).toHaveBeenCalled()
  expect(wrapper.text()).toContain(mockData.title)
})
```

### Available Test Utilities

- `mountComponent(component, options)`: Mount component with defaults
- `shallowMountComponent(component, options)`: Shallow mount component
- `createTestRouter(routes)`: Create test router
- `createTestPinia()`: Create test Pinia store
- `createMockUser(overrides)`: Create mock user object
- `createMockOrder(overrides)`: Create mock order object
- `createMockAxios()`: Create mock axios instance
- `waitForNextTick()`: Wait for Vue next tick
- `waitFor(ms)`: Wait for specified milliseconds

---

## 📊 Test Types

### 1. Unit Tests

**Purpose**: Test individual functions/components in isolation

**Characteristics**:
- Fast execution (< 100ms per test)
- No external dependencies
- Mock all external calls
- High coverage target (80%+)

**Example**:
```python
@pytest.mark.unit
def test_calculate_price():
    result = calculate_price(pages=5, rate=10.0)
    assert result == 50.0
```

### 2. Integration Tests

**Purpose**: Test interactions between components

**Characteristics**:
- Require database
- Test API endpoints
- Test service layer interactions
- Medium execution time (< 1s per test)

**Example**:
```python
@pytest.mark.integration
@pytest.mark.api
def test_create_order_integration(authenticated_client):
    response = authenticated_client.post('/api/v1/orders/', {...})
    assert response.status_code == 201
```

### 3. End-to-End Tests

**Purpose**: Test complete user workflows

**Characteristics**:
- Test full user journeys
- Require all services (DB, Redis, etc.)
- Slower execution (> 1s per test)
- Critical path coverage

**Example**:
```python
@pytest.mark.e2e
def test_complete_order_workflow():
    # 1. Client creates order
    # 2. Admin assigns writer
    # 3. Writer completes order
    # 4. Client approves
    # 5. Payment processed
    pass
```

### 4. Performance Tests

**Purpose**: Ensure system meets performance requirements

**Characteristics**:
- Measure response times
- Test under load
- Identify bottlenecks
- Set performance benchmarks

**Example**:
```python
@pytest.mark.performance
def test_bulk_order_creation():
    start = time.time()
    # Create 100 orders
    elapsed = time.time() - start
    assert elapsed < 5.0  # Must complete in < 5 seconds
```

### 5. Security Tests

**Purpose**: Verify security measures

**Characteristics**:
- Test authentication/authorization
- Test input validation
- Test SQL injection prevention
- Test XSS prevention

**Example**:
```python
@pytest.mark.security
def test_sql_injection_prevention():
    malicious_input = "'; DROP TABLE users; --"
    response = api_client.post('/api/v1/orders/', {
        'title': malicious_input
    })
    # Should sanitize input, not crash
    assert response.status_code != 500
```

---

## ✅ Best Practices

### 1. Test Naming

**Good**:
```python
def test_user_cannot_access_admin_endpoints_when_not_admin():
    pass
```

**Bad**:
```python
def test1():
    pass
```

### 2. Test Organization

- One test per behavior
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 3. Test Data

- Use factories for test data
- Don't rely on database state
- Clean up after tests
- Use fixtures for common setup

### 4. Assertions

- Use specific assertions
- Include helpful error messages
- Test both positive and negative cases
- Test edge cases

### 5. Test Independence

- Tests should not depend on each other
- Tests should be runnable in any order
- Tests should be idempotent

### 6. Coverage

- Aim for 70%+ coverage
- Focus on critical paths
- Don't chase 100% coverage blindly
- Review coverage reports regularly

---

## 🔄 CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests
- Daily at 2 AM UTC (scheduled)

### Test Workflow

1. **Backend Tests**: Run pytest with coverage
2. **Frontend Tests**: Run Vitest with coverage
3. **Integration Tests**: Run full integration suite
4. **Test Summary**: Report results

### Coverage Reports

- Coverage uploaded to Codecov
- HTML reports available as artifacts
- Coverage thresholds enforced (70% minimum)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Tests fail with database errors
```bash
# Solution: Recreate test database
pytest --create-db
```

**Problem**: Tests are slow
```bash
# Solution: Run tests in parallel
pytest -n auto
```

**Problem**: Coverage not showing
```bash
# Solution: Check coverage configuration
pytest --cov=. --cov-report=html
# Open htmlcov/index.html
```

### Frontend Issues

**Problem**: Tests fail with module not found
```bash
# Solution: Reinstall dependencies
npm install
```

**Problem**: jsdom errors
```bash
# Solution: Check vitest.config.js setup
# Ensure jsdom is in devDependencies
```

**Problem**: Vue component not rendering
```bash
# Solution: Check test-utils.js setup
# Ensure Vue Test Utils is configured correctly
```

---

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Factory Boy](https://factoryboy.readthedocs.io/)

---

## 🎯 Quality Gates

Before merging code:

- ✅ All tests must pass
- ✅ Coverage must be ≥ 70%
- ✅ No linting errors
- ✅ All new code must have tests
- ✅ Tests must be reviewed

---

**Remember**: Good tests are an investment in code quality and maintainability. Write them well, and they'll save you time in the long run.

