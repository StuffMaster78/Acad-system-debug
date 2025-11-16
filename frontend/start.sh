#!/bin/bash

# Frontend Quick Start Script

echo "🚀 Starting Writing System Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
# Environment Variables
VUE_APP_API_URL=http://localhost:8000/api/v1
VUE_APP_NAME=Writing System
VUE_APP_VERSION=1.0.0
VUE_APP_ENV=development

# Feature Flags
VUE_APP_ENABLE_2FA=true
VUE_APP_ENABLE_MAGIC_LINK=true
EOF
    echo "✅ .env file created"
    echo ""
fi

echo "🎯 Starting development server..."
echo "📍 Frontend will be available at: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000/api/v1"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev

