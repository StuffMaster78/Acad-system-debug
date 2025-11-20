#!/bin/bash
# Script to create test users inside Docker container

docker-compose exec -T web python manage.py shell << 'EOF'
import os
import sys
import django

django.setup()

from django.contrib.auth import get_user_model
from websites.models import Website
from django.db import transaction

User = get_user_model()

# Common password for all test users
TEST_PASSWORD = "testpass123"

# Test users configuration
TEST_USERS = [
    {
        "email": "test@admin.local",
        "username": "test_admin",
        "role": "admin",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "email": "test@superadmin.local",
        "username": "test_superadmin",
        "role": "superadmin",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "test@editor.local",
        "username": "test_editor",
        "role": "editor",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "test@writer.local",
        "username": "test_writer",
        "role": "writer",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "test@support.local",
        "username": "test_support",
        "role": "support",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "test@client.local",
        "username": "test_client",
        "role": "client",
        "is_staff": False,
        "is_superuser": False,
    },
]

def create_test_users():
    """Create test users for all roles."""
    print("=" * 60)
    print("Creating Test Users")
    print("=" * 60)
    
    # Get or create a default website
    website, created = Website.objects.get_or_create(
        name="Test Website",
        defaults={
            "domain": "https://test.local",
            "is_active": True,
        }
    )
    if created:
        print(f"✅ Created default website: {website.name}")
    else:
        print(f"✅ Using existing website: {website.name}")
    
    created_users = []
    updated_users = []
    
    with transaction.atomic():
        for user_config in TEST_USERS:
            email = user_config["email"]
            username = user_config["username"]
            role = user_config["role"]
            
            try:
                # Check if user exists
                user = User.objects.filter(email=email).first()
                
                if user:
                    # Update existing user
                    user.username = username
                    user.role = role
                    user.is_staff = user_config.get("is_staff", False)
                    user.is_superuser = user_config.get("is_superuser", False)
                    user.is_active = True
                    user.set_password(TEST_PASSWORD)
                    
                    # Assign website for roles that need it
                    if role in ["writer", "client", "admin"] and not user.website:
                        user.website = website
                    
                    user.save()
                    updated_users.append(user)
                    print(f"🔄 Updated: {email} ({role})")
                else:
                    # Create new user
                    user = User.objects.create_user(
                        email=email,
                        username=username,
                        password=TEST_PASSWORD,
                        role=role,
                        is_staff=user_config.get("is_staff", False),
                        is_superuser=user_config.get("is_superuser", False),
                        is_active=True,
                    )
                    
                    # Assign website for roles that need it
                    if role in ["writer", "client", "admin"]:
                        user.website = website
                        user.save()
                    
                    created_users.append(user)
                    print(f"✅ Created: {email} ({role})")
                    
            except Exception as e:
                print(f"❌ Error creating {email}: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Created: {len(created_users)} users")
    print(f"Updated: {len(updated_users)} users")
    print(f"\nAll users use password: {TEST_PASSWORD}")
    print("\n" + "=" * 60)
    print("Test Users Credentials")
    print("=" * 60)
    
    for user_config in TEST_USERS:
        print(f"Email: {user_config['email']}")
        print(f"Role: {user_config['role']}")
        print(f"Password: {TEST_PASSWORD}")
        print("-" * 60)

create_test_users()
EOF

