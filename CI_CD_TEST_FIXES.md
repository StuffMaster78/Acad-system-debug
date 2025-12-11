# CI/CD Test Failure Investigation & Fixes

**Date**: December 2025  
**Status**: Investigation in Progress  
**Priority**: 🔴 CRITICAL

---

## 🔍 **Identified Issues**

### 1. **Test Settings Configuration** ⚠️

**Problem**: CI/CD uses PostgreSQL but test settings default to SQLite

**Current Setup:**
- CI/CD provides: `DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_db`
- `pytest.ini` uses: `DJANGO_SETTINGS_MODULE = writing_system.settings`
- `settings_test.py` defaults to SQLite unless `TEST_DB=postgres`

**Impact**: Tests may be running against wrong database or wrong settings

**Fix Required:**
1. Update `pytest.ini` to use test settings in CI
2. Ensure `TEST_DB=postgres` is set in CI environment
3. Or configure Django to use `DATABASE_URL` from environment

---

### 2. **Missing Test Factories** ⚠️

**Problem**: Tests import from `tests.factories` but file may not exist

**Evidence:**
```python
# backend/tests/test_orders.py
from tests.factories import (
    ClientUserFactory, WriterUserFactory, OrderFactory,
    WebsiteFactory, ClientWalletFactory
)
```

**Fix Required:**
1. Check if `backend/tests/factories.py` exists
2. Create if missing with all required factories
3. Ensure factories match fixture patterns in `conftest.py`

---

### 3. **Database Migration Issues** ⚠️

**Problem**: Migrations may not be running correctly in CI

**Current Setup:**
- Migrations run before tests: ✅
- But test database may not match expected schema

**Fix Required:**
1. Verify migrations complete successfully
2. Check for migration conflicts
3. Ensure test database is properly isolated

---

### 4. **Environment Variable Mismatch** ⚠️

**Problem**: CI sets `DATABASE_URL` but Django may not use it

**Current CI Setup:**
```yaml
env:
  DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
  SECRET_KEY: test-secret-key-for-ci
  DEBUG: 'False'
  REDIS_URL: redis://localhost:6379/0
```

**Django Settings:**
- May not be reading `DATABASE_URL` correctly
- May need `TEST_DB=postgres` to use PostgreSQL

**Fix Required:**
1. Update settings to read `DATABASE_URL` for tests
2. Or set `TEST_DB=postgres` in CI environment
3. Ensure database connection works

---

## 🔧 **Recommended Fixes**

### Fix 1: Update pytest.ini for CI

**File**: `backend/pytest.ini`

**Change:**
```ini
[pytest]
# Use test settings that handle DATABASE_URL
DJANGO_SETTINGS_MODULE = writing_system.settings_test
```

**Or add environment variable in CI:**
```yaml
env:
  DJANGO_SETTINGS_MODULE: writing_system.settings_test
  TEST_DB: postgres
```

---

### Fix 2: Update settings_test.py to Use DATABASE_URL

**File**: `backend/writing_system/settings_test.py`

**Add:**
```python
import os
from urllib.parse import urlparse

# Check for DATABASE_URL first (for CI/CD)
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Parse DATABASE_URL
    parsed = urlparse(database_url)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path[1:],  # Remove leading /
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or 5432,
        }
    }
elif os.getenv("TEST_DB", "sqlite").lower() == "postgres":
    # Existing postgres setup
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB_NAME", "penman_db"),
            "USER": os.getenv("POSTGRES_USER_NAME", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": int(os.getenv("DB_PORT", 5432)),
        }
    }
else:
    # SQLite fallback
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_db.sqlite3",
        }
    }
```

---

### Fix 3: Create Missing Test Factories

**File**: `backend/tests/factories.py` (create if missing)

