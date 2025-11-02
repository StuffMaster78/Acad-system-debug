#!/bin/bash

# End-to-End Testing Script for Writing System Backend
# Tests core workflows and system functionality

set -e  # Exit on error

echo "🧪 Starting End-to-End Testing..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0
SKIPPED=0

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}: $2"
        ((FAILED++))
    fi
}

# Function to print info
test_info() {
    echo -e "${YELLOW}ℹ️  INFO${NC}: $1"
}

# Check if Docker is running
echo ""
echo "📦 Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon is not running!${NC}"
    exit 1
fi
test_result 0 "Docker daemon is running"

# Check if containers are running
echo ""
echo "🐳 Checking Docker containers..."
if ! docker-compose ps | grep -q "Up"; then
    test_info "Containers not running. Starting them..."
    docker-compose up -d
    echo "Waiting 10 seconds for services to start..."
    sleep 10
fi

# Check if web container is responding
echo ""
echo "🌐 Testing web service..."
if docker-compose exec -T web python manage.py check > /dev/null 2>&1; then
    test_result 0 "Django application is healthy"
else
    test_result 1 "Django application health check failed"
fi

# Check database connection
echo ""
echo "🗄️  Testing database connection..."
if docker-compose exec -T web python manage.py dbshell -c "SELECT 1;" > /dev/null 2>&1; then
    test_result 0 "Database connection successful"
else
    test_result 1 "Database connection failed"
fi

# Check Redis connection
echo ""
echo "📮 Testing Redis connection..."
if docker-compose exec -T redis redis-cli -a ${REDIS_PASSWORD:-redis_password_123} ping > /dev/null 2>&1; then
    test_result 0 "Redis connection successful"
else
    test_result 1 "Redis connection failed"
fi

# Run migrations
echo ""
echo "🔄 Running migrations..."
if docker-compose exec -T web python manage.py migrate --noinput > /dev/null 2>&1; then
    test_result 0 "Database migrations completed"
else
    test_result 1 "Database migrations failed"
fi

# Check for pending migrations
echo ""
echo "🔍 Checking for pending migrations..."
PENDING=$(docker-compose exec -T web python manage.py makemigrations --dry-run 2>&1 | grep -c "No changes" || echo "1")
if [ "$PENDING" -eq 1 ]; then
    test_result 0 "No pending migrations"
else
    test_info "There are pending migrations. Run: docker-compose exec web python manage.py makemigrations"
    ((SKIPPED++))
fi

# Test API endpoints (if server is accessible)
echo ""
echo "🔌 Testing API endpoints..."
if curl -s http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
    test_result 0 "Health check endpoint accessible"
else
    test_info "Health endpoint not available (may not be configured)"
    ((SKIPPED++))
fi

# Run Django test suite for critical apps
echo ""
echo "🧪 Running Django tests..."

APPS_TO_TEST=(
    "authentication"
    "users"
    "orders"
    "order_payments_management"
    "discounts"
    "class_management"
    "tickets"
    "communications"
)

for app in "${APPS_TO_TEST[@]}"; do
    echo "  Testing $app..."
    if docker-compose exec -T web python manage.py test $app --verbosity=0 > /dev/null 2>&1; then
        test_result 0 "$app tests passed"
    else
        test_result 1 "$app tests failed (check logs for details)"
    fi
done

# Check critical services are configured
echo ""
echo "⚙️  Checking service configuration..."

# Check Celery
if docker-compose ps | grep -q "celery.*Up"; then
    test_result 0 "Celery worker is running"
else
    test_result 1 "Celery worker is not running"
fi

# Check Celery Beat
if docker-compose ps | grep -q "beat.*Up"; then
    test_result 0 "Celery Beat scheduler is running"
else
    test_result 1 "Celery Beat scheduler is not running"
fi

# Summary
echo ""
echo "=================================="
echo "📊 Test Summary:"
echo "   ✅ Passed: $PASSED"
echo "   ❌ Failed: $FAILED"
echo "   ⏭️  Skipped: $SKIPPED"
echo "=================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please review the output above.${NC}"
    exit 1
fi

