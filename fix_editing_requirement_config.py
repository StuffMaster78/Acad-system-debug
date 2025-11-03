#!/usr/bin/env python3
"""Quick fix to create EditingRequirementConfig table."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.db import connection, transaction
from django.conf import settings

def check_table_exists(table_name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, [table_name])
        return cursor.fetchone()[0]

table_name = 'order_configs_editingrequirementconfig'

if check_table_exists(table_name):
    print(f"✓ Table {table_name} already exists")
else:
    print(f"Creating table {table_name}...")
    
    # Get the user model table name
    user_model = settings.AUTH_USER_MODEL
    user_table = user_model.split('.')[-1].lower() + '_user'  # Approximate
    
    # Create the table
    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id BIGSERIAL PRIMARY KEY,
        website_id BIGINT NOT NULL REFERENCES websites_website(id) ON DELETE CASCADE,
        enable_editing_by_default BOOLEAN DEFAULT TRUE,
        skip_editing_for_urgent BOOLEAN DEFAULT TRUE,
        allow_editing_for_early_submissions BOOLEAN DEFAULT TRUE,
        early_submission_hours_threshold INTEGER DEFAULT 24,
        editing_required_for_first_orders BOOLEAN DEFAULT TRUE,
        editing_required_for_high_value BOOLEAN DEFAULT TRUE,
        high_value_threshold NUMERIC(10, 2) DEFAULT 300.00,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL,
        CONSTRAINT unique_website UNIQUE (website_id)
    );
    
    CREATE INDEX IF NOT EXISTS {table_name}_website_id_idx ON {table_name}(website_id);
    CREATE INDEX IF NOT EXISTS {table_name}_created_by_id_idx ON {table_name}(created_by_id);
    """
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(sql)
    
    print(f"✅ Table {table_name} created successfully!")