**Content:**
```python
"""
Test factories for creating test data.
"""
import factory
from django.contrib.auth import get_user_model
from websites.models import Website
from orders.models import Order
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class WebsiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Website
    
    domain = factory.Sequence(lambda n: f"test{n}.local")
    name = factory.Sequence(lambda n: f"Test Website {n}")
    slug = factory.Sequence(lambda n: f"test-{n}")
    is_active = True


class ClientUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"client{n}")
    email = factory.Sequence(lambda n: f"client{n}@test.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = 'client'
    is_active = True
    website = factory.SubFactory(WebsiteFactory)


class WriterUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"writer{n}")
    email = factory.Sequence(lambda n: f"writer{n}@test.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = 'writer'
    is_active = True
    website = factory.SubFactory(WebsiteFactory)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    
    client = factory.SubFactory(ClientUserFactory)
    website = factory.SubFactory(WebsiteFactory)
    topic = factory.Sequence(lambda n: f"Test Order {n}")
    number_of_pages = 5
    total_price = Decimal('100.00')
    status = 'draft'
    client_deadline = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=7)
    )


class ClientWalletFactory(factory.django.DjangoModelFactory):
    # Adjust based on actual wallet model
    class Meta:
        model = 'client_wallet.ClientWallet'  # Update with actual model
    
    user = factory.SubFactory(ClientUserFactory)
    balance = Decimal('0.00')
```

---

### Fix 4: Update CI/CD Workflow

**File**: `.github/workflows/test.yml`

**Add to backend-tests job:**
```yaml
- name: Run backend tests
  working-directory: ./backend
  env:
    DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
    SECRET_KEY: test-secret-key-for-ci
    DEBUG: 'False'
    REDIS_URL: redis://localhost:6379/0
    DJANGO_SETTINGS_MODULE: writing_system.settings_test  # Add this
    TEST_DB: postgres  # Add this
  run: |
    pytest \
      --cov=. \
      --cov-report=xml \
      --cov-report=html \
      --cov-report=term \
      --junitxml=junit.xml \
      -v \
      --maxfail=10
```

---

## 🧪 **Testing the Fixes**

### Step 1: Test Locally with PostgreSQL

```bash
cd backend
export DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_db
export TEST_DB=postgres
export DJANGO_SETTINGS_MODULE=writing_system.settings_test
pytest -v --tb=short
```

### Step 2: Test with SQLite (Fallback)

```bash
cd backend
export TEST_DB=sqlite
export DJANGO_SETTINGS_MODULE=writing_system.settings_test
pytest -v --tb=short
```

### Step 3: Verify CI/CD

1. Push changes
2. Check GitHub Actions logs
3. Verify all tests pass
4. Check coverage reports

---

## 📋 **Checklist**

- [ ] Update `pytest.ini` or add `DJANGO_SETTINGS_MODULE` to CI
- [ ] Update `settings_test.py` to use `DATABASE_URL`
- [ ] Create `tests/factories.py` if missing
- [ ] Update CI/CD workflow with test settings
- [ ] Test locally with PostgreSQL
- [ ] Test locally with SQLite
- [ ] Verify CI/CD passes
- [ ] Check test coverage

---

## 🚨 **Common Test Failure Patterns**

### Pattern 1: Database Connection Errors
**Symptom**: `django.db.utils.OperationalError: could not connect to server`
**Fix**: Ensure PostgreSQL service is running and accessible

### Pattern 2: Migration Errors
**Symptom**: `django.db.migrations.exceptions.InconsistentMigrationHistory`
**Fix**: Run `python manage.py migrate --run-syncdb` or reset test database

### Pattern 3: Missing Fixtures
**Symptom**: `fixture 'xyz' not found`
**Fix**: Check `conftest.py` for fixture definitions

### Pattern 4: Import Errors
**Symptom**: `ModuleNotFoundError: No module named 'tests.factories'`
**Fix**: Create `tests/factories.py` or update imports

### Pattern 5: Settings Errors
**Symptom**: `django.core.exceptions.ImproperlyConfigured`
**Fix**: Ensure correct settings module and environment variables

---

## 📊 **Expected Outcomes**

After fixes:
- ✅ All tests run in CI/CD
- ✅ Tests use PostgreSQL in CI
- ✅ Tests use SQLite locally (fallback)
- ✅ Test coverage maintained
- ✅ No database connection errors
- ✅ No migration errors
- ✅ All fixtures available

---

**Next Steps**: Implement fixes and verify CI/CD passes

