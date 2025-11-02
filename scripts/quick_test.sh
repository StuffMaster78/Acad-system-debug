#!/bin/bash

# Quick End-to-End Test Script
echo "🧪 Quick E2E Test - Writing System Backend"
echo "=========================================="

# Check containers
echo ""
echo "📦 Container Status:"
docker-compose ps

echo ""
echo "🔍 Testing Services..."

# Test database
echo -n "  Database: "
if docker-compose exec -T db pg_isready -U ${POSTGRES_USER_NAME:-awinorick} > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not accessible"
fi

# Test Redis
echo -n "  Redis: "
if docker-compose exec -T redis redis-cli -a ${REDIS_PASSWORD:-redis_password_123} ping > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not accessible"
fi

# Test Django
echo -n "  Django: "
if docker-compose exec -T web python -c "import django; print('OK')" > /dev/null 2>&1; then
    echo "✅ Importing"
else
    echo "❌ Import error"
fi

# Test API
echo -n "  API Server: "
if curl -s http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "✅ Responding"
else
    echo "⏳ Starting..."
fi

echo ""
echo "✅ Quick check complete!"
echo ""
echo "To run full tests:"
echo "  docker-compose exec web python manage.py test"
echo ""
echo "To check migrations:"
echo "  docker-compose exec web python manage.py makemigrations --dry-run"

