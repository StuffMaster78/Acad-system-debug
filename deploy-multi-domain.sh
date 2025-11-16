#!/bin/bash

# Multi-Domain Deployment Script
# Usage: ./deploy-multi-domain.sh [environment]
# Environment: dev, prod (default: prod)

set -e

ENVIRONMENT=${1:-prod}

echo "🚀 Starting multi-domain deployment for environment: $ENVIRONMENT"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy env.template to .env and configure your settings:"
    echo "   cp env.template .env"
    echo "   nano .env"
    exit 1
fi

# Load environment variables
source .env

echo "📋 Environment Configuration:"
echo "   - Database: $POSTGRES_DB_NAME"
echo "   - Redis: $REDIS_HOST:$REDIS_PORT"
echo "   - Debug: $DEBUG"

if [ "$ENVIRONMENT" = "prod" ]; then
    echo "🏭 Deploying to PRODUCTION environment"
    
    # Build frontend dashboards
    echo "📦 Building frontend dashboards..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "📥 Installing frontend dependencies..."
        npm install
    fi
    
    echo "🔨 Building Writer Dashboard..."
    npm run build:writers || echo "⚠️  Warning: build:writers script not found, skipping..."
    
    echo "🔨 Building Client Dashboard..."
    npm run build:clients || echo "⚠️  Warning: build:clients script not found, skipping..."
    
    echo "🔨 Building Staff Dashboard..."
    npm run build:staff || echo "⚠️  Warning: build:staff script not found, skipping..."
    
    cd ..
    
    # Production deployment
    echo "📦 Building production images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    echo "🛑 Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down
    
    echo "🗄️  Creating volumes..."
    docker volume create writing_system_postgres_data 2>/dev/null || true
    docker volume create writing_system_redis_data 2>/dev/null || true
    
    echo "🚀 Starting production services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 30
    
    echo "🔧 Running database migrations..."
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate
    
    echo "📊 Collecting static files..."
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
    
    echo "✅ Production deployment complete!"
    echo ""
    echo "🌐 Dashboards available at:"
    echo "   - Writers: https://writers.yourdomain.com"
    echo "   - Clients: https://clients.yourdomain.com"
    echo "   - Staff: https://staff.yourdomain.com"
    echo ""
    echo "📝 Note: Update 'yourdomain.com' with your actual domain in:"
    echo "   - nginx-multi-domain.conf"
    echo "   - .env file (CORS_ALLOWED_ORIGINS)"
    echo "   - Django settings (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS)"
    
else
    echo "🔧 Deploying to DEVELOPMENT environment"
    
    # Development deployment
    echo "📦 Building development images..."
    docker-compose build
    
    echo "🛑 Stopping existing containers..."
    docker-compose down
    
    echo "🚀 Starting development services..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 15
    
    echo "🔧 Running database migrations..."
    docker-compose exec -T web python manage.py migrate
    
    echo "✅ Development deployment complete!"
    echo "🌐 Backend available at: http://localhost:8000"
    echo "🌐 Frontend available at: http://localhost:3000"
fi

echo ""
echo "📊 To view logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🔍 To check service status:"
echo "   docker-compose -f docker-compose.prod.yml ps"

