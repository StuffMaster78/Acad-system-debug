# Production File Storage Strategy

## Current Setup

Currently using **local filesystem storage**:
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

**Issues in Production:**
- ❌ Files stored on server filesystem (not scalable)
- ❌ No backup/redundancy
- ❌ Difficulty sharing across multiple servers/containers
- ❌ Limited CDN capabilities
- ❌ Disk space management issues
- ❌ Security concerns (files accessible via direct URL)

## Recommended: DigitalOcean Spaces (S3-Compatible)

### Why DigitalOcean Spaces for Droplets?

Since you're using DigitalOcean droplets, **DigitalOcean Spaces** is the perfect fit:

1. **Seamless Integration**: Works with your existing DO infrastructure
2. **S3-Compatible API**: Uses same libraries (boto3) as AWS S3
3. **Cost-Effective**: Lower cost than AWS S3, especially for DO users
4. **CDN Included**: Built-in CDN for fast global access
5. **Simple Billing**: One unified bill with your droplets
6. **Multi-tenant Support**: Easy website/tenant isolation
7. **Unlimited Storage**: Scales automatically
8. **Built-in Backup**: 3x replication by default

### DigitalOcean Spaces Setup

#### Pricing (as of 2024)
- Storage: $5/month for 250GB, then $0.02/GB
- Bandwidth: Free for first 1TB, then $0.01/GB
- Much cheaper than AWS for typical use cases

---

## Alternative Options for DigitalOcean Droplets

### Option 1: DigitalOcean Spaces (Recommended) ⭐

**Best for**: Production with scalability needs

### Option 2: Local Storage + Automated Backups

**Best for**: Small deployments, budget-conscious, simple setup

### Option 3: AWS S3 (Cross-Cloud)

**Best for**: Multi-cloud strategy, enterprise requirements

---

## Recommended: DigitalOcean Spaces (Recommended for Multi-Tenant)

### Why S3?

1. **Scalability**: Unlimited storage, handles growth automatically
2. **Multi-tenant isolation**: Easy to organize by website/tenant
3. **CDN Integration**: Works seamlessly with CloudFront
4. **Durability**: 99.999999999% (11 nines) durability
5. **Security**: IAM roles, bucket policies, signed URLs
6. **Cost-effective**: Pay for what you use
7. **Backup/Versioning**: Built-in versioning and lifecycle policies
8. **Cross-region replication**: For disaster recovery

### Implementation with django-storages

DigitalOcean Spaces uses the **S3-compatible API**, so the same code works with minimal changes!

#### Step 1: Install Required Packages

Add to `requirements.txt`:
```
django-storages[aws]==1.14.2
boto3==1.34.0
```

#### Step 2: Create DigitalOcean Space

1. Go to DigitalOcean Console → Spaces
2. Create a new Space:
   - **Name**: `your-app-media` (must be globally unique)
   - **Region**: Choose closest to your droplets (e.g., `nyc3`, `sfo3`)
   - **File Listing**: Disabled (more secure)
3. Generate Spaces Keys:
   - Go to API → Spaces Keys
   - Create new key pair
   - Save Access Key and Secret Key

#### Step 3: Update Django Settings

