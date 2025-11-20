#!/usr/bin/env python3
"""
Script to fix missing database columns and tables.
This applies SQL directly to the database.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.db import connection

def execute_sql(sql):
    """Execute SQL and return result."""
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.rowcount

def check_column_exists(table, column):
    """Check if a column exists in a table."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        """, [table, column])
        return cursor.fetchone() is not None

def check_table_exists(table):
    """Check if a table exists."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = %s
        """, [table])
        return cursor.fetchone() is not None

print("=" * 60)
print("Fixing Missing Database Columns and Tables")
print("=" * 60)
print()

# Fix Orders
print("1. Fixing orders_order table...")
orders_fixes = [
    ("submitted_at", "ALTER TABLE orders_order ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP WITH TIME ZONE"),
    ("requires_editing", "ALTER TABLE orders_order ADD COLUMN IF NOT EXISTS requires_editing BOOLEAN DEFAULT NULL"),
    ("editing_skip_reason", "ALTER TABLE orders_order ADD COLUMN IF NOT EXISTS editing_skip_reason VARCHAR(255)"),
]

for col_name, sql in orders_fixes:
    if not check_column_exists('orders_order', col_name):
        try:
            execute_sql(sql)
            print(f"   ✅ Added {col_name}")
        except Exception as e:
            print(f"   ❌ Failed to add {col_name}: {e}")
    else:
        print(f"   ✓ {col_name} already exists")

# Fix Communications
print("\n2. Fixing communications_communicationthread table...")
comm_fixes = [
    ("content_type_id", "ALTER TABLE communications_communicationthread ADD COLUMN IF NOT EXISTS content_type_id INTEGER REFERENCES django_content_type(id) ON DELETE CASCADE"),
    ("object_id", "ALTER TABLE communications_communicationthread ADD COLUMN IF NOT EXISTS object_id INTEGER"),
]

for col_name, sql in comm_fixes:
    if not check_column_exists('communications_communicationthread', col_name):
        try:
            execute_sql(sql)
            print(f"   ✅ Added {col_name}")
        except Exception as e:
            print(f"   ❌ Failed to add {col_name}: {e}")
    else:
        print(f"   ✓ {col_name} already exists")

# Fix BlogCategory
print("\n3. Fixing blog_pages_management_blogcategory table...")
blogcat_fixes = [
    ("meta_title", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS meta_title VARCHAR(255)"),
    ("meta_description", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS meta_description TEXT"),
    ("category_image", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS category_image VARCHAR(100)"),
    ("post_count", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS post_count INTEGER DEFAULT 0"),
    ("total_views", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS total_views INTEGER DEFAULT 0"),
    ("total_conversions", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS total_conversions INTEGER DEFAULT 0"),
    ("display_order", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0"),
    ("is_featured", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE"),
    ("is_active", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"),
    ("created_at", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()"),
    ("updated_at", "ALTER TABLE blog_pages_management_blogcategory ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()"),
]

for col_name, sql in blogcat_fixes:
    if not check_column_exists('blog_pages_management_blogcategory', col_name):
        try:
            execute_sql(sql)
            print(f"   ✅ Added {col_name}")
        except Exception as e:
            print(f"   ❌ Failed to add {col_name}: {e}")
    else:
        print(f"   ✓ {col_name} already exists")

# Fix BlogPost content and status
print("\n4. Fixing blog_pages_management_blogpost table...")
if not check_column_exists('blog_pages_management_blogpost', 'content'):
    try:
        execute_sql("ALTER TABLE blog_pages_management_blogpost ADD COLUMN IF NOT EXISTS content TEXT")
        print("   ✅ Added content column")
    except Exception as e:
        print(f"   ❌ Failed to add content: {e}")
else:
    print("   ✓ content column already exists")

if not check_column_exists('blog_pages_management_blogpost', 'status'):
    try:
        execute_sql("ALTER TABLE blog_pages_management_blogpost ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'draft'")
        print("   ✅ Added status column")
    except Exception as e:
        print(f"   ❌ Failed to add status: {e}")
else:
    print("   ✓ status column already exists")

# Create PDF tables
print("\n5. Creating PDF sample tables...")

if not check_table_exists('blog_pages_management_pdfsamplesection'):
    try:
        execute_sql("""
            CREATE TABLE blog_pages_management_pdfsamplesection (
                id BIGSERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                requires_auth BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                blog_id BIGINT NOT NULL REFERENCES blog_pages_management_blogpost(id) ON DELETE CASCADE
            )
        """)
        execute_sql("""
            CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsamplesection_blog_id_is_active_idx 
            ON blog_pages_management_pdfsamplesection(blog_id, is_active)
        """)
        print("   ✅ Created PDFSampleSection table")
    except Exception as e:
        print(f"   ❌ Failed to create PDFSampleSection: {e}")
else:
    print("   ✓ PDFSampleSection table already exists")

if not check_table_exists('blog_pages_management_pdfsample'):
    try:
        execute_sql("""
            CREATE TABLE blog_pages_management_pdfsample (
                id BIGSERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                pdf_file VARCHAR(100) NOT NULL,
                file_size INTEGER,
                display_order INTEGER DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                is_featured BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                section_id BIGINT NOT NULL REFERENCES blog_pages_management_pdfsamplesection(id) ON DELETE CASCADE,
                uploaded_by_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL
            )
        """)
        execute_sql("""
            CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsample_section_id_is_active_idx 
            ON blog_pages_management_pdfsample(section_id, is_active)
        """)
        execute_sql("""
            CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsample_download_count_idx 
            ON blog_pages_management_pdfsample(download_count)
        """)
        print("   ✅ Created PDFSample table")
    except Exception as e:
        print(f"   ❌ Failed to create PDFSample: {e}")
else:
    print("   ✓ PDFSample table already exists")

if not check_table_exists('blog_pages_management_pdfsampledownload'):
    try:
        execute_sql("""
            CREATE TABLE blog_pages_management_pdfsampledownload (
                id BIGSERIAL PRIMARY KEY,
                ip_address INET,
                user_agent TEXT,
                session_id VARCHAR(255),
                downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                pdf_sample_id BIGINT NOT NULL REFERENCES blog_pages_management_pdfsample(id) ON DELETE CASCADE,
                user_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL
            )
        """)
        execute_sql("""
            CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsampledownload_pdf_sample_id_downloaded_at_idx 
            ON blog_pages_management_pdfsampledownload(pdf_sample_id, downloaded_at)
        """)
        execute_sql("""
            CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsampledownload_user_id_downloaded_at_idx 
            ON blog_pages_management_pdfsampledownload(user_id, downloaded_at)
        """)
        print("   ✅ Created PDFSampleDownload table")
    except Exception as e:
        print(f"   ❌ Failed to create PDFSampleDownload: {e}")
else:
    print("   ✓ PDFSampleDownload table already exists")

print("\n" + "=" * 60)
print("✅ Database fixes complete!")
print("=" * 60)
print("\nNow mark migrations as applied:")
print("  docker-compose exec web python manage.py migrate --fake orders 0003_add_editing_fields")
print("  docker-compose exec web python manage.py migrate --fake communications 0005_add_content_type_fields")
print("  docker-compose exec web python manage.py migrate --fake blog_pages_management 0003_add_blogcategory_fields")
print("  docker-compose exec web python manage.py migrate --fake blog_pages_management 0004_add_blogpost_content_field")
print("  docker-compose exec web python manage.py migrate --fake blog_pages_management 0005_create_pdf_sample_models")

