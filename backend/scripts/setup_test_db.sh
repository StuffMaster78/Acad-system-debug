#!/bin/bash
# Setup script for test database
# This ensures migrations are run before tests

set -e

echo "🔧 Setting up test database..."

# Set test settings
export DJANGO_SETTINGS_MODULE=writing_system.settings_test

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput --verbosity=0

# Create test website if needed
echo "🌐 Creating test website..."
python manage.py shell << EOF
from websites.models.websites import Website
Website.objects.get_or_create(
    domain="test.local",
    defaults={
        "name": "Test Website",
        "slug": "test",
        "is_active": True
    }
)
print("✅ Test website created/verified")
EOF

echo "✅ Test database setup complete!"

