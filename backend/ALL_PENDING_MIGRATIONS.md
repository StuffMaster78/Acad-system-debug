# All Pending Migrations Summary

## Overview

Multiple migrations need to be applied to fix missing database columns and tables.

## Migrations Created

### 1. Orders App
**File**: `orders/migrations/0003_add_editing_fields.py`
- Adds `submitted_at` (DateTimeField)
- Adds `requires_editing` (BooleanField)
- Adds `editing_skip_reason` (CharField)

### 2. Communications App
**File**: `communications/migrations/0005_add_content_type_fields.py`
- Adds `content_type_id` (ForeignKey)
- Adds `object_id` (PositiveIntegerField)

### 3. Blog Pages Management App

#### 3a. BlogCategory Fields
**File**: `blog_pages_management/migrations/0003_add_blogcategory_fields.py`
- Adds `meta_title`, `meta_description`, `category_image`
- Adds `post_count`, `total_views`, `total_conversions`
- Adds `display_order`, `is_featured`, `is_active`
- Adds `created_at`, `updated_at`

#### 3b. BlogPost Content Field
**File**: `blog_pages_management/migrations/0004_add_blogpost_content_field.py`
- Adds `content` (TextField) - Fixes models.Field() issue
- Uses RunSQL to add column directly

#### 3c. PDF Sample Models
**File**: `blog_pages_management/migrations/0005_create_pdf_sample_models.py`
- Creates `PDFSampleSection` table
- Creates `PDFSample` table
- Creates `PDFSampleDownload` table

## Apply All Migrations

Run this single command to apply all pending migrations:

```bash
docker-compose exec web python manage.py migrate
```

Or apply specific apps:

```bash
# Apply orders
docker-compose exec web python manage.py migrate orders

# Apply communications
docker-compose exec web python manage.py migrate communications

# Apply blog pages
docker-compose exec web python manage.py migrate blog_pages_management
```

## Verify Migrations

After applying, verify all migrations are applied:

```bash
docker-compose exec web python manage.py showmigrations orders communications blog_pages_management
```

All should show `[X]` (checked).

## Expected Admin Pages to Work After Migrations

- ✅ `/admin/orders/order/`
- ✅ `/admin/communications/communicationthread/`
- ✅ `/admin/communications/communicationthread/add/`
- ✅ `/admin/communications/flaggedmessage/`
- ✅ `/admin/communications/communicationlog/`
- ✅ `/admin/blog_pages_management/blogcategory/`
- ✅ `/admin/blog_pages_management/blogpost/`
- ✅ `/admin/blog_pages_management/pdfsamplesection/`
- ✅ `/admin/blog_pages_management/pdfsample/`
- ✅ `/admin/blog_pages_management/pdfsampledownload/`

## Troubleshooting

### If migrations fail with "field already exists"
The column might exist but Django doesn't know about it. Check the database:

```sql
-- Connect to database
docker-compose exec web python manage.py dbshell

-- Check if column exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'orders_order' 
AND column_name = 'submitted_at';
```

### If RunSQL migration fails
The migration uses `IF NOT EXISTS` so it should be safe to run multiple times. If it still fails, run the SQL manually:

```sql
ALTER TABLE blog_pages_management_blogpost ADD COLUMN IF NOT EXISTS content TEXT;
```

## Quick Fix Script

To apply all migrations and verify:

```bash
docker-compose exec web bash -c "
python manage.py migrate && \
python manage.py showmigrations orders communications blog_pages_management
"
```

