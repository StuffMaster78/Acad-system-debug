#!/usr/bin/env python
"""
Generate Nginx configuration dynamically from Website models in database.

This script queries the Django database for all active websites and generates
nginx server blocks for each client domain, plus shared writer and staff dashboards.

Usage:
    python manage.py shell < scripts/generate_nginx_config.py > nginx-generated.conf
    OR
    python scripts/generate_nginx_config.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from websites.models import Website

# Configuration
WRITER_DOMAIN = os.getenv('WRITER_DOMAIN', 'writers.yourdomain.com')
STAFF_DOMAIN = os.getenv('STAFF_DOMAIN', 'staff.yourdomain.com')
API_DOMAIN = os.getenv('API_DOMAIN', 'api.yourdomain.com')  # Optional
SSL_CERT_PATH = '/etc/nginx/ssl'
FRONTEND_ROOT = '/var/www'

def normalize_domain(domain_url):
    """Extract clean domain from URL."""
    domain = domain_url.replace('https://', '').replace('http://', '').replace('www.', '')
    return domain.split('/')[0]

def generate_nginx_config():
    """Generate complete nginx configuration."""
    
    # Get all active websites
    active_websites = Website.objects.filter(is_active=True, is_deleted=False)
    
    config = []
    
    # Header
    config.append("""events {
    worker_connections 1024;
}

http {
    upstream django {
        server web:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
""")
    
    # Writer Dashboard
    config.append(f"""
    # Writer Dashboard
    server {{
        listen 80;
        listen [::]:80;
        server_name {WRITER_DOMAIN};

        return 301 https://$server_name$request_uri;
    }}

    server {{
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name {WRITER_DOMAIN};

        ssl_certificate {SSL_CERT_PATH}/{WRITER_DOMAIN}/fullchain.pem;
        ssl_certificate_key {SSL_CERT_PATH}/{WRITER_DOMAIN}/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        root {FRONTEND_ROOT}/writers;
        index index.html;

        location /api/ {{
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;
            proxy_connect_timeout 60s;
        }}

        location / {{
            try_files $uri $uri/ /index.html;
            expires 1h;
            add_header Cache-Control "public, must-revalidate";
        }}

        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
""")
    
    # Staff Dashboard
    config.append(f"""
    # Staff Dashboard
    server {{
        listen 80;
        listen [::]:80;
        server_name {STAFF_DOMAIN};

        return 301 https://$server_name$request_uri;
    }}

    server {{
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name {STAFF_DOMAIN};

        ssl_certificate {SSL_CERT_PATH}/{STAFF_DOMAIN}/fullchain.pem;
        ssl_certificate_key {SSL_CERT_PATH}/{STAFF_DOMAIN}/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        root {FRONTEND_ROOT}/staff;
        index index.html;

        location /api/ {{
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;
            proxy_connect_timeout 60s;
        }}

        location / {{
            try_files $uri $uri/ /index.html;
            expires 1h;
            add_header Cache-Control "public, must-revalidate";
        }}

        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
""")
    
    # Client Dashboards (one per website)
    for website in active_websites:
        domain = normalize_domain(website.domain)
        domain_safe = domain.replace('.', '_')
        
        config.append(f"""
    # Client Dashboard: {website.name} ({domain})
    server {{
        listen 80;
        listen [::]:80;
        server_name {domain};

        return 301 https://$server_name$request_uri;
    }}

    server {{
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name {domain};

        ssl_certificate {SSL_CERT_PATH}/{domain}/fullchain.pem;
        ssl_certificate_key {SSL_CERT_PATH}/{domain}/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        root {FRONTEND_ROOT}/clients;
        index index.html;

        location /api/ {{
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;
            proxy_connect_timeout 60s;
        }}

        location / {{
            try_files $uri $uri/ /index.html;
            expires 1h;
            add_header Cache-Control "public, must-revalidate";
        }}

        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
""")
    
    # API Server (Optional)
    if API_DOMAIN:
        config.append(f"""
    # API Server
    server {{
        listen 80;
        listen [::]:80;
        server_name {API_DOMAIN};

        return 301 https://$server_name$request_uri;
    }}

    server {{
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name {API_DOMAIN};

        ssl_certificate {SSL_CERT_PATH}/{API_DOMAIN}/fullchain.pem;
        ssl_certificate_key {SSL_CERT_PATH}/{API_DOMAIN}/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {{
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;
            proxy_connect_timeout 60s;
        }}
    }}
""")
    
    # Footer
    config.append("}\n")
    
    return ''.join(config)

if __name__ == '__main__':
    try:
        print(generate_nginx_config())
    except Exception as e:
        print(f"Error generating nginx config: {e}", file=sys.stderr)
        sys.exit(1)

