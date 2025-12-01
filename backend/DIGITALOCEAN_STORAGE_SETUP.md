# DigitalOcean Spaces Setup Guide

## Quick Start for DigitalOcean Droplets

Since you're using DigitalOcean droplets, **DigitalOcean Spaces** is the recommended file storage solution.

## Why DigitalOcean Spaces?

✅ **Perfect for DO Infrastructure**: Seamless integration with your droplets  
✅ **S3-Compatible**: Works with existing django-storages/boto3 code  
✅ **Cost-Effective**: Starting at $5/month for 250GB  
✅ **Built-in CDN**: Fast global content delivery included  
✅ **Simple Billing**: One bill with your droplets  
✅ **Automatic Backups**: 3x replication by default  
✅ **Unlimited Scaling**: Grows with your needs  

## Step-by-Step Setup

### 1. Create DigitalOcean Space

1. **Log in** to DigitalOcean Console
2. **Navigate** to Spaces (left sidebar)
3. **Click** "Create a Spaces Bucket"
4. **Configure**:
   - **Name**: `your-app-media` (must be globally unique, lowercase, no spaces)
   - **Region**: Choose closest to your droplets:
     - `nyc3` - New York
     - `sfo3` - San Francisco  
     - `sgp1` - Singapore
     - `ams3` - Amsterdam
     - `fra1` - Frankfurt
   - **File Listing**: **Disabled** (more secure)
   - **CDN**: **Enabled** (recommended for performance)
5. **Click** "Create a Spaces Bucket"

### 2. Generate Access Keys

1. **Go to** API → **Spaces Keys** (left sidebar)
2. **Click** "Generate New Key"
3. **Name**: `production-spaces-key`
4. **Save** both:
   - **Access Key** (starts with alphanumeric)
   - **Secret Key** (long random string)
   - ⚠️ **Secret Key is shown only once!** Save it securely.

### 3. Enable CDN (Recommended)

1. **Go to** your Space → **Settings** tab
2. **Enable** CDN
3. **Note** the CDN endpoint: `your-space-name.nyc3.cdn.digitaloceanspaces.com`
4. This endpoint will be used in your environment variables

### 4. Configure Environment Variables

Add to your `.env` file on the droplet:

```bash
# DigitalOcean Spaces Configuration
STORAGE_BACKEND=do_spaces
AWS_ACCESS_KEY_ID=your-spaces-access-key-here
AWS_SECRET_ACCESS_KEY=your-spaces-secret-key-here
AWS_STORAGE_BUCKET_NAME=your-space-name
DO_SPACES_REGION=nyc3
DO_SPACES_CDN_ENDPOINT=your-space-name.nyc3.cdn.digitaloceanspaces.com
```

### 5. Install Dependencies

On your droplet:

```bash
pip install django-storages[aws]==1.14.2 boto3==1.34.0
```

Or add to `requirements.txt`:
```
django-storages[aws]==1.14.2
boto3==1.34.0
```

### 6. Deploy and Test

```bash
# Restart your application
sudo systemctl restart gunicorn  # or your app server

# Test file upload via Django shell
python manage.py shell
>>> from django.core.files.storage import default_storage
>>> default_storage.exists('test.txt')
>>> # Upload a test file
```

## Space Structure

Your files will be organized like this:

```
your-space-name/
├── media/
│   ├── website-1/
│   │   ├── order_files/
│   │   ├── class_bundles/
│   │   ├── ticket_attachments/
│   │   └── message_attachments/
│   ├── website-2/
│   │   └── ...
│   └── shared/
├── static/
│   └── (if using Spaces for static files)
└── public-media/
    └── blog_media/
```

## Cost Estimate

### Typical Usage (100GB storage, 500GB bandwidth/month)

- **Storage**: 100GB × $0.02/GB = $2.00/month
- **Bandwidth**: First 1TB is FREE
- **Total**: ~$2-5/month

Much cheaper than AWS S3 for typical workloads!

### Pricing Tiers

- **250GB Plan**: $5/month (includes 250GB storage)
- **Pay-as-you-go**: $0.02/GB storage + $0.01/GB bandwidth (after 1TB free)

## Security Best Practices

### 1. Private Files by Default

All files are private. Access via signed URLs (already configured).

### 2. CORS Configuration

If you need direct browser uploads, configure CORS:

**DigitalOcean Console** → Your Space → **Settings** → **CORS Configurations**