```python
# writing_system/settings.py

import os

# Storage configuration: 'do_spaces', 's3', or 'local'
STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'local')  # 'do_spaces', 's3', 'local'

if STORAGE_BACKEND in ['do_spaces', 's3']:
    # DigitalOcean Spaces (S3-compatible) or AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')  # Spaces Access Key for DO
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')  # Spaces Secret Key for DO
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    if STORAGE_BACKEND == 'do_spaces':
        # DigitalOcean Spaces configuration
        AWS_S3_ENDPOINT_URL = f'https://{os.getenv("DO_SPACES_REGION", "nyc3")}.digitaloceanspaces.com'
        AWS_S3_REGION_NAME = os.getenv('DO_SPACES_REGION', 'nyc3')
        # DO Spaces CDN endpoint (created automatically when CDN enabled)
        AWS_S3_CUSTOM_DOMAIN = os.getenv('DO_SPACES_CDN_ENDPOINT')  # Optional: CDN endpoint
        
        # Media URL for DO Spaces
        if AWS_S3_CUSTOM_DOMAIN:
            MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
        else:
            MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com/media/'
    else:
        # AWS S3 configuration
        AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
        AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN or AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/media/'
    
    # Security settings (same for both DO Spaces and S3)
    AWS_DEFAULT_ACL = 'private'  # Private files by default
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 1 day cache
        'ServerSideEncryption': 'AES256',
    }
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True  # Use signed URLs
    
    # Storage classes
    DEFAULT_FILE_STORAGE = 'core.storage_backends.MediaStorage'
    STATICFILES_STORAGE = 'core.storage_backends.StaticStorage'
    
    MEDIA_ROOT = ''  # Not used with cloud storage
else:
    # Local filesystem storage (development)
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

#### Step 3: Create Storage Backend Classes

Create `core/storage_backends.py`:

```python
"""
Custom storage backends for S3 with multi-tenant support.
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import os


class MediaStorage(S3Boto3Storage):
    """
    Storage backend for media files (user uploads).
    Organizes files by website/tenant for isolation.
    """
    location = 'media'
    default_acl = 'private'
    file_overwrite = False
    
    def get_valid_name(self, name):
        """Add website prefix for multi-tenant isolation."""
        # Try to get website from context
        try:
            from core.tenant_context import get_current_website
            website = get_current_website()
            if website:
                # Organize by website: media/website-slug/...
                website_slug = website.slug or str(website.id)
                if not name.startswith(f'{website_slug}/'):
                    name = f'{website_slug}/{name}'
        except (ImportError, AttributeError):
            pass
        
        return super().get_valid_name(name)
    
    def url(self, name, parameters=None, expire=3600):
        """
        Generate signed URL for private files.
        Default expiry: 1 hour (3600 seconds)
        """
        # Increase expiry for certain file types if needed
        if name.endswith(('.pdf', '.doc', '.docx')):
            expire = 3600 * 24  # 24 hours for documents
        
        return super().url(name, parameters=parameters, expire=expire)


class StaticStorage(S3Boto3Storage):
    """
    Storage backend for static files (CSS, JS, images).
    These can be public for better CDN performance.
    """
    location = 'static'
    default_acl = 'public-read'  # Static files can be public
    file_overwrite = True


class PublicMediaStorage(S3Boto3Storage):
    """
    For public media files (blog images, public assets).
    Use when you want files accessible without signed URLs.
    """
    location = 'public-media'
    default_acl = 'public-read'
    file_overwrite = False
```

#### Step 4: Environment Variables

**For DigitalOcean Spaces:**
```bash
STORAGE_BACKEND=do_spaces
AWS_ACCESS_KEY_ID=your-do-spaces-access-key
AWS_SECRET_ACCESS_KEY=your-do-spaces-secret-key
AWS_STORAGE_BUCKET_NAME=your-space-name
DO_SPACES_REGION=nyc3  # nyc3, sfo3, sgp1, etc.
DO_SPACES_CDN_ENDPOINT=your-space-name.nyc3.cdn.digitaloceanspaces.com  # Optional: CDN
```

**For AWS S3 (alternative):**
```bash
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=cdn.yourdomain.com  # Optional: CloudFront
```

**For Local Storage (development):**
```bash
STORAGE_BACKEND=local
# MEDIA_ROOT will use default local path
```

#### Step 5: Update File Models (Optional - for public files)

If you have files that should be public (like blog images), create a custom field:

```python
# core/fields.py
from django.db import models
from core.storage_backends import PublicMediaStorage

class PublicFileField(models.FileField):
    """FileField that uses public storage."""
    def __init__(self, *args, **kwargs):
        kwargs['storage'] = PublicMediaStorage()
        super().__init__(*args, **kwargs)
```

Usage in models:
```python
from core.fields import PublicFileField

class BlogMediaFile(models.Model):
    file = PublicFileField(upload_to='blog_media/')  # Public access
```

### DigitalOcean Spaces Structure (Multi-Tenant)

Same structure works for both DO Spaces and AWS S3:

```
your-bucket/
├── media/
│   ├── website-1/              # Tenant isolation
│   │   ├── order_files/
│   │   ├── class_bundles/
│   │   ├── ticket_attachments/
│   │   └── message_attachments/
│   ├── website-2/
│   │   └── ...
│   └── shared/                 # Cross-tenant files if needed
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── public-media/               # Public files
    └── blog_media/
```

### S3 Bucket Policy Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicAccessToStatic",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket/static/*"
    },
    {
      "Sid": "DenyPublicAccessToMedia",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket/media/*"
    }
  ]
}
```

---

## Alternative: Azure Blob Storage

If you prefer Azure:

### Setup

```python
# Install: pip install django-storages[azure]

AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER')
AZURE_CUSTOM_DOMAIN = os.getenv('AZURE_CUSTOM_DOMAIN')

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
```

---

## Alternative: Google Cloud Storage

```python
# Install: pip install django-storages[gcloud]

GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME')
GS_PROJECT_ID = os.getenv('GS_PROJECT_ID')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
```

---

## Migration Strategy

### Step 1: Setup S3 Bucket

1. Create S3 bucket in AWS Console
2. Enable versioning (recommended)
3. Set up lifecycle policies (move old files to Glacier)
4. Configure CORS if needed for direct uploads
5. Set up CloudFront distribution (optional but recommended)

### Step 2: Update Code

1. Install django-storages
2. Update settings.py
3. Create storage_backends.py
4. Deploy with USE_S3=False initially

### Step 3: Migrate Existing Files

Create a management command to migrate existing files:

```python
# core/management/commands/migrate_to_s3.py
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from order_files.models import OrderFile
from class_management.models import ClassBundleFile
# ... import other file models

class Command(BaseCommand):
    help = 'Migrate existing files from local storage to S3'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting file migration to S3...')
        
        # Migrate OrderFiles
        order_files = OrderFile.objects.all()
        for order_file in order_files:
            if order_file.file and order_file.file.name:
                try:
                    # Open local file
                    with open(order_file.file.path, 'rb') as f:
                        # Save to S3 (will use new storage backend)
                        order_file.file.save(
                            order_file.file.name,
                            f,
                            save=True
                        )
                    self.stdout.write(f'Migrated: {order_file.file.name}')
                except Exception as e:
                    self.stderr.write(f'Error migrating {order_file.file.name}: {e}')
        
        # Repeat for other file models...
        
        self.stdout.write(self.style.SUCCESS('Migration complete!'))
```

### Step 4: Enable S3 in Production

1. Set `USE_S3=True` in production environment
2. Deploy
3. Run migration command
4. Verify files are accessible
5. Keep local files as backup for 30 days

---

## Security Best Practices

### 1. Signed URLs for Private Files

Already implemented in `MediaStorage.url()` method. Files are private by default and accessed via signed URLs with expiration.

### 2. IAM Roles (Better than Access Keys)

Use IAM roles for EC2/ECS instead of access keys:

```python
# If using IAM role, don't set AWS_ACCESS_KEY_ID
# boto3 will automatically use the role credentials
if not os.getenv('AWS_ACCESS_KEY_ID'):
    # Using IAM role
    pass
```

### 3. Bucket Policies

Restrict access to specific IPs or VPC:
```json
{
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": ["YOUR.SERVER.IP/32"]
    }
  }
}
```

### 4. Encryption

Enable server-side encryption:
```python
AWS_S3_OBJECT_PARAMETERS = {
    'ServerSideEncryption': 'AES256',  # or 'aws:kms'
}
```

---

## Performance Optimization

### 1. CloudFront CDN

Set up CloudFront distribution for:
- Faster global access
- Reduced S3 costs
- Better caching

### 2. Pre-signed URLs with Longer Expiry

For frequently accessed files:
```python
# In views or services
from django.core.files.storage import default_storage

def get_file_url(file_instance, expire=86400):  # 24 hours
    """Get pre-signed URL with custom expiry."""
    return default_storage.url(file_instance.file.name, expire=expire)
```

### 3. Direct Uploads

Allow clients to upload directly to S3:

```python
# Install: pip install django-s3direct

# settings.py
S3DIRECT_REGION = 'us-east-1'
S3DIRECT_DESTINATIONS = {
    'order-files': {
        'key': 'media/{website_slug}/order_files/',
        'allowed': ['application/pdf', 'application/msword'],
        'acl': 'private',
    }
}
```

---

## Cost Optimization

### 1. Lifecycle Policies

Move old files to cheaper storage classes:
- After 30 days → Standard-IA (Infrequent Access)
- After 90 days → Glacier
- After 1 year → Glacier Deep Archive

### 2. Intelligent Tiering

Enable S3 Intelligent-Tiering for automatic cost optimization.

### 3. Compression

Compress files before upload:
```python
import gzip

def compress_file(file):
    """Compress file before upload."""
    # Implementation
    pass
```

---

## Monitoring & Backup

### 1. CloudWatch Alerts

Monitor:
- Bucket size
- Request counts
- Error rates

### 2. Versioning

Enable S3 versioning for accidental deletion recovery.

### 3. Cross-Region Replication

For disaster recovery, replicate to another region.

---

## Testing Strategy

### Development

```python
# Use local storage
USE_S3 = False
```

### Staging

```python
# Use separate S3 bucket for staging
USE_S3 = True
AWS_STORAGE_BUCKET_NAME = 'your-app-staging'
```

### Production

```python
# Production bucket
USE_S3 = True
AWS_STORAGE_BUCKET_NAME = 'your-app-production'
```

---

## Recommended Implementation Priority

1. **Phase 1**: Setup S3 backend, deploy with USE_S3=False
2. **Phase 2**: Test S3 with USE_S3=True in staging
3. **Phase 3**: Migrate existing files
4. **Phase 4**: Enable CloudFront CDN
5. **Phase 5**: Setup lifecycle policies and monitoring

This approach minimizes risk and allows gradual migration.

