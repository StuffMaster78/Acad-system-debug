#!/usr/bin/env python3
"""
Quick script to verify if migrations need to be applied.
Run this inside your Docker container to check the database state.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.db import connection

print("=" * 60)
print("Migration Verification Script")
print("=" * 60)
print()

# Check orders_order table
print("Checking orders_order table...")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'orders_order'
        AND column_name IN ('submitted_at', 'requires_editing', 'editing_skip_reason')
        ORDER BY column_name
    """)
    existing_columns = [row[0] for row in cursor.fetchall()]
    
    required_columns = ['submitted_at', 'requires_editing', 'editing_skip_reason']
    missing_columns = [col for col in required_columns if col not in existing_columns]
    
    if missing_columns:
        print(f"❌ MISSING COLUMNS: {', '.join(missing_columns)}")
        print()
        print("👉 ACTION REQUIRED: Run migrations!")
        print("   docker-compose exec web python manage.py migrate orders")
        sys.exit(1)
    else:
        print(f"✅ All required columns exist: {', '.join(existing_columns)}")

# Check communications_communicationthread table
print()
print("Checking communications_communicationthread table...")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'communications_communicationthread'
        AND column_name IN ('content_type_id', 'object_id')
        ORDER BY column_name
    """)
    existing_columns = [row[0] for row in cursor.fetchall()]
    
    required_columns = ['content_type_id', 'object_id']
    missing_columns = [col for col in required_columns if col not in existing_columns]
    
    if missing_columns:
        print(f"❌ MISSING COLUMNS: {', '.join(missing_columns)}")
        print()
        print("👉 ACTION REQUIRED: Run migrations!")
        print("   docker-compose exec web python manage.py migrate communications")
        sys.exit(1)
    else:
        print(f"✅ All required columns exist: {', '.join(existing_columns)}")

print()
print("=" * 60)
print("✅ All migrations appear to be applied!")
print("=" * 60)

