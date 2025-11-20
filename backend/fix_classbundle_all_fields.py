#!/usr/bin/env python3
"""Quick fix to add all missing ClassBundle fields."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.db import connection, transaction

def check_column_exists(table_name, column_name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            )
        """, [table_name, column_name])
        return cursor.fetchone()[0]

def add_classbundle_columns():
    print("Adding missing ClassBundle columns...")
    table_name = 'class_management_classbundle'
    
    columns_to_add = [
        ("website_id", "BIGINT REFERENCES websites_website(id) ON DELETE CASCADE"),
        ("assigned_writer_id", "BIGINT REFERENCES users_user(id) ON DELETE SET NULL"),
        ("pricing_source", "VARCHAR(20) DEFAULT 'config'"),
        ("start_date", "DATE"),
        ("end_date", "DATE"),
        ("deposit_required", "NUMERIC(10, 2) DEFAULT 0.00"),
        ("deposit_paid", "NUMERIC(10, 2) DEFAULT 0.00"),
        ("installments_enabled", "BOOLEAN DEFAULT FALSE"),
        ("installment_count", "INTEGER DEFAULT 0"),
        ("original_price", "NUMERIC(10, 2)"),
        ("discount_id", "BIGINT REFERENCES discounts_discount(id) ON DELETE SET NULL"),
        ("created_by_admin_id", "BIGINT REFERENCES users_user(id) ON DELETE SET NULL"),
    ]
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            for col_name, col_type in columns_to_add:
                if not check_column_exists(table_name, col_name):
                    print(f"  Adding {col_name}...")
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};")
                        print(f"    ✅ Added {col_name}")
                    except Exception as e:
                        print(f"    ❌ Failed to add {col_name}: {e}")
                else:
                    print(f"  ✓ {col_name} already exists")
    
    # Add indexes
    print("\nAdding indexes...")
    indexes = [
        ("website_id", "class_management_classbundle_website_id_idx"),
        ("assigned_writer_id", "class_management_classbundle_assigned_writer_id_idx"),
        ("discount_id", "class_management_classbundle_discount_id_idx"),
        ("created_by_admin_id", "class_management_classbundle_created_by_admin_id_idx"),
    ]
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            for col, idx_name in indexes:
                try:
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS {idx_name} 
                        ON {table_name}({col});
                    """)
                    print(f"  ✅ Index {idx_name} created/verified")
                except Exception as e:
                    print(f"  ⚠️  Index {idx_name}: {e}")

if __name__ == "__main__":
    add_classbundle_columns()
    print("\n✅ Done! Refresh admin page.")

