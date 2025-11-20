#!/bin/bash
# Complete script to fix all database issues and mark migrations as applied

echo "=========================================="
echo "Complete Database Fix Script"
echo "=========================================="
echo ""

# Run the Python fix script
echo "Step 1: Running database column fixes..."
python3 fix_database_columns.py

echo ""
echo "Step 2: Marking migrations as applied..."
docker-compose exec web python manage.py migrate --fake orders 0003_add_editing_fields
docker-compose exec web python manage.py migrate --fake communications 0005_add_content_type_fields
docker-compose exec web python manage.py migrate --fake blog_pages_management 0003_add_blogcategory_fields
docker-compose exec web python manage.py migrate --fake blog_pages_management 0004_add_blogpost_content_field
docker-compose exec web python manage.py migrate --fake blog_pages_management 0005_create_pdf_sample_models

echo ""
echo "Step 3: Verifying fixes..."
python3 verify_fixes.py

echo ""
echo "=========================================="
echo "Done! Try accessing admin pages now."
echo "=========================================="

