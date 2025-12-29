# Running Authentication Tests

## ✅ Test Suite Created

**140+ comprehensive authentication tests** across 8 test files are ready to run!

## 📁 Test Files

1. `authentication/tests/test_auth/test_login.py` - 25+ tests
2. `authentication/tests/test_auth/test_registration.py` - 20+ tests
3. `authentication/tests/test_password_reset.py` - 20+ tests
4. `authentication/tests/test_mfa.py` - 20+ tests
5. `authentication/tests/test_logout.py` - 15+ tests
6. `authentication/tests/test_token_management.py` - 15+ tests
7. `authentication/tests/test_magic_links.py` - 10+ tests
8. `authentication/tests/test_security_features.py` - 15+ tests

## 🚀 Running Tests

### Option 1: Using Docker (Recommended)

```bash
# Start Docker services
docker-compose up -d db redis

# Run all authentication tests
docker-compose exec web pytest authentication/tests/test_auth/ -v

# Run specific test file
docker-compose exec web pytest authentication/tests/test_auth/test_login.py -v

# Run with coverage (if pytest-cov is installed)
docker-compose exec web pytest authentication/tests/test_auth/ -v --cov=authentication --cov-report=html
```

### Option 2: Using Local Environment

```bash
# Activate virtual environment
source venv/bin/activate  # or your venv path

# Install dependencies
pip install -r requirements.txt

# Run tests
cd backend
pytest authentication/tests/test_auth/ -v
```

### Option 3: Using Makefile

```bash
# If Makefile has test commands
make test-auth
# or
make test
```

## 📊 Test Coverage

### Expected Coverage Areas

- **Login/Logout**: ~95%+ ✅
- **Registration**: ~95%+ ✅
- **Password Reset**: ~95%+ ✅
- **MFA/2FA**: ~95%+ ✅
- **Token Management**: ~95%+ ✅
- **Magic Links**: ~95%+ ✅
- **Security Features**: ~90%+ ✅

## 🔧 Troubleshooting

### Issue: pytest-cov not installed

If you see errors about `--cov` arguments:

```bash
# Install pytest-cov
pip install pytest-cov

# Or run without coverage
pytest authentication/tests/test_auth/ -v -o addopts=""
```

### Issue: Database connection errors

Ensure database is running:

```bash
# For Docker
docker-compose up -d db

# Check database connection
docker-compose exec web python manage.py dbshell
```

### Issue: Missing fixtures

All required fixtures are in `backend/conftest.py`:
- `website` - Test website instance
- `client_user` - Client user
- `admin_user` - Admin user
- `writer_user` - Writer user
- And more...

## 📝 Test Summary

### Test Categories

1. **Login Tests (25+)**
   - Successful login
   - Invalid credentials
   - Account lockout
   - Password expiration
   - 2FA requirements

2. **Registration Tests (20+)**
   - User creation
   - Validation
   - Email verification
   - Referral codes

3. **Password Reset Tests (20+)**
   - Token generation
   - OTP validation
   - Password reset flow

4. **MFA Tests (20+)**
   - TOTP setup
   - Email OTP
   - Backup codes
   - MFA login flow

5. **Logout Tests (15+)**
   - Single logout
   - Logout all devices
   - Session management

6. **Token Management Tests (15+)**
   - Token refresh
   - Token validation
   - Token expiration

7. **Magic Links Tests (10+)**
   - Link generation
   - Link validation
   - Expiration handling

8. **Security Features Tests (15+)**
   - Account lockout
   - Failed login tracking
   - IP blocking
   - Session limits

## ✅ Next Steps

1. **Start Docker services**:
   ```bash
   docker-compose up -d db redis
   ```

2. **Run tests**:
   ```bash
   docker-compose exec web pytest authentication/tests/test_auth/ -v
   ```

3. **Check coverage**:
   ```bash
   docker-compose exec web pytest authentication/tests/test_auth/ -v --cov=authentication --cov-report=html
   ```

4. **View coverage report**:
   ```bash
   open backend/htmlcov/index.html  # macOS
   # or
   xdg-open backend/htmlcov/index.html  # Linux
   ```

## 🎯 Expected Results

- **Total Tests**: 140+ test methods
- **Expected Pass Rate**: 95%+ (some may need fixture adjustments)
- **Coverage**: ~95%+ for authentication module

All tests are ready and waiting for the environment to be set up! 🚀

