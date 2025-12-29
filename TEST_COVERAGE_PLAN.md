# Test Coverage Plan - 95% Target

**Date**: January 2025  
**Target**: 95% code coverage minimum  
**Status**: In Progress

---

## 🎯 Goal

Achieve and maintain **95% test coverage** across both backend and frontend codebases.

---

## 📊 Current Status

### Backend Coverage
- **Current**: ~10-15% (estimated)
- **Target**: 95%
- **Gap**: ~80-85%

### Frontend Coverage
- **Current**: ~5-10% (estimated)
- **Target**: 95%
- **Gap**: ~85-90%

---

## 🔍 Coverage Analysis

### What's Currently Tested

#### Backend ✅
- Payment system (14 tests)
- Order workflows (16 tests)
- Discount system (12+ tests)
- Wallet system (10+ tests)
- Authentication (10 tests)
- Order management (12 tests)
- Model unit tests (12 tests)
- Permissions (8 tests)
- Writer management (10+ tests)
- Integration workflows (5+ tests)

**Total**: ~100+ test methods

#### Frontend ✅
- OrderList component
- PaymentHistory component
- Basic component tests
- API integration tests

**Total**: ~30+ test cases

### What Needs Testing

#### Backend (Priority Order)

**High Priority** (Critical Business Logic):
1. **Order Services** (~20% coverage needed)
   - `orders/services/assignment.py`
   - `orders/services/status_transition_service.py`
   - `orders/services/smart_matching_service.py`
   - `orders/services/cancel_order_service.py`
   - `orders/services/order_action_service.py`

2. **Payment Services** (~15% coverage needed)
   - `order_payments_management/services/payment_service.py`
   - Payment processing logic
   - Refund workflows
   - Invoice generation

3. **User Management** (~25% coverage needed)
   - `users/services/user_edit_service.py`
   - Profile management
   - Role management
   - User activation/deactivation

4. **Authentication** (~10% coverage needed)
   - `authentication/services/auth_service.py`
   - Session management
   - Magic link service
   - Password reset

5. **Writer Management** (~20% coverage needed)
   - `writer_management/services/`
   - Performance metrics
   - Assignment logic
   - Earnings calculation

6. **Support Management** (~15% coverage needed)
   - `support_management/services/`
   - SLA tracking
   - Ticket assignment
   - Email notifications

**Medium Priority**:
7. **Communications** (~30% coverage needed)
   - `communications/services/`
   - Message threading
   - Real-time updates

8. **Notifications** (~25% coverage needed)
   - `notifications_system/services/`
   - Template rendering
   - Delivery logic

9. **Loyalty & Referrals** (~20% coverage needed)
   - `loyalty_management/services/`
   - `referrals/services/`

10. **Fines System** (~15% coverage needed)
    - `fines/services/`
    - Fine calculation
    - Appeal processing

**Lower Priority**:
11. **Blog/Content Management** (~10% coverage needed)
12. **Analytics** (~10% coverage needed)
13. **Admin Dashboards** (~10% coverage needed)

#### Frontend (Priority Order)

**High Priority**:
1. **API Clients** (~40% coverage needed)
   - All API service files in `src/api/`
   - Error handling
   - Request/response transformations

2. **Stores (Pinia)** (~30% coverage needed)
   - `src/stores/auth.js`
   - `src/stores/messages.js`
   - State management logic

3. **Composables** (~25% coverage needed)
   - `src/composables/useOrderMessages.js`
   - `src/composables/useWriterData.js`
   - `src/composables/useApiCache.js`

4. **Critical Components** (~20% coverage needed)
   - Order management components
   - Payment components
   - Dashboard components

**Medium Priority**:
5. **Form Components** (~15% coverage needed)
6. **Utility Functions** (~10% coverage needed)
7. **Router Guards** (~10% coverage needed)

---

## 📋 Implementation Plan

### Phase 1: Backend Core Services (Week 1-2)

**Goal**: Reach 60% backend coverage

1. **Order Services** (Priority 1)
   ```python
   # Create: backend/orders/tests/test_services/
   - test_assignment_service.py
   - test_status_transition_service.py
   - test_smart_matching_service.py
   - test_cancel_order_service.py
   - test_order_action_service.py
   ```

2. **Payment Services** (Priority 2)
   ```python
   # Create: backend/order_payments_management/tests/test_services/
   - test_payment_service.py
   - test_refund_service.py
   - test_invoice_service.py
   ```

3. **User Services** (Priority 3)
   ```python
   # Create: backend/users/tests/test_services/
   - test_user_edit_service.py
   - test_profile_service.py
   ```

### Phase 2: Backend Extended Coverage (Week 3-4)

**Goal**: Reach 80% backend coverage

4. **Writer Management Services**
5. **Support Management Services**
6. **Authentication Services**
7. **Communication Services**

### Phase 3: Frontend Coverage (Week 5-6)

**Goal**: Reach 70% frontend coverage

1. **API Clients**
2. **Stores**
3. **Composables**
4. **Critical Components**

### Phase 4: Final Push to 95% (Week 7-8)

**Goal**: Reach 95% coverage

1. **Remaining Backend Services**
2. **Remaining Frontend Components**
3. **Edge Cases**
4. **Error Handling**

---

## 🛠️ Tools & Commands

### Run Tests with Coverage

```bash
# All tests with 95% requirement
make test-coverage

# Backend only
make test-coverage-backend

# Frontend only
make test-coverage-frontend

# Using script directly
./scripts/run_tests_with_coverage.sh
```

