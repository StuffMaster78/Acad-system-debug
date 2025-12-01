# Multi-Domain Deployment Guide

## Overview

This guide covers deploying the Writing System dashboards on separate domains:
- **Writer Dashboard**: `writers.yourdomain.com` (single shared dashboard)
- **Client Dashboards**: Multiple domains, one per Website in database (e.g., `client1.com`, `client2.com`, etc.)
- **Staff Dashboard**: `staff.yourdomain.com` (single shared dashboard for Admin, Support, Editor)

**Important**: The system supports multiple client domains because each `Website` in the database can have its own domain. Clients access their dashboard via their website's domain.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Backend API                           │
│              api.yourdomain.com:8000                     │
│         (Single Django backend instance)                 │
│         (Multi-tenant: identifies website by domain)     │
└─────────────────────────────────────────────────────────┘
                        ▲
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Writer       │ │ Client 1     │ │ Client 2     │ │ Staff        │
│ Dashboard    │ │ Dashboard    │ │ Dashboard    │ │ Dashboard    │
│ writers.     │ │ client1.com  │ │ client2.com  │ │ staff.       │
│ yourdomain   │ │              │ │              │ │ yourdomain   │
│ .com         │ │              │ │              │ │ .com        │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
   (Shared)         (Per Website)    (Per Website)     (Shared)
```

---

## Prerequisites

1. **Domain Names**: 
   - **Writer Dashboard**: `writers.yourdomain.com` (single domain)
   - **Client Dashboards**: One domain per Website in your database (configured in Django admin)
     - Example: `client1.com`, `client2.com`, `orders.example.com`, etc.
   - **Staff Dashboard**: `staff.yourdomain.com` (single domain)
   - **API**: `api.yourdomain.com` (optional, for API)

2. **SSL Certificates**: Let's Encrypt certificates for each domain

3. **Server**: DigitalOcean Droplet or similar with:
   - Docker & Docker Compose installed
   - Nginx installed (or use Docker Nginx)
   - Ports 80, 443, 8000 open

---

## Step 1: Backend Configuration

### 1.1 Update Django Settings

Update `writing_system/settings.py` to allow all dashboard domains:

```python
# ALLOWED_HOSTS - Add all your domains
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS", 
    "localhost,127.0.0.1,api.yourdomain.com"
).split(",")

# CORS Configuration - Allow all dashboard domains
CORS_ALLOWED_ORIGINS = [
    "https://writers.yourdomain.com",
    "https://clients.yourdomain.com",
    "https://staff.yourdomain.com",
    "http://localhost:5173",  # Keep for local dev
    "http://localhost:3000",
]

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "https://writers.yourdomain.com",
    "https://clients.yourdomain.com",
    "https://staff.yourdomain.com",
    "http://localhost:5173",
]

# Frontend URLs for email links (role-specific)
WRITER_FRONTEND_URL = os.getenv("WRITER_FRONTEND_URL", "https://writers.yourdomain.com")
CLIENT_FRONTEND_URL = os.getenv("CLIENT_FRONTEND_URL", "https://clients.yourdomain.com")
STAFF_FRONTEND_URL = os.getenv("STAFF_FRONTEND_URL", "https://staff.yourdomain.com")
```

### 1.2 Environment Variables (.env)

Update your `.env` file:

```bash
# Domain Configuration
ALLOWED_HOSTS=api.yourdomain.com,localhost,127.0.0.1
WRITER_FRONTEND_URL=https://writers.yourdomain.com
CLIENT_FRONTEND_URL=https://clients.yourdomain.com
STAFF_FRONTEND_URL=https://staff.yourdomain.com

# CORS Origins (comma-separated)
CORS_ALLOWED_ORIGINS=https://writers.yourdomain.com,https://clients.yourdomain.com,https://staff.yourdomain.com
```

---

## Step 2: Frontend Configuration

### 2.1 Create Environment-Specific Config Files

Create separate environment files for each dashboard:

**`frontend/.env.writers`**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_DASHBOARD_TYPE=writer
VITE_APP_TITLE=Writer Dashboard
```

**`frontend/.env.clients`**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_DASHBOARD_TYPE=client
VITE_APP_TITLE=Client Dashboard
```

**`frontend/.env.staff`**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_DASHBOARD_TYPE=staff
VITE_APP_TITLE=Staff Dashboard
```

