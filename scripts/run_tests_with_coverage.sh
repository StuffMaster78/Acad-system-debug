#!/bin/bash

# Test Coverage Runner Script
# Runs tests and generates coverage reports for both backend and frontend
# Target: 95% coverage minimum

set -e

echo "🧪 Running Tests with Coverage Analysis"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in Docker or local
IN_DOCKER=false
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    IN_DOCKER=true
fi

# Function to run backend tests
run_backend_tests() {
    echo -e "${YELLOW}📦 Running Backend Tests...${NC}"
    echo ""
    
    if [ "$IN_DOCKER" = true ]; then
        cd /app/backend || cd backend
    else
        cd backend || { echo "❌ Backend directory not found"; exit 1; }
    fi
    
    # Check if pytest-cov is installed
    if ! python -c "import pytest_cov" 2>/dev/null; then
        echo "📥 Installing pytest-cov..."
        pip install pytest-cov pytest-xdist
    fi
    
    echo "Running pytest with 95% coverage requirement..."
    pytest \
        --cov=. \
        --cov-report=term-missing \
        --cov-report=html \
        --cov-report=xml \
        --cov-fail-under=95 \
        --junitxml=junit.xml \
        -v \
        -n auto || {
        echo -e "${RED}❌ Backend tests failed or coverage below 95%${NC}"
        echo ""
        echo "Coverage report generated at: backend/htmlcov/index.html"
        echo "View detailed coverage: open backend/htmlcov/index.html"
        return 1
    }
    
    echo -e "${GREEN}✅ Backend tests passed with 95%+ coverage${NC}"
    echo ""
    echo "📊 Coverage report: backend/htmlcov/index.html"
    echo "📊 Coverage XML: backend/coverage.xml"
    echo ""
}

# Function to run frontend tests
run_frontend_tests() {
    echo -e "${YELLOW}🎨 Running Frontend Tests...${NC}"
    echo ""
    
    if [ "$IN_DOCKER" = true ]; then
        cd /app/frontend || cd frontend
    else
        cd frontend || { echo "❌ Frontend directory not found"; exit 1; }
    fi
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📥 Installing dependencies..."
        npm install
    fi
    
    echo "Running Vitest with 95% coverage requirement..."
    npm run test:run -- --coverage \
        --coverage.threshold.lines=95 \
        --coverage.threshold.functions=95 \
        --coverage.threshold.branches=95 \
        --coverage.threshold.statements=95 || {
        echo -e "${RED}❌ Frontend tests failed or coverage below 95%${NC}"
        echo ""
        echo "Coverage report generated at: frontend/coverage/index.html"
        return 1
    }
    
    echo -e "${GREEN}✅ Frontend tests passed with 95%+ coverage${NC}"
    echo ""
    echo "📊 Coverage report: frontend/coverage/index.html"
    echo ""
}

# Main execution
BACKEND_ONLY=false
FRONTEND_ONLY=false
SHOW_REPORTS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --show-reports)
            SHOW_REPORTS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--backend-only] [--frontend-only] [--show-reports]"
            exit 1
            ;;
    esac
done

# Run tests
BACKEND_PASSED=true
FRONTEND_PASSED=true

if [ "$FRONTEND_ONLY" = false ]; then
    run_backend_tests || BACKEND_PASSED=false
fi

if [ "$BACKEND_ONLY" = false ]; then
    run_frontend_tests || FRONTEND_PASSED=false
fi

# Summary
echo "========================================"
echo "📊 Test Coverage Summary"
echo "========================================"

if [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_ONLY" = false ]; then
    if [ "$BACKEND_PASSED" = true ] && [ "$FRONTEND_PASSED" = true ]; then
        echo -e "${GREEN}✅ All tests passed with 95%+ coverage!${NC}"
        echo ""
        echo "📁 Coverage Reports:"
        echo "   Backend:  backend/htmlcov/index.html"
        echo "   Frontend: frontend/coverage/index.html"
        
        if [ "$SHOW_REPORTS" = true ]; then
            echo ""
            echo "Opening coverage reports..."
            if command -v open &> /dev/null; then
                open backend/htmlcov/index.html 2>/dev/null || true
                open frontend/coverage/index.html 2>/dev/null || true
            elif command -v xdg-open &> /dev/null; then
                xdg-open backend/htmlcov/index.html 2>/dev/null || true
                xdg-open frontend/coverage/index.html 2>/dev/null || true
            fi
        fi
        exit 0
    else
        echo -e "${RED}❌ Some tests failed or coverage below 95%${NC}"
        [ "$BACKEND_PASSED" = false ] && echo "   Backend: Failed"
        [ "$FRONTEND_PASSED" = false ] && echo "   Frontend: Failed"
        exit 1
    fi
elif [ "$BACKEND_ONLY" = true ]; then
    if [ "$BACKEND_PASSED" = true ]; then
        echo -e "${GREEN}✅ Backend tests passed with 95%+ coverage!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Backend tests failed or coverage below 95%${NC}"
        exit 1
    fi
elif [ "$FRONTEND_ONLY" = true ]; then
    if [ "$FRONTEND_PASSED" = true ]; then
        echo -e "${GREEN}✅ Frontend tests passed with 95%+ coverage!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Frontend tests failed or coverage below 95%${NC}"
        exit 1
    fi
fi

