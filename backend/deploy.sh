#!/bin/bash

# Production Deployment Script for Writing System Backend
# Usage: ./deploy.sh [environment]
# Environment: dev, prod (default: dev)

set -e

ENVIRONMENT=${1:-dev}

echo "🚀 Starting deployment for environment: $ENVIRONMENT"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your settings:"
    echo "   cp .env.example .env"
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
    docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
    
    echo "📊 Collecting static files..."
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
    
    echo "✅ Production deployment complete!"
    echo "🌐 Application available at: http://localhost"
    
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
    sleep 20
    
    echo "🔧 Running database migrations..."
    docker-compose exec web python manage.py migrate
    
    echo "✅ Development deployment complete!"
    echo "🌐 Application available at: http://localhost:8000"
fi

echo ""
echo "📊 Service Status:"
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml ps
else
    docker-compose ps
fi

echo ""
echo "🔍 To view logs:"
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "   docker-compose -f docker-compose.prod.yml logs -f"
else
    echo "   docker-compose logs -f"
fi

echo ""
echo "🛑 To stop services:"
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "   docker-compose -f docker-compose.prod.yml down"
else
    echo "   docker-compose down"
fi
