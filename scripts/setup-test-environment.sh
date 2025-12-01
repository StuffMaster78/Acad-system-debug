#!/bin/bash

# Setup Test Environment Script
# This script sets up a local Python virtual environment for running backend tests

set -e  # Exit on error

echo "🧪 Setting up test environment for Writing System Platform"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Found Python ${PYTHON_VERSION}"

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || exit 1

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment"
        source venv/bin/activate
        echo "✅ Virtual environment activated"
        echo ""
        echo "Installing/updating dependencies..."
        pip install --upgrade pip -q
        pip install -r requirements.txt -q
        echo "✅ Dependencies installed"
        echo ""
        echo -e "${GREEN}✅ Test environment ready!${NC}"
        echo ""
        echo "To activate the environment manually:"
        echo "  source backend/venv/bin/activate"
        echo ""
        echo "To run tests:"
        echo "  pytest"
        exit 0
    fi
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📥 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

echo ""
echo -e "${GREEN}✅ Test environment setup complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To activate the environment:"
echo "  source backend/venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest                    # Run all tests"
echo "  pytest -v                  # Verbose output"
echo "  pytest --cov=. --cov-report=html  # With coverage"
echo "  pytest -m unit             # Run only unit tests"
echo "  pytest tests/examples/     # Run example tests"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

