#!/bin/bash

# Quick Test Script - Simplified version for immediate use

set -e

echo "🧪 Quick Test Runner"
echo ""

# Check if we're in the project root
if [ ! -f "Makefile" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Run frontend tests (always works)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 Running Frontend Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd frontend
npm run test:run
cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Frontend tests completed"
echo ""
echo "For backend tests, use one of these options:"
echo "  1. Docker: docker-compose up -d && make test-backend"
echo "  2. Local:  ./scripts/setup-test-environment.sh && cd backend && source venv/bin/activate && pytest"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