### 2.2 Update API Client Configuration

Update `frontend/src/api/client.js` to use environment variable:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for CORS with credentials
})
```

### 2.3 Create Website Store for Branding

Create a Pinia store to manage website configuration and branding. Create `frontend/src/stores/website.js`:

```javascript
import { defineStore } from 'pinia'
import apiClient from '@/api/client'

export const useWebsiteStore = defineStore('website', {
  state: () => ({
    website: null,
    loading: false,
    error: null
  }),

  getters: {
    logo: (state) => state.website?.logo || null,
    themeColor: (state) => state.website?.theme_color || '#3B82F6',
    websiteName: (state) => state.website?.name || 'Writing System',
    contactEmail: (state) => state.website?.contact_email || null,
    contactPhone: (state) => state.website?.contact_phone || null,
  },

  actions: {
    async fetchCurrentWebsite() {
      this.loading = true
      this.error = null
      
      try {
        const response = await apiClient.get('/websites/current/')
        this.website = response.data
        
        // Apply theme color to document
        if (this.website.theme_color) {
          document.documentElement.style.setProperty('--primary-color', this.website.theme_color)
        }
        
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch website config:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
```

### 2.4 Initialize Website Config on App Mount

Update `frontend/src/App.vue` or `main.js` to fetch website config on app initialization:

```javascript
// main.js or App.vue
import { createApp } from 'vue'
import { useWebsiteStore } from '@/stores/website'

const app = createApp(App)

// Fetch website config on app initialization (for client dashboards)
if (import.meta.env.VITE_DASHBOARD_TYPE === 'client') {
  const websiteStore = useWebsiteStore()
  websiteStore.fetchCurrentWebsite().catch(err => {
    console.warn('Could not fetch website config:', err)
  })
}
```

### 2.5 Create Role-Based Router Guards

Update `frontend/src/router/index.js` to add domain-based role restrictions:

```javascript
// Add domain-based access control
const DASHBOARD_TYPE = import.meta.env.VITE_DASHBOARD_TYPE

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if user is accessing the correct dashboard for their role
  if (to.meta.requiresAuth && authStore.isAuthenticated) {
    const userRole = authStore.userRole
    
    // Writer dashboard - only writers
    if (DASHBOARD_TYPE === 'writer' && userRole !== 'writer') {
      next({ name: 'Login' })
      return
    }
    
    // Client dashboard - only clients
    if (DASHBOARD_TYPE === 'client' && userRole !== 'client') {
      next({ name: 'Login' })
      return
    }
    
    // Staff dashboard - admin, support, editor only
    if (DASHBOARD_TYPE === 'staff' && 
        !['admin', 'support', 'editor', 'superadmin'].includes(userRole)) {
      next({ name: 'Login' })
      return
    }
  }
  
  next()
})
```

### 2.4 Build Scripts for Each Dashboard

Create build scripts in `frontend/package.json`:

```json
{
  "scripts": {
    "build:writers": "vite build --mode writers",
    "build:clients": "vite build --mode clients",
    "build:staff": "vite build --mode staff",
    "build:all": "npm run build:writers && npm run build:clients && npm run build:staff"
  }
}
```

Update `vite.config.js` to support multiple modes:

```javascript
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  build: {
    outDir: (mode) => {
      const dashboardType = mode === 'writers' ? 'writers' : 
                           mode === 'clients' ? 'clients' : 'staff'
      return `dist/${dashboardType}`
    },
    assetsDir: 'assets',
    sourcemap: false
  }
})
```

---

## Step 3: Nginx Configuration

### 3.1 Dynamic Nginx Config Generation (Recommended)

Since you have multiple client domains (one per Website), it's best to generate the nginx configuration dynamically from your database.

**Option A: Generate from Database (Recommended)**

Use the provided script to generate nginx config from active websites:

```bash
# Generate nginx configuration from database
python scripts/generate_nginx_config.py > nginx-generated.conf

# Or using Django management command
python manage.py shell < scripts/generate_nginx_config.py > nginx-generated.conf
```

This script will:
- Query all active `Website` objects from the database
- Generate nginx server blocks for each client domain
- Include shared writer and staff dashboards
- Create proper SSL certificate paths for each domain

**Option B: Manual Configuration**

If you prefer manual configuration, create `nginx-multi-domain.conf` with all your client domains:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream django {
        server web:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Writer Dashboard
    server {
        listen 80;
        listen [::]:80;
        server_name writers.yourdomain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name writers.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/writers.yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/writers.yourdomain.com/privkey.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        # Frontend static files
        root /var/www/writers;
        index index.html;

        # API proxy
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes (SPA)
        location / {
            try_files $uri $uri/ /index.html;
        }
    }

    # Client Dashboard - Example for client1.com
    # Repeat this block for each client domain
    server {
        listen 80;
        listen [::]:80;
        server_name client1.com;

        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name client1.com;

        ssl_certificate /etc/nginx/ssl/client1.com/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/client1.com/privkey.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        # Frontend static files
        root /var/www/clients;
        index index.html;

        # API proxy
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes (SPA)
        location / {
            try_files $uri $uri/ /index.html;
        }
    }

    # Staff Dashboard
    server {
        listen 80;
        listen [::]:80;
        server_name staff.yourdomain.com;

        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name staff.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/staff.yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/staff.yourdomain.com/privkey.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        # Frontend static files
        root /var/www/staff;
        index index.html;

        # API proxy
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes (SPA)
        location / {
            try_files $uri $uri/ /index.html;
        }
    }

    # API Server (Optional - if you want separate API domain)
    server {
        listen 80;
        listen [::]:80;
        server_name api.yourdomain.com;

        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/api.yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/api.yourdomain.com/privkey.pem;

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API only
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## Step 4: Docker Compose Configuration

### 4.1 Update docker-compose.prod.yml

Add volumes for frontend builds and update nginx:

```yaml
services:
  # ... existing services (web, db, redis, celery, beat) ...

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-multi-domain.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./frontend/dist/writers:/var/www/writers:ro
      - ./frontend/dist/clients:/var/www/clients:ro
      - ./frontend/dist/staff:/var/www/staff:ro
    depends_on:
      - web
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Step 5: Deployment Process

### 5.1 Build Frontend for Each Dashboard

```bash
cd frontend

# Build all dashboards
npm install
npm run build:writers
npm run build:clients
npm run build:staff
```

### 5.2 Setup SSL Certificates

Using Let's Encrypt with Certbot:

**For Shared Dashboards:**
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificates for shared dashboards
sudo certbot certonly --standalone -d writers.yourdomain.com
sudo certbot certonly --standalone -d staff.yourdomain.com
sudo certbot certonly --standalone -d api.yourdomain.com  # Optional
```

**For Client Domains:**

You need SSL certificates for **each client domain** (each Website in your database):

```bash
# Option 1: Generate certificates manually for each client domain
sudo certbot certonly --standalone -d client1.com
sudo certbot certonly --standalone -d client2.com
sudo certbot certonly --standalone -d orders.example.com
# ... repeat for all client domains

# Option 2: Use wildcard certificate (if all client domains are subdomains)
sudo certbot certonly --standalone -d *.yourdomain.com

# Copy certificates to project directory
# For each domain:
sudo mkdir -p ssl/writers.yourdomain.com
sudo mkdir -p ssl/staff.yourdomain.com
sudo mkdir -p ssl/client1.com
sudo mkdir -p ssl/client2.com
# ... repeat for all domains

sudo cp /etc/letsencrypt/live/writers.yourdomain.com/fullchain.pem ssl/writers.yourdomain.com/
sudo cp /etc/letsencrypt/live/writers.yourdomain.com/privkey.pem ssl/writers.yourdomain.com/
# Repeat for all other domains...
```

**Automated Certificate Generation Script:**

Create a script to generate certificates for all active websites:

```bash
#!/bin/bash
# scripts/generate_ssl_certs.sh

# Get all active website domains from database
python manage.py shell << EOF
from websites.models import Website
domains = Website.objects.filter(is_active=True, is_deleted=False).values_list('domain', flat=True)
for domain_url in domains:
    domain = domain_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    print(domain)
EOF | while read domain; do
    echo "Generating certificate for $domain..."
    sudo certbot certonly --standalone -d "$domain" --non-interactive --agree-tos --email your-email@example.com
done
```

### 5.3 Deploy

```bash
# Update environment variables
nano .env

# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## Step 6: DNS Configuration

Configure DNS records for each domain:

**Shared Dashboards:**
```
Type    Name      Value              TTL
A       writers   YOUR_SERVER_IP     3600
A       staff     YOUR_SERVER_IP     3600
A       api       YOUR_SERVER_IP     3600  (Optional)
```

**Client Domains:**
Configure DNS for **each client domain** (each Website in your database):

```
Type    Name      Value              TTL
A       @         YOUR_SERVER_IP     3600  (for client1.com)
A       @         YOUR_SERVER_IP     3600  (for client2.com)
A       @         YOUR_SERVER_IP     3600  (for orders.example.com)
# ... repeat for all client domains
```

**Note**: Each client domain should point to the same server IP. The backend identifies which website to use based on the `Host` header in the request.

---

## Step 7: Database Initial Setup

### 7.1 Create Initial Websites

Before deploying, you need to create at least one Website in the database:

**Option A: Using Django Admin (Recommended)**
1. Access Django Admin: `http://your-server:8000/admin/`
2. Go to **Websites** → **Add Website**
3. Fill in:
   - **Name**: Your website name (e.g., "Client 1")
   - **Domain**: Full URL (e.g., `https://client1.com`)
   - **Is Active**: ✅ Checked
   - **Logo**: Upload logo image
   - **Theme Color**: HEX color (e.g., `#3B82F6`)
   - **Contact Email**: support@client1.com
   - **Contact Phone**: +1234567890

**Option B: Using Django Shell**
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# In shell:
from websites.models import Website
Website.objects.create(
    name="Client 1",
    domain="https://client1.com",
    is_active=True,
    theme_color="#3B82F6",
    contact_email="support@client1.com"
)
```

**Option C: Using Management Command**
Create `websites/management/commands/create_initial_websites.py`:

```python
from django.core.management.base import BaseCommand
from websites.models import Website

class Command(BaseCommand):
    help = 'Create initial websites'

    def handle(self, *args, **options):
        websites = [
            {
                'name': 'Client 1',
                'domain': 'https://client1.com',
                'theme_color': '#3B82F6',
            },
            {
                'name': 'Client 2',
                'domain': 'https://client2.com',
                'theme_color': '#10B981',
            },
        ]
        
        for site_data in websites:
            website, created = Website.objects.get_or_create(
                domain=site_data['domain'],
                defaults=site_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created website: {website.name}'))
            else:
                self.stdout.write(f'Website already exists: {website.name}')
```

Run: `python manage.py create_initial_websites`

---

## Step 8: Testing

### 8.1 Test Each Dashboard

1. **Writer Dashboard**: `https://writers.yourdomain.com`
   - Login as a writer
   - Verify API calls work
   - Check CORS headers

2. **Client Dashboard**: `https://clients.yourdomain.com`
   - Login as a client
   - Verify API calls work
   - Check CORS headers

3. **Staff Dashboard**: `https://staff.yourdomain.com`
   - Login as admin/support/editor
   - Verify API calls work
   - Check CORS headers

### 7.2 Verify Security

- ✅ HTTPS redirects work
- ✅ CORS headers are correct
- ✅ Role-based access control works
- ✅ CSRF protection is active
- ✅ SSL certificates are valid

---

## Step 9: Maintenance

### 9.1 Adding New Client Domains

When you add a new Website in Django Admin:

1. **Add Website in Django Admin**:
   - Go to Django Admin → Websites
   - Create new website with domain (e.g., `https://newclient.com`)
   - Set `is_active = True`

2. **Generate SSL Certificate**:
   ```bash
   sudo certbot certonly --standalone -d newclient.com
   sudo mkdir -p ssl/newclient.com
   sudo cp /etc/letsencrypt/live/newclient.com/fullchain.pem ssl/newclient.com/
   sudo cp /etc/letsencrypt/live/newclient.com/privkey.pem ssl/newclient.com/
   ```

3. **Regenerate Nginx Config**:
   ```bash
   python scripts/generate_nginx_config.py > nginx-generated.conf
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

4. **Update DNS**: Point the new domain to your server IP

5. **Update CORS/ALLOWED_HOSTS**: If using manual configuration, add the new domain

### 9.2 SSL Certificate Renewal

Set up automatic renewal for all domains:

```bash
# Add to crontab
sudo crontab -e

# Add this line (runs twice daily)
0 0,12 * * * certbot renew --quiet --deploy-hook "docker-compose -f /path/to/docker-compose.prod.yml restart nginx"
```

**Note**: Certbot will automatically renew certificates for all domains it has issued certificates for.

### 9.3 Monitoring and Logging per Domain

**Nginx Access Logs:**
Configure nginx to log per domain for easier debugging:

```nginx
# In each server block, add:
access_log /var/log/nginx/client1.com.access.log;
error_log /var/log/nginx/client1.com.error.log;
```

**Django Logging:**
Update `settings.py` to include website context in logs:

```python
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '[{website}] {levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'filters': {
        'website_context': {
            '()': 'core.logging.WebsiteContextFilter',
        },
    },
    # ... rest of logging config
}
```

### 9.4 Update Deployment Script

Create `deploy-multi-domain.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying multi-domain dashboards..."

