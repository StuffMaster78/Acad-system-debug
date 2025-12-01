#!/bin/bash

# Run All Tests Script
# This script runs both backend and frontend tests with proper setup

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧪 Running All Tests - Writing System Platform${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Parse command line arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false
WITH_COVERAGE=false
VERBOSE=false

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
        --coverage)
            WITH_COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only    Run only backend tests"
            echo "  --frontend-only   Run only frontend tests"
            echo "  --coverage        Generate coverage reports"
            echo "  --verbose, -v     Verbose output"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run backend tests
run_backend_tests() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔧 Backend Tests${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    cd "$PROJECT_ROOT/backend"
    
    # Check if using Docker
    if command_exists docker-compose && docker-compose ps >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Docker detected, using Docker for tests"
        echo ""
        
        if [ "$WITH_COVERAGE" = true ]; then
            docker-compose exec -T web pytest --cov=. --cov-report=html --cov-report=term -v
        else
            if [ "$VERBOSE" = true ]; then
                docker-compose exec -T web pytest -v
            else
                docker-compose exec -T web pytest
            fi
        fi
    else
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
            echo "Setting up test environment..."
            "$SCRIPT_DIR/setup-test-environment.sh"
        fi
        
        # Activate virtual environment
        if [ -d "venv" ]; then
            source venv/bin/activate
            echo -e "${GREEN}✓${NC} Virtual environment activated"
        else
            echo -e "${RED}❌ Failed to set up virtual environment${NC}"
            exit 1
        fi
        
        echo ""
        
        # Run tests
        if [ "$WITH_COVERAGE" = true ]; then
            pytest --cov=. --cov-report=html --cov-report=term -v
        else
            if [ "$VERBOSE" = true ]; then
                pytest -v
            else
                pytest
            fi
        fi
    fi
    
    echo ""
    echo -e "${GREEN}✅ Backend tests completed${NC}"
    echo ""
}

# Function to run frontend tests
run_frontend_tests() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🎨 Frontend Tests${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules not found, installing dependencies...${NC}"
        npm install
    fi
    
    echo ""
    
    # Run tests
    if [ "$WITH_COVERAGE" = true ]; then
        npm run test:coverage
    else
        npm run test:run
    fi
    
    echo ""
    echo -e "${GREEN}✅ Frontend tests completed${NC}"
    echo ""
}

# Main execution
BACKEND_FAILED=false
FRONTEND_FAILED=false

# Run backend tests
if [ "$FRONTEND_ONLY" = false ]; then
    if run_backend_tests; then
        echo ""
    else
        BACKEND_FAILED=true
        echo -e "${RED}❌ Backend tests failed${NC}"
        echo ""
    fi
fi

# Run frontend tests
if [ "$BACKEND_ONLY" = false ]; then
    if run_frontend_tests; then
        echo ""
    else
        FRONTEND_FAILED=true
        echo -e "${RED}❌ Frontend tests failed${NC}"
        echo ""
    fi
fi

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Test Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_ONLY" = false ]; then
    if [ "$BACKEND_FAILED" = false ] && [ "$FRONTEND_FAILED" = false ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        [ "$BACKEND_FAILED" = true ] && echo -e "${RED}  - Backend tests failed${NC}"
        [ "$FRONTEND_FAILED" = true ] && echo -e "${RED}  - Frontend tests failed${NC}"
        exit 1
    fi
elif [ "$BACKEND_ONLY" = true ]; then
    if [ "$BACKEND_FAILED" = false ]; then
        echo -e "${GREEN}✅ Backend tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Backend tests failed${NC}"
        exit 1
    fi
elif [ "$FRONTEND_ONLY" = true ]; then
    if [ "$FRONTEND_FAILED" = false ]; then
        echo -e "${GREEN}✅ Frontend tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Frontend tests failed${NC}"
        exit 1
    fi
fi

