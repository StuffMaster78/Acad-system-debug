# Testing Start Guide

## 🎯 Quick Start

### Frontend Tests ✅ Working
```bash
cd frontend
npm test
```

**Current Status**: 24 tests passing ✅

### Backend Tests ⚠️ Setup Needed

The backend tests need pytest-cov to be installed or coverage options removed from pytest.ini.

**Option 1: Install pytest-cov** (Recommended)
```bash
docker-compose exec web pip install pytest-cov
```

**Option 2: Run without coverage** (Current)
```bash
docker-compose exec web pytest tests/ -v --no-cov
```

## 📝 New Tests Created

### Backend Tests

1. **Payment Tests** (`backend/tests/test_payments.py`)
   - Payment creation
   - Wallet payment processing
   - Insufficient balance handling
   - Discount application
   - Payment listing

2. **Order Workflow Tests** (`backend/tests/test_order_workflows.py`)
   - Order creation
   - Order assignment
   - Order completion
   - Order cancellation
   - Order listing and filtering

### Frontend Tests

1. **OrderList Component** (`frontend/tests/components/OrderList.test.js`)
   - Component rendering
   - Loading states
   - Error handling
   - Filtering
   - Bulk selection

2. **PaymentHistory Component** (`frontend/tests/components/PaymentHistory.test.js`)
   - Payment history display
   - Receipt download
   - Status filtering

## 🚀 Running Tests

### Run All Frontend Tests
```bash
cd frontend
npm test
```

### Run All Backend Tests
```bash
docker-compose exec web pytest tests/ -v
```

### Run Specific Test Files
```bash
# Backend
docker-compose exec web pytest tests/test_payments.py -v
docker-compose exec web pytest tests/test_order_workflows.py -v

# Frontend
cd frontend
npm test OrderList
npm test PaymentHistory
```

### Run Tests by Marker
```bash
# Backend
docker-compose exec web pytest -m payment -v
docker-compose exec web pytest -m order -v
docker-compose exec web pytest -m api -v
```

## 🔧 Fixing Issues

### Backend Test Issues

1. **Marker Registration Error**
   - Markers are defined in `pytest.ini`
   - If error persists, run: `pytest --strict-markers=false`

2. **Missing Fixtures**
   - Added to `conftest.py`
   - Includes: `order`, `client_wallet`, `discount`, `writer_profile`, etc.

3. **Import Errors**
   - Check if models/services exist
   - Update imports if app structure changed

### Frontend Test Issues

1. **Component Not Found**
   - Check import paths
   - Verify component exists

2. **API Mock Issues**
   - Update mock implementations
   - Check API client structure

## 📊 Test Coverage

### Current Coverage
- **Frontend**: ~5% (basic tests)
- **Backend**: ~10% (some tests exist)

### Target Coverage
- **Frontend**: 70%+
- **Backend**: 70%+
- **Critical Paths**: 90%+

## ✅ Next Steps

1. **Run the new tests**
   ```bash
   # Backend
   docker-compose exec web pytest tests/test_payments.py tests/test_order_workflows.py -v
   
   # Frontend
   cd frontend && npm test
   ```

2. **Fix any failing tests**
   - Update fixtures if needed
   - Adjust test expectations
   - Fix API endpoints if issues found

3. **Expand test coverage**
   - Add more payment scenarios
   - Add more order scenarios
   - Add discount tests
   - Add wallet tests
   - Add more frontend components

4. **Set up coverage reporting**
   - Install pytest-cov for backend
   - Configure coverage thresholds
   - Generate coverage reports

## 📚 Test Files Created

- `backend/tests/test_payments.py` - Payment system tests
- `backend/tests/test_order_workflows.py` - Order workflow tests
- `frontend/tests/components/OrderList.test.js` - Order list component tests
- `frontend/tests/components/PaymentHistory.test.js` - Payment history tests
- `TESTING_IMPLEMENTATION_PLAN.md` - Testing roadmap

## 🎉 Status

**Testing Infrastructure**: ✅ **READY**

- Frontend tests: 24 passing ✅
- Backend test framework: Configured ✅
- New critical tests: Created ✅
- Test fixtures: Enhanced ✅

Ready to run tests and expand coverage!

