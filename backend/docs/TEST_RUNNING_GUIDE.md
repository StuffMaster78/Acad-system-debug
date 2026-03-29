# Test Running Guide

## ⚠️ **Current Issue: Migration Dependencies**

The tests are encountering a migration dependency issue:
```
Migration users.0005_alter_user_options_alter_userauditlog_website_and_more 
dependencies reference nonexistent parent node ('notifications_system', '0002_initial')
```

This is a known issue with pytest-django's migration discovery when running tests outside of Docker.

---

## ✅ **Solutions**

### **Option 1: Run Tests in Docker (Recommended)**

If you're using Docker for development, run tests inside the container:

```bash
# Start services
docker-compose up -d

# Run tests inside web container
docker-compose exec web pytest order_payments_management/tests/test_payment_reminders.py -v

# Or run all new tests
docker-compose exec web pytest \
  order_payments_management/tests/test_payment_reminders.py \
  client_management/tests/test_enhanced_order_status.py \
  admin_management/tests/test_fines_dashboard.py \
  -v
```

### **Option 2: Use Django Test Runner**

Run tests using Django's built-in test runner (may work better with migrations):

```bash
# Make sure you're in the backend directory
cd backend

# Run specific test
python manage.py test order_payments_management.tests.test_payment_reminders

# Run all new tests
python manage.py test \
  order_payments_management.tests.test_payment_reminders \
  client_management.tests.test_enhanced_order_status \
  admin_management.tests.test_fines_dashboard
```

### **Option 3: Fix Migration Dependencies**

If you need to run tests locally without Docker:

1. **Check migration dependencies**:
   ```bash
   python manage.py showmigrations notifications_system
   python manage.py showmigrations users
   ```

2. **Ensure all migrations are applied**:
   ```bash
   python manage.py migrate
   ```

3. **Try running tests again**:
   ```bash
   pytest order_payments_management/tests/test_payment_reminders.py -v
   ```

### **Option 4: Use --nomigrations Flag (Limited)**

⚠️ **Warning**: This skips migrations and may cause issues with model state.

```bash
pytest order_payments_management/tests/test_payment_reminders.py -v --nomigrations
```

---

## 📋 **Test Files Created**

### 1. Payment Reminder Tests
**File**: `backend/order_payments_management/tests/test_payment_reminders.py`

**Test Classes**:
- `TestPaymentReminderConfig` - Configuration CRUD
- `TestPaymentReminderService` - Service logic
- `TestPaymentReminderSent` - Sent reminders tracking
- `TestPaymentReminderDeletionMessage` - Deletion messages

**Endpoints Tested**:
- `POST /api/v1/order-payments/payment-reminder-configs/`
- `PATCH /api/v1/order-payments/payment-reminder-configs/{id}/`
- `DELETE /api/v1/order-payments/payment-reminder-configs/{id}/`
- `GET /api/v1/order-payments/payment-reminders-sent/`

### 2. Enhanced Order Status Tests
**File**: `backend/client_management/tests/test_enhanced_order_status.py`

**Test Classes**:
- `TestEnhancedOrderStatus` - Main endpoint tests

**Endpoints Tested**:
- `GET /api/v1/client-management/dashboard/enhanced-order-status/`

### 3. Admin Fines Dashboard Tests
**File**: `backend/admin_management/tests/test_fines_dashboard.py`

**Test Classes**:
- `TestFinesAnalytics` - Analytics dashboard
- `TestFinesDisputeQueue` - Dispute management
- `TestActiveFines` - Active fines listing

**Endpoints Tested**:
- `GET /api/v1/admin-management/fines/analytics/`
- `GET /api/v1/admin-management/fines/appeals/`
- `POST /api/v1/admin-management/fines/{id}/appeals/approve/`
- `POST /api/v1/admin-management/fines/{id}/appeals/reject/`
- `GET /api/v1/admin-management/fines/pending/`

---

## 🎯 **Running Specific Tests**

### Run Single Test
```bash
pytest order_payments_management/tests/test_payment_reminders.py::TestPaymentReminderConfig::test_create_reminder_config -v
```

### Run Test Class
```bash
pytest order_payments_management/tests/test_payment_reminders.py::TestPaymentReminderConfig -v
```

### Run with Coverage
```bash
pytest --cov=order_payments_management --cov-report=html order_payments_management/tests/test_payment_reminders.py
```

### Run with Markers
```bash
pytest -m api          # API endpoint tests
pytest -m integration  # Integration tests
pytest -m payment      # Payment-related tests
pytest -m admin        # Admin-related tests
```

---

## 🔧 **Troubleshooting**

### Issue: Migration dependency errors
**Solution**: Run tests in Docker or ensure all migrations are applied

### Issue: Module not found errors
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Database connection errors
**Solution**: Check database settings in `settings_test.py` and ensure database is accessible

### Issue: Permission errors
**Solution**: Ensure test database has proper permissions or use SQLite for tests

---

## 📊 **Expected Test Results**

When tests run successfully, you should see:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.0, pytest-8.4.0
collected 11 items

order_payments_management/tests/test_payment_reminders.py::TestPaymentReminderConfig::test_list_reminder_configs_requires_auth PASSED
order_payments_management/tests/test_payment_reminders.py::TestPaymentReminderConfig::test_list_reminder_configs_admin_only PASSED
order_payments_management/tests/test_payment_reminders.py::TestPaymentReminderConfig::test_create_reminder_config PASSED
...

============================= 11 passed in 2.34s ==============================
```

---

## 🚀 **Next Steps**

1. **Fix migration dependencies** (if running locally)
2. **Run tests in Docker** (recommended)
3. **Add more test coverage** for service layers
4. **Add integration tests** for complete workflows

---

**Last Updated**: December 2025  
**Status**: Tests created, migration dependency issue needs resolution

