#!/bin/bash

echo "=========================================="
echo "FRONTEND-BACKEND INTEGRATION TESTS"
echo "=========================================="
echo ""

# Check if backend is running
echo "▶ Checking backend status..."
if ! docker-compose ps web | grep -q "Up"; then
    echo "❌ Backend is not running. Starting..."
    docker-compose up -d web
    echo "⏳ Waiting for backend to start..."
    sleep 10
    
    # Check if it started successfully
    if ! docker-compose ps web | grep -q "Up"; then
        echo "❌ Failed to start backend"
        exit 1
    fi
fi

echo "✅ Backend container is running"

 # Check if backend is actually responding (accept 200/404/405/429)
echo ""
echo "▶ Checking if backend is responding..."

BACKEND_OK=false
for i in {1..15}; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/ || echo "000")
  if echo "$HTTP_CODE" | grep -qE "200|404|405|429"; then
    BACKEND_OK=true
    break
  fi
  if [ $i -eq 1 ]; then
    echo "⚠️  Backend not ready yet (HTTP $HTTP_CODE). Waiting..."
  fi
  sleep 2
done

if [ "$BACKEND_OK" = true ]; then
  echo "✅ Backend is responding on http://localhost:8000 (HTTP $HTTP_CODE)"
else
  echo "⚠️  Backend container is running but not responding on port 8000"
  echo "Checking logs..."
  docker-compose logs web --tail 20
  echo ""
  echo "Trying to start backend again..."
  docker-compose restart web
  echo "Waiting for backend to start..."
  sleep 8
fi

# Check frontend (optional)
echo ""
echo "▶ Checking frontend status..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5175 | grep -qE "200|404"; then
    echo "✅ Frontend is running on http://localhost:5175"
else
    echo "⚠️  Frontend is not running (optional for backend tests)"
fi

# Run backend integration test
echo ""
echo "▶ Running backend integration tests..."
echo "   (Note: Running from inside Docker container)"
echo ""

# Run test from inside container (has Django available)
# Try to use timeout if available (Linux), otherwise run without it (macOS)
if command -v timeout >/dev/null 2>&1; then
    # Linux: Use timeout command
    timeout 60 docker-compose exec -T -e API_BASE_URL=http://localhost:8000/api/v1 web python test_frontend_backend_integration.py 2>&1
    TEST_EXIT_CODE=$?
    
    if [ $TEST_EXIT_CODE -eq 124 ]; then
        echo ""
        echo "❌ Test script timed out after 60 seconds"
        TEST_EXIT_CODE=1
    fi
else
    # macOS/BSD: Run without timeout (Python has its own timeouts)
    echo "   (Note: timeout command not available, using Python's internal timeouts)"
    docker-compose exec -T -e API_BASE_URL=http://localhost:8000/api/v1 web python test_frontend_backend_integration.py 2>&1
    TEST_EXIT_CODE=$?
fi

echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Tests completed successfully!"
else
    echo "❌ Tests completed with errors"
fi
echo "=========================================="

exit $TEST_EXIT_CODE
