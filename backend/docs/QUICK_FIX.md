# Quick Database Fix - Manual Steps

## Run This Python Script

```bash
cd /Users/awwy/writing_system_backend
python3 fix_database_columns.py
```

This will:
- Add all missing columns
- Create missing tables
- Show progress for each step

## OR Run SQL Directly

If the Python script doesn't work, connect to your database and run:

```bash
# Option 1: Using Django dbshell
docker-compose exec web python manage.py dbshell

# Then paste all the SQL commands from fix_all_missing_columns.sql

# Option 2: Using psql directly
docker-compose exec db psql -U awinorick -d writingsondo
```

## Essential SQL Commands (Copy & Paste)

Run these in your database shell:

```sql
-- 1. Orders
ALTER TABLE orders_order 
ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS requires_editing BOOLEAN DEFAULT NULL,
ADD COLUMN IF NOT EXISTS editing_skip_reason VARCHAR(255);

-- 2. Communications
ALTER TABLE communications_communicationthread
ADD COLUMN IF NOT EXISTS content_type_id INTEGER,
ADD COLUMN IF NOT EXISTS object_id INTEGER;

-- 3. BlogCategory
ALTER TABLE blog_pages_management_blogcategory
ADD COLUMN IF NOT EXISTS meta_title VARCHAR(255),
ADD COLUMN IF NOT EXISTS meta_description TEXT,
ADD COLUMN IF NOT EXISTS post_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_views INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 4. BlogPost
ALTER TABLE blog_pages_management_blogpost
ADD COLUMN IF NOT EXISTS content TEXT;

-- 5. PDF Tables (run these one at a time)
CREATE TABLE IF NOT EXISTS blog_pages_management_pdfsamplesection (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    requires_auth BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    blog_id BIGINT NOT NULL REFERENCES blog_pages_management_blogpost(id) ON DELETE CASCADE
);
```

## After Running SQL

Mark migrations as fake-applied:

```bash
docker-compose exec web python manage.py migrate --fake orders 0003_add_editing_fields
docker-compose exec web python manage.py migrate --fake communications 0005_add_content_type_fields  
docker-compose exec web python manage.py migrate --fake blog_pages_management 0003_add_blogcategory_fields
docker-compose exec web python manage.py migrate --fake blog_pages_management 0004_add_blogpost_content_field
docker-compose exec web python manage.py migrate --fake blog_pages_management 0005_create_pdf_sample_models
```

## Verify

Try accessing admin pages - they should work now!

