#!/usr/bin/env python3
"""Quick fix to add status column to BlogPost."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.db import connection, transaction

with transaction.atomic():
    with connection.cursor() as cursor:
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'blog_pages_management_blogpost' 
            AND column_name = 'status'
        """)
        exists = cursor.fetchone() is not None
        
        if not exists:
            print("Adding status column to blog_pages_management_blogpost...")
            cursor.execute("""
                ALTER TABLE blog_pages_management_blogpost 
                ADD COLUMN status VARCHAR(20) DEFAULT 'draft'
            """)
            print("✅ Status column added successfully!")
        else:
            print("✓ Status column already exists")

