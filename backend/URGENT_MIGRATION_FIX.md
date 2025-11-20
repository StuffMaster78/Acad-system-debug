# 🚨 URGENT: Apply Database Migrations

## The Problem

Your database is missing columns that Django models expect:
- `orders_order.submitted_at` ❌
- `orders_order.requires_editing` ❌  
- `orders_order.editing_skip_reason` ❌
- `communications_communicationthread.content_type_id` ❌
- `communications_communicationthread.object_id` ❌

**This is why admin pages are crashing.**

## ⚡ Quick Fix (Copy & Paste)

Run this command **NOW**:

```bash
docker-compose exec web python manage.py migrate
```

Or if you're using a different Docker setup:

```bash
docker exec -it $(docker ps -q -f "ancestor=your_image_name") python manage.py migrate
```

## Step-by-Step Instructions

### 1. Find Your Docker Container

```bash
# List running containers
docker ps

# OR if using docker-compose
docker-compose ps
```

### 2. Apply Migrations

**Option A: Using docker-compose (Recommended)**
```bash
docker-compose exec web python manage.py migrate
```

**Option B: Using docker exec**
```bash
# Replace <container_name> with your actual container name from step 1
docker exec -it <container_name> python manage.py migrate
```

**Option C: If you have a service name**
```bash
docker-compose exec <service_name> python manage.py migrate
```

### 3. Verify Migrations Applied

After running migrate, verify it worked:

```bash
# Check migration status
docker-compose exec web python manage.py showmigrations orders communications

# Or use the verification script
docker-compose exec web python manage.py shell < verify_migration.py
```

You should see `[X]` for all migrations, meaning they're applied.

### 4. Restart Your Server (if needed)

After migrations, restart your Django server:

```bash
# If using docker-compose
docker-compose restart web

# Or just restart the container
docker restart <container_name>
```

## Verify the Fix

After applying migrations, try accessing:
- `/admin/communications/communicationthread/add/` ✅ Should work now
- `/admin/orders/order/` ✅ Should work now

## What These Migrations Do

1. **orders/migrations/0003_add_editing_fields.py**
   - Adds `submitted_at` - Tracks when writer submitted order
   - Adds `requires_editing` - Admin control for editing requirement
   - Adds `editing_skip_reason` - Reason why editing was skipped

2. **communications/migrations/0005_add_content_type_fields.py**
   - Adds `content_type_id` - For GenericForeignKey support
   - Adds `object_id` - For GenericForeignKey support
   - Allows CommunicationThread to link to different model types

## Why This Happens

When you access the admin page for CommunicationThread, Django:
1. Loads the form to add a new CommunicationThread
2. Sees it has a ForeignKey to Order model
3. Tries to load Order fields to populate the dropdown
4. **CRASHES** because `submitted_at` column doesn't exist in database yet

## Troubleshooting

### "No migrations to apply"
If you see this but still get errors:
```bash
# Force check
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### "Table already exists"
Migration might be partially applied. Check which migrations are actually applied:
```bash
docker-compose exec web python manage.py showmigrations
```

### Can't access container
Make sure container is running:
```bash
docker ps
docker-compose ps
```

## Need Help?

If migrations still fail, run this diagnostic:

```bash
docker-compose exec web python manage.py check --deploy
```

This will show all database/configuration issues.

