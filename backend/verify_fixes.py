#!/usr/bin/env python3
"""Quick script to verify all database fixes are in place."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.db import connection

def check_column(table, column):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        """, [table, column])
        return cursor.fetchone() is not None

def check_table(table):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = %s
        """, [table])
        return cursor.fetchone() is not None

print("Verifying database fixes...")
print()

checks = [
    # Orders
    ("orders_order", "submitted_at", "Orders: submitted_at"),
    ("orders_order", "requires_editing", "Orders: requires_editing"),
    ("orders_order", "editing_skip_reason", "Orders: editing_skip_reason"),
    # Communications
    ("communications_communicationthread", "content_type_id", "Communications: content_type_id"),
    ("communications_communicationthread", "object_id", "Communications: object_id"),
    # BlogCategory
    ("blog_pages_management_blogcategory", "meta_title", "BlogCategory: meta_title"),
    ("blog_pages_management_blogcategory", "created_at", "BlogCategory: created_at"),
    # BlogPost
    ("blog_pages_management_blogpost", "content", "BlogPost: content"),
    ("blog_pages_management_blogpost", "status", "BlogPost: status"),
    # PDF Tables
    ("blog_pages_management_pdfsamplesection", None, "Table: PDFSampleSection"),
    ("blog_pages_management_pdfsample", None, "Table: PDFSample"),
    ("blog_pages_management_pdfsampledownload", None, "Table: PDFSampleDownload"),
]

all_good = True
for table, column, description in checks:
    if column:
        exists = check_column(table, column)
    else:
        exists = check_table(table)
    
    if exists:
        print(f"✅ {description}")
    else:
        print(f"❌ {description} - MISSING!")
        all_good = False

print()
if all_good:
    print("🎉 All fixes are in place! Admin pages should work now.")
else:
    print("⚠️  Some fixes are missing. Run fix_database_columns.py or apply SQL manually.")