```json
[
  {
    "AllowedOrigins": ["https://yourdomain.com"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

### 3. Bucket Policies

For additional security, restrict access:

**Settings** → **Bucket Policies**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-space-name/media/*",
      "Condition": {
        "StringNotEquals": {
          "aws:Referer": ["https://yourdomain.com"]
        }
      }
    }
  ]
}
```

### 4. Access Keys Security

- ✅ Store keys in environment variables (never in code)
- ✅ Use different keys for staging/production
- ✅ Rotate keys periodically
- ✅ Limit key permissions if possible

## Performance Optimization

### 1. Enable CDN

✅ Already configured if you enabled CDN in step 3. Files are cached globally.

### 2. Cache Headers

Files include `Cache-Control: max-age=86400` (1 day) for optimal caching.

### 3. Signed URL Expiry

Adjust based on file type:
- Documents: 24 hours
- Images: 12 hours  
- General files: 1 hour

Configured in `core/storage_backends.py`.

## Monitoring

### DigitalOcean Metrics

Monitor in DO Console:
- **Storage Used**: Space → Overview
- **Bandwidth**: Space → Overview → Bandwidth graph
- **Requests**: Space → Overview → Requests graph

### Set Up Alerts

1. **Go to** Monitoring → Alerts
2. **Create** alerts for:
   - Storage > 80% capacity
   - Bandwidth spike
   - Unusual request patterns

## Backup Strategy

### Option 1: Enable Versioning

**Space** → **Settings** → **Versioning** → **Enable**

Keeps old versions when files are overwritten.

### Option 2: Automated Backups

Create a cron job to sync to another Space or S3:

```bash
# Install DO CLI
doctl install

# Sync backup (daily at 2 AM)
0 2 * * * /usr/local/bin/doctl compute ssh-key list
```

### Option 3: Lifecycle Policies

**Space** → **Settings** → **Lifecycle Policies**

Automatically move old files to cheaper storage or delete after X days.

## Migration from Local Storage

### Using Django Management Command

The system includes migration support. Create this command:

```python
# core/management/commands/migrate_to_spaces.py
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from order_files.models import OrderFile
# ... import other file models

class Command(BaseCommand):
    help = 'Migrate files from local storage to DigitalOcean Spaces'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting migration to DigitalOcean Spaces...')
        
        # Example: Migrate OrderFiles
        count = 0
        for order_file in OrderFile.objects.all():
            if order_file.file and order_file.file.name:
                try:
                    # Re-save will upload to Spaces
                    order_file.file.save(
                        order_file.file.name,
                        order_file.file,
                        save=False
                    )
                    order_file.save()
                    count += 1
                    if count % 100 == 0:
                        self.stdout.write(f'Migrated {count} files...')
                except Exception as e:
                    self.stderr.write(f'Error: {e}')
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} files!'))
```

Run migration:
```bash
python manage.py migrate_to_spaces
```

## Troubleshooting

### Issue: "Access Denied" errors

**Solution**: Check your access keys are correct and have proper permissions.

### Issue: Slow uploads

**Solution**: 
- Enable CDN
- Check your droplet's network connection
- Consider using direct browser uploads

### Issue: Files not accessible

**Solution**:
- Verify `STORAGE_BACKEND=do_spaces` is set
- Check `AWS_STORAGE_BUCKET_NAME` matches your Space name
- Verify CDN endpoint is correct if using CDN

### Issue: High costs

**Solution**:
- Review bandwidth usage
- Enable lifecycle policies to archive old files
- Consider compression for large files

## Alternative: Local Storage + Backup

If Spaces doesn't fit your needs, you can use local storage with automated backups:

```bash
# Backup script (run daily via cron)
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /backups/media-$DATE.tar.gz /path/to/media/
# Upload to DO Spaces or another backup location
doctl compute ssh-key list  # Example backup command
```

## Support Resources

- **DigitalOcean Spaces Docs**: https://docs.digitalocean.com/products/spaces/
- **django-storages Docs**: https://django-storages.readthedocs.io/
- **S3 API Compatibility**: DO Spaces is 100% S3-compatible

## Next Steps

1. ✅ Create Space
2. ✅ Generate keys  
3. ✅ Set environment variables
4. ✅ Install dependencies
5. ✅ Deploy and test
6. ✅ Migrate existing files
7. ✅ Monitor usage

You're all set! Your files will now be stored securely in DigitalOcean Spaces. 🚀