# Build frontends
echo "📦 Building frontend dashboards..."
cd frontend
npm install
npm run build:all
cd ..

# Deploy backend
echo "🐳 Deploying backend..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
echo "🗄️  Running migrations..."
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
echo "📊 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
echo "🌐 Dashboards available at:"
echo "   - Writers: https://writers.yourdomain.com"
echo "   - Clients: https://clients.yourdomain.com"
echo "   - Staff: https://staff.yourdomain.com"
```

---

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Check `CORS_ALLOWED_ORIGINS` in Django settings
2. Verify domain names match exactly (including https://)
3. Check browser console for specific error messages
4. Verify `CORS_ALLOW_CREDENTIALS = True`

### SSL Certificate Issues

1. Ensure certificates are in the correct directory
2. Check file permissions (nginx needs read access)
3. Verify certificate paths in nginx config
4. Test with: `openssl x509 -in ssl/writers.yourdomain.com/fullchain.pem -text -noout`

### 404 Errors on Frontend Routes

1. Ensure `try_files $uri $uri/ /index.html;` is in nginx config
2. Verify frontend build files are in correct directories
3. Check nginx root paths match build output directories

### Role-Based Access Issues

1. Verify `VITE_DASHBOARD_TYPE` is set correctly in build
2. Check router guards are working
3. Verify user roles in database match expected values

### Website Not Identified

If the backend can't identify the website:

1. **Check WebsiteMiddleware is enabled** in `settings.py`
2. **Verify domain matches exactly** in database (including https://)
3. **Check Host header** is being passed correctly by nginx:
   ```nginx
   proxy_set_header Host $host;  # Must be present
   ```
4. **Test endpoint**: `curl -H "Host: client1.com" https://api.yourdomain.com/api/v1/websites/current/`

