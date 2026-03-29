# Production Deployment Guide

## Pre-Deployment Checklist

### ✅ Completed
- [x] All import conflicts resolved
- [x] All migration errors fixed
- [x] Migrations applied successfully
- [x] Static files collected
- [x] Default data initialized
- [x] System checks passing (0 errors)

### ⏳ Manual Steps Required
- [ ] Create superuser account
- [ ] Configure environment variables
- [ ] Set up database backups
- [ ] Configure SSL certificates
- [ ] Set up monitoring/logging

## Step 1: Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

Enter:
- Username
- Email address
- Password (twice)

## Step 2: Environment Variables

Create a `.env` file or set environment variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@db:5432/dbname
# OR
DB_NAME=writingsondo
DB_USER=awinorick
DB_PASSWORD=Nyakach2030
DB_HOST=db
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
CORS_ALLOW_CREDENTIALS=True

# Celery (if using)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# AWS/DigitalOcean Spaces (for file storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_REGION_NAME=nyc3
```

## Step 3: DigitalOcean Spaces Setup

### Create Spaces Bucket
1. Go to DigitalOcean → Spaces
2. Create a new Space in `nyc3` region
3. Note the endpoint URL
4. Generate API keys

### Configure Django Settings

Update `writing_system/settings.py` to use DigitalOcean Spaces:

```python
# Use DigitalOcean Spaces for file storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'nyc3')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
```

## Step 4: Database Backups

### Automated Backup Script

Create `scripts/backup_db.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

docker-compose exec -T db pg_dump -U awinorick writingsondo > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

### Schedule with Cron

```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * /path/to/scripts/backup_db.sh
```

## Step 5: Nginx Configuration

### Production Nginx Config

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 100M;

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

## Step 6: Deployment Steps

### 1. Build and Start Services
```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Run Migrations
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### 3. Collect Static Files
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 4. Initialize Default Data
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c "from fines.services.initialize_default_fine_types import initialize_default_fine_types; initialize_default_fine_types()"
```

### 5. Create Superuser
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Step 7: Monitoring

### Health Check Endpoint
Create a simple health check:

```python
# In your urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'timestamp': timezone.now()})
```

### Logging Configuration

Configure logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/app.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

## Step 8: Security Checklist

- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is secure and not committed
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] SSL certificates installed and working
- [ ] CORS configured correctly
- [ ] Database credentials secure
- [ ] API rate limiting configured
- [ ] Security headers configured (CSP, HSTS, etc.)

## Step 9: Performance Optimization

### Enable Gzip Compression
In Nginx config:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### Configure Caching
- Static files: Long-term caching
- API responses: Appropriate cache headers
- Database queries: Query optimization and indexing

### CDN Configuration
- Configure CDN for static/media files
- Set appropriate cache headers
- Use DigitalOcean Spaces CDN if available

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if Django is running: `docker-compose ps`
   - Check Django logs: `docker-compose logs web`
   - Verify database connection

2. **Static files not loading**
   - Verify `collectstatic` ran successfully
   - Check `STATIC_ROOT` and `STATIC_URL` settings
   - Verify Nginx/Apache configuration

3. **Database connection errors**
   - Verify database credentials
   - Check database is running: `docker-compose ps db`
   - Check network connectivity

4. **Permission errors**
   - Check file permissions
   - Verify user/group ownership
   - Check Docker volume permissions

## Support

- Check logs: `docker-compose logs -f web`
- Django shell: `docker-compose exec web python manage.py shell`
- Database shell: `docker-compose exec db psql -U awinorick -d writingsondo`

**System is ready for production deployment!** 🚀