### View Coverage Reports

```bash
# Backend HTML report
open backend/htmlcov/index.html

# Frontend HTML report
open frontend/coverage/index.html
```

### Check Coverage for Specific Files

```bash
# Backend - specific file
cd backend
pytest --cov=orders/services/assignment.py --cov-report=term-missing

# Frontend - specific file
cd frontend
npm run test:run -- --coverage src/api/orders.js
```

---

## 📝 Test Writing Guidelines

### Backend Test Structure

```python
import pytest
from django.test import TestCase
from orders.services.assignment import AssignmentService

@pytest.mark.django_db
class TestAssignmentService:
    """Test assignment service functionality."""
    
    def test_assign_order_to_writer(self, order, writer_profile):
        """Test successful order assignment."""
        result = AssignmentService.assign_order(order.id, writer_profile.id)
        assert result.success is True
        assert result.order.writer == writer_profile
    
    def test_assign_order_invalid_writer(self, order):
        """Test assignment with invalid writer."""
        with pytest.raises(ValueError):
            AssignmentService.assign_order(order.id, 99999)
```

### Frontend Test Structure

```javascript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import OrderList from '@/components/OrderList.vue'

describe('OrderList', () => {
  it('renders orders correctly', async () => {
    const wrapper = mount(OrderList, {
      props: {
        orders: [{ id: 1, title: 'Test Order' }]
      }
    })
    
    expect(wrapper.text()).toContain('Test Order')
  })
})
```

---

## 🎯 Coverage Targets by Module

### Backend Modules

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| `orders/services/` | ~20% | 95% | 🔴 High |
| `order_payments_management/services/` | ~15% | 95% | 🔴 High |
| `users/services/` | ~10% | 95% | 🔴 High |
| `authentication/services/` | ~30% | 95% | 🔴 High |
| `writer_management/services/` | ~20% | 95% | 🟡 Medium |
| `support_management/services/` | ~15% | 95% | 🟡 Medium |
| `communications/services/` | ~10% | 95% | 🟡 Medium |
| `notifications_system/services/` | ~10% | 95% | 🟡 Medium |
| `loyalty_management/services/` | ~5% | 95% | 🟢 Low |
| `fines/services/` | ~30% | 95% | 🟢 Low |

### Frontend Modules

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| `src/api/` | ~5% | 95% | 🔴 High |
| `src/stores/` | ~10% | 95% | 🔴 High |
| `src/composables/` | ~5% | 95% | 🔴 High |
| `src/components/orders/` | ~20% | 95% | 🟡 Medium |
| `src/components/payments/` | ~15% | 95% | 🟡 Medium |
| `src/utils/` | ~10% | 95% | 🟢 Low |

---

## 📈 Progress Tracking

### Week 1 Progress
- [ ] Order services tests (0/5 files)
- [ ] Payment services tests (0/3 files)
- [ ] User services tests (0/2 files)

### Week 2 Progress
- [ ] Writer management tests
- [ ] Support management tests
- [ ] Authentication services tests

### Week 3-4 Progress
- [ ] Communication services tests
- [ ] Notification services tests
- [ ] Remaining backend services

### Week 5-6 Progress
- [ ] Frontend API clients
- [ ] Frontend stores
- [ ] Frontend composables

### Week 7-8 Progress
- [ ] Edge cases
- [ ] Error handling
- [ ] Final coverage push

---

## 🔧 CI/CD Integration

The CI/CD pipeline now enforces 95% coverage:

- ✅ Backend tests fail if coverage < 95%
- ✅ Frontend tests fail if coverage < 95%
- ✅ Coverage reports uploaded as artifacts
- ✅ Coverage displayed in PR comments

---

## 💡 Tips for High Coverage

### 1. Test Happy Paths First
- Start with successful operations
- Then add error cases
- Finally add edge cases

### 2. Use Fixtures
- Reuse test data
- Keep tests DRY
- Use factories for complex objects

### 3. Mock External Services
- Don't test external APIs
- Mock database calls when appropriate
- Mock file system operations

### 4. Test Business Logic
- Focus on services, not views
- Test calculations
- Test state transitions

### 5. Use Coverage Reports
- Identify untested code
- Focus on high-impact areas
- Don't obsess over 100%

---

## 🚨 Common Issues

### Coverage Not Increasing

**Problem**: Running tests but coverage stays the same

**Solution**:
- Check if files are in `omit` list in `pytest.ini`
- Verify test files are being discovered
- Check coverage report for missing lines

### Tests Too Slow

**Problem**: Test suite takes too long

**Solution**:
- Use `--reuse-db` flag
- Run tests in parallel: `pytest -n auto`
- Mock slow operations
- Use `@pytest.mark.slow` for long tests

### Coverage Threshold Too High

**Problem**: Can't reach 95% immediately

**Solution**:
- Start with lower threshold (70%)
- Increase gradually (75%, 80%, 85%, 90%, 95%)
- Focus on critical paths first

---

## ✅ Success Criteria

- [ ] Backend coverage ≥ 95%
- [ ] Frontend coverage ≥ 95%
- [ ] All tests passing
- [ ] CI/CD enforcing coverage
- [ ] Coverage reports generated
- [ ] Documentation updated

---

## 📚 Resources

- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Vitest Coverage](https://vitest.dev/guide/coverage.html)
- [Django Testing Best Practices](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Vue Testing Guide](https://vuejs.org/guide/scaling-up/testing.html)

---

**Let's achieve 95% coverage!** 🎯

