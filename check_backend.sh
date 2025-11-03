#!/bin/bash

echo "=========================================="
echo "BACKEND HEALTH CHECK"
echo "=========================================="

# Check Docker containers
echo ""
echo "▶ Checking Docker containers..."
docker-compose ps

# Check if web container is running
if docker-compose ps web | grep -q "Up"; then
    echo "✅ Web container is running"
else
    echo "❌ Web container is not running"
    echo "Starting web container..."
    docker-compose up -d web
    sleep 5
fi

# Check if backend is responding
echo ""
echo "▶ Checking backend API..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/ | grep -q "200\|404"; then
    echo "✅ Backend is responding at http://localhost:8000/api/v1/"
    curl -s http://localhost:8000/api/v1/ | head -20
else
    echo "❌ Backend is not responding"
    echo ""
    echo "Checking logs..."
    docker-compose logs web --tail 30
fi

# Check inside container
echo ""
echo "▶ Checking from inside container..."
docker-compose exec -T web curl -s http://localhost:8000/api/v1/ 2>&1 | head -5 || echo "Cannot connect from inside container"

echo ""
echo "=========================================="

