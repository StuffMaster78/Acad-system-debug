# 🐳 Docker Deployment Guide

This guide covers deploying the Writing System Backend using Docker for both development and production environments.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd writing_system_backend
cp .env.example .env
# Edit .env with your configuration
nano .env
```

### 2. Development Deployment
```bash
# Using the deployment script
./deploy.sh dev

# Or manually
docker-compose up --build
```

### 3. Production Deployment
```bash
# Using the deployment script
./deploy.sh prod

# Or manually
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
SECRET_KEY=your-secret-key-here
POSTGRES_DB_NAME=writing_system_db
POSTGRES_USER_NAME=postgres
POSTGRES_PASSWORD=your-db-password-here
REDIS_PASSWORD=your-redis-password-here

# Optional
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your-email@gmail.com
AWS_ACCESS_KEY_ID=your-aws-key
```

## 🏗️ Architecture

### Development (docker-compose.yml)
- **web**: Django development server
- **db**: PostgreSQL 15
- **redis**: Redis with password
- **celery**: Background task worker
- **beat**: Celery beat scheduler
- **Volume mounts**: Live code reloading

### Production (docker-compose.prod.yml)
- **web**: Gunicorn WSGI server (3 workers)
- **db**: PostgreSQL 15 with persistent volume
- **redis**: Redis 7 with persistent volume
- **celery**: Background task worker
- **beat**: Celery beat scheduler
- **nginx**: Reverse proxy with rate limiting
- **No volume mounts**: Immutable containers

## 🔒 Security Features

### Dockerfile Security
- ✅ Multi-stage build for smaller images
- ✅ Non-root user (`appuser`)
- ✅ Minimal runtime dependencies
- ✅ Security headers and environment variables

### Production Security
- ✅ Nginx rate limiting
- ✅ Security headers (X-Frame-Options, X-XSS-Protection, etc.)
- ✅ Gzip compression
- ✅ Static file caching
- ✅ Health checks for all services

## 📊 Monitoring

### Health Checks
```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Check specific service
curl http://localhost:8000/health/
```

### Service Status
```bash
# Development
docker-compose ps

# Production
docker-compose -f docker-compose.prod.yml ps
```

## 🛠️ Management Commands

### Database Operations
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files (production)
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Celery Operations
```bash
# Check Celery status
docker-compose exec celery celery -A writing_system inspect ping

# View Celery logs
docker-compose logs -f celery
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
./deploy.sh [dev|prod]
```

### Backup Database
```bash
# Create backup
docker-compose exec db pg_dump -U $POSTGRES_USER_NAME $POSTGRES_DB_NAME > backup.sql

# Restore backup
docker-compose exec -T db psql -U $POSTGRES_USER_NAME $POSTGRES_DB_NAME < backup.sql
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or change port in docker-compose.yml
   ```

2. **Database connection failed**
   ```bash
   # Check database logs
   docker-compose logs db
   # Ensure environment variables are correct
   ```

3. **Permission denied**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Logs and Debugging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web

# Access container shell
docker-compose exec web bash
```

## 📈 Performance Optimization

### Production Optimizations
- Gunicorn with 3 workers
- Nginx reverse proxy
- Redis caching
- Static file serving
- Gzip compression
- Database connection pooling

### Resource Limits
```yaml
# Add to docker-compose.prod.yml services
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

## 🔐 Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup data regularly

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Check service health status
4. Review this documentation

---

**Happy Deploying! 🚀**
