# Deployment Guide

**Version**: 1.0  
**Last Updated**: December 2025

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [SSL/HTTPS Configuration](#sslhttps-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-Deployment Checklist

### Code Preparation

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Environment variables documented
- [ ] Database migrations ready
- [ ] Static files collected
- [ ] Security audit completed

### Configuration

- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` configured
- [ ] `SECRET_KEY` set (not in code)
- [ ] Database credentials configured
- [ ] Email backend configured
- [ ] CORS settings configured

### Infrastructure

- [ ] Server provisioned
- [ ] Domain name configured
- [ ] SSL certificate ready
- [ ] Database server ready
- [ ] Backup system configured

---

## 🌍 Environment Setup

### Environment Variables

Create `.env` file for production:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Redis (if using)
REDIS_URL=redis://localhost:6379/0

# AWS S3 (if using)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

### Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

---

## 🗄️ Database Setup

### PostgreSQL Setup

1. **Install PostgreSQL**
   ```bash
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE writing_system;
   CREATE USER writing_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE writing_system TO writing_user;
   ```

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

### Database Backup

```bash
# Backup
pg_dump -U writing_user writing_system > backup.sql

# Restore
psql -U writing_user writing_system < backup.sql
```

---

## 🔧 Backend Deployment

### Using Gunicorn

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn Config**
   ```python
   # gunicorn_config.py
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "sync"
   timeout = 120
   keepalive = 5
   ```

3. **Run Gunicorn**
   ```bash
   gunicorn writing_system.wsgi:application --config gunicorn_config.py
   ```

### Using Systemd Service

Create `/etc/systemd/system/writing-system.service`:

```ini
[Unit]
Description=Writing System Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/writing_project/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn writing_system.wsgi:application --config gunicorn_config.py

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start writing-system
sudo systemctl enable writing-system
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/writing_project/backend/staticfiles/;
    }

    location /media/ {
        alias /path/to/writing_project/backend/media/;
    }
}
```

---

## 🎨 Frontend Deployment

### Build for Production

```bash
cd frontend
npm run build
```

### Serve with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /path/to/writing_project/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Variables

Create `.env.production`:

```bash
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## 🔒 SSL/HTTPS Configuration

### Using Let's Encrypt

1. **Install Certbot**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Get Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

3. **Auto-Renewal**
   ```bash
   sudo certbot renew --dry-run
   ```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of configuration
}
```

---

## 📊 Monitoring & Logging

### Application Logging

Configure logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/writing-system/app.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Monitoring Tools

- **Sentry** - Error tracking
- **DataDog** - Application monitoring
- **New Relic** - Performance monitoring
- **Prometheus** - Metrics collection

---

## 💾 Backup & Recovery

### Automated Backups

Create backup script:

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="writing_system"
DB_USER="writing_user"

# Database backup
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /path/to/media

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Schedule with cron:
```bash
0 2 * * * /path/to/backup.sh
```

### Recovery Procedure

1. **Stop Services**
   ```bash
   sudo systemctl stop writing-system
   ```

2. **Restore Database**
   ```bash
   psql -U writing_user writing_system < backup.sql
   ```

3. **Restore Media**
   ```bash
   tar -xzf media_backup.tar.gz -C /path/to/media
   ```

4. **Start Services**
   ```bash
   sudo systemctl start writing-system
   ```

---

## 🔧 Troubleshooting

### Common Issues

**Database Connection Error**
- Check database credentials
- Verify database is running
- Check firewall rules

**Static Files Not Loading**
- Run `python manage.py collectstatic`
- Check Nginx configuration
- Verify file permissions

**502 Bad Gateway**
- Check Gunicorn is running
- Check application logs
- Verify port configuration

**SSL Certificate Issues**
- Check certificate expiration
- Verify domain configuration
- Check Nginx SSL settings

---

## 📞 Support

For deployment assistance:
- Check logs: `/var/log/writing-system/`
- Review documentation
- Contact DevOps team

---

**Last Updated**: December 2025