### Frontend Branding Not Loading

1. **Check API endpoint**: Visit `https://client1.com/api/v1/websites/current/` directly
2. **Verify CORS**: Check browser console for CORS errors
3. **Check website store**: Verify `fetchCurrentWebsite()` is called on app mount
4. **Check logo URL**: Ensure logo is accessible via media URL

---

## Security Considerations

1. **Separate Domains**: Provides better isolation between user types
2. **HTTPS Only**: All traffic should use HTTPS
3. **CORS Restrictions**: Only allow specific origins
4. **Rate Limiting**: Configure rate limits per domain
5. **Role Validation**: Always validate user roles on backend
6. **Session Security**: Use secure, httpOnly cookies
7. **CSRF Protection**: Enable CSRF for all state-changing operations

---

## Alternative: Single Domain with Path-Based Routing

If you prefer a single domain with path-based routing:

- `yourdomain.com/writers/*` → Writer Dashboard
- `yourdomain.com/clients/*` → Client Dashboard
- `yourdomain.com/staff/*` → Staff Dashboard

This requires different nginx configuration but simpler SSL setup (single certificate).

---

## Next Steps

1. ✅ Configure DNS records
2. ✅ Set up SSL certificates
3. ✅ Update environment variables
4. ✅ Build and deploy frontends
5. ✅ Test each dashboard
6. ✅ Set up monitoring and logging
7. ✅ Configure backups

---

## Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs nginx`
- Check backend logs: `docker-compose -f docker-compose.prod.yml logs web`
- Test API directly: `curl https://api.yourdomain.com/api/v1/health/`

