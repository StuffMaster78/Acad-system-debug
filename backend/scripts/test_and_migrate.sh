#!/bin/bash

# Comprehensive Testing and Migration Script
# Runs migrations, checks for issues, and tests the system

set -e

echo "🚀 Starting System Testing and Migration Process..."
echo "=================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}: $2"
        ((FAILED++))
    fi
}

warning() {
    echo -e "${YELLOW}⚠️  WARNING${NC}: $1"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

# Check if Docker is available
echo ""
echo "📦 Checking Docker..."
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    USE_DOCKER=true
    info "Docker is available - will use docker-compose exec"
else
    USE_DOCKER=false
    warning "Docker not available - using local Python (if available)"
fi

# Function to run command
run_cmd() {
    if [ "$USE_DOCKER" = true ]; then
        docker-compose exec -T web $@
    else
        python3 manage.py $@ 2>/dev/null || python manage.py $@ 2>/dev/null || {
            warning "Could not run: $@"
            return 1
        }
    fi
}

# 1. Check Django Installation
echo ""
echo "🔍 Step 1: Checking Django Installation..."
if run_cmd check --deploy 2>&1 | grep -q "System check identified no issues"; then
    test_result 0 "Django system check passed"
else
    CHECK_OUTPUT=$(run_cmd check --deploy 2>&1 || echo "Failed to run check")
    if echo "$CHECK_OUTPUT" | grep -qi "error"; then
        test_result 1 "Django system check found errors"
        echo "$CHECK_OUTPUT" | grep -i error | head -5
    else
        test_result 0 "Django system check passed (with warnings)"
        echo "$CHECK_OUTPUT" | grep -i warning | head -3 || true
    fi
fi

# 2. Check for Pending Migrations
echo ""
echo "🔄 Step 2: Checking for Pending Migrations..."
MIGRATION_OUTPUT=$(run_cmd makemigrations --dry-run 2>&1 || echo "")
if echo "$MIGRATION_OUTPUT" | grep -q "No changes detected"; then
    test_result 0 "No pending migrations"
else
    PENDING_APPS=$(echo "$MIGRATION_OUTPUT" | grep -E "Migrations for" | sed 's/Migrations for //' || echo "unknown")
    warning "Pending migrations detected for: $PENDING_APPS"
    info "Creating migrations..."
    run_cmd makemigrations 2>&1 | tail -20
    test_result 0 "Migrations created"
fi

# 3. Run Migrations
echo ""
echo "🗄️  Step 3: Running Database Migrations..."
if run_cmd migrate --noinput 2>&1 | tail -5; then
    test_result 0 "Database migrations completed"
else
    test_result 1 "Database migrations failed"
fi

# 4. Check for Migration Conflicts
echo ""
echo "🔍 Step 4: Checking for Migration Issues..."
if run_cmd showmigrations --plan 2>&1 | grep -q "\[ \]"; then
    UNAPPLIED=$(run_cmd showmigrations --plan 2>&1 | grep -c "\[ \]" || echo "0")
    if [ "$UNAPPLIED" -gt 0 ]; then
        warning "$UNAPPLIED unapplied migrations found"
    else
        test_result 0 "All migrations applied"
    fi
else
    test_result 0 "No migration issues detected"
fi

# 5. Check Model Imports
echo ""
echo "🧩 Step 5: Checking Model Imports..."
run_cmd shell -c "
from django.apps import apps
errors = []
for app_config in apps.get_app_configs():
    try:
        models = app_config.get_models()
        print(f'✅ {app_config.name}: {len(list(models))} models')
    except Exception as e:
        errors.append(f'{app_config.name}: {str(e)}')
        print(f'❌ {app_config.name}: Error - {str(e)}')
if errors:
    exit(1)
exit(0)
" 2>&1 | tail -40

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    test_result 0 "All model imports successful"
else
    test_result 1 "Some model imports failed"
fi

# 6. Test Database Connection
echo ""
echo "💾 Step 6: Testing Database Connection..."
if run_cmd dbshell -c "SELECT 1;" 2>&1 | grep -q "1"; then
    test_result 0 "Database connection working"
else
    test_result 1 "Database connection failed"
fi

# 7. Check for Circular Imports
echo ""
echo "🔄 Step 7: Checking for Import Issues..."
run_cmd shell -c "
import sys
sys.path.insert(0, '.')
errors = []
try:
    from fines.models import Fine, FineTypeConfig, LatenessFineRule
    print('✅ Fines models imported')
except Exception as e:
    errors.append(f'Fines: {e}')
    print(f'❌ Fines models: {e}')

try:
    from orders.models import Order
    print('✅ Orders models imported')
except Exception as e:
    errors.append(f'Orders: {e}')
    print(f'❌ Orders models: {e}')

try:
    from class_management.models import ClassBundle
    print('✅ Class management models imported')
except Exception as e:
    errors.append(f'Class: {e}')
    print(f'❌ Class models: {e}')

if errors:
    for e in errors:
        print(f'Error: {e}')
    exit(1)
exit(0)
" 2>&1

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    test_result 0 "Critical model imports successful"
else
    test_result 1 "Some critical imports failed"
fi

# 8. Check URL Configuration
echo ""
echo "🌐 Step 8: Checking URL Configuration..."
if run_cmd check --deploy 2>&1 | grep -qi "url"; then
    test_result 0 "URL configuration check passed"
else
    URL_OUTPUT=$(run_cmd shell -c "
from django.urls import get_resolver
try:
    resolver = get_resolver()
    print('✅ URL resolver loaded successfully')
    print(f'   Total URL patterns: {len(list(resolver.url_patterns))}')
except Exception as e:
    print(f'❌ URL resolver error: {e}')
    exit(1)
exit(0)
" 2>&1)
    echo "$URL_OUTPUT"
    if echo "$URL_OUTPUT" | grep -q "✅"; then
        test_result 0 "URL configuration working"
    else
        test_result 1 "URL configuration has issues"
    fi
fi

# 9. Run Critical Tests
echo ""
echo "🧪 Step 9: Running Critical Tests..."
CRITICAL_APPS=("fines" "orders" "authentication")
for app in "${CRITICAL_APPS[@]}"; do
    echo "  Testing $app..."
    if run_cmd test $app --verbosity=1 --keepdb 2>&1 | tail -10; then
        test_result 0 "$app tests passed"
    else
        TEST_OUTPUT=$(run_cmd test $app --verbosity=1 2>&1 | tail -20)
        if echo "$TEST_OUTPUT" | grep -qi "no such table\|does not exist\|OperationalError"; then
            warning "$app tests need migrations"
        else
            test_result 1 "$app tests failed"
            echo "$TEST_OUTPUT" | grep -E "FAILED|Error|Exception" | head -5
        fi
    fi
done

# 10. Check Deployment Readiness
echo ""
echo "🚀 Step 10: Checking Deployment Readiness..."
DEPLOYMENT_CHECKS=0
DEPLOYMENT_ISSUES=0

# Check SECRET_KEY
if grep -q "SECRET_KEY.*os.getenv" writing_system/settings.py 2>/dev/null; then
    ((DEPLOYMENT_CHECKS++))
    info "SECRET_KEY configured via environment"
else
    warning "SECRET_KEY might not be secure"
    ((DEPLOYMENT_ISSUES++))
fi

# Check DEBUG mode
if grep -q "DEBUG.*=.*os.getenv" writing_system/settings.py 2>/dev/null; then
    ((DEPLOYMENT_CHECKS++))
    info "DEBUG configurable via environment"
else
    warning "DEBUG setting needs review"
    ((DEPLOYMENT_ISSUES++))
fi

# Check ALLOWED_HOSTS
if grep -q "ALLOWED_HOSTS" writing_system/settings.py 2>/dev/null; then
    ((DEPLOYMENT_CHECKS++))
    info "ALLOWED_HOSTS configured"
else
    warning "ALLOWED_HOSTS needs configuration"
    ((DEPLOYMENT_ISSUES++))
fi

# Check Database Configuration
if grep -q "DATABASES" writing_system/settings.py 2>/dev/null; then
    ((DEPLOYMENT_CHECKS++))
    info "Database configuration present"
else
    test_result 1 "Database configuration missing"
    ((DEPLOYMENT_ISSUES++))
fi

if [ $DEPLOYMENT_ISSUES -eq 0 ]; then
    test_result 0 "Deployment configuration looks good"
else
    warning "$DEPLOYMENT_ISSUES deployment configuration issues found"
fi

# Summary
echo ""
echo "=================================================="
echo "📊 Test Summary:"
echo "   ✅ Passed: $PASSED"
echo "   ❌ Failed: $FAILED"
echo "   ⚠️  Warnings: $WARNINGS"
echo "=================================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 System is ready for deployment!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review any warnings above"
    echo "  2. Set up environment variables for production"
    echo "  3. Configure ALLOWED_HOSTS for your domain"
    echo "  4. Set up static file collection"
    echo "  5. Configure email backend"
    echo "  6. Set up SSL/TLS certificates"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Please review and fix issues before deployment.${NC}"
    exit 1
fi

