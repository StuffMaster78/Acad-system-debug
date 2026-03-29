# Apply Missing Migrations

## Current Issue

The database is missing the following columns:
- `orders_order.submitted_at`
- `orders_order.requires_editing`
- `orders_order.editing_skip_reason`
- `communications_communicationthread.content_type_id`
- `communications_communicationthread.object_id`

## Solution

Run these commands to apply the migrations:

### Option 1: Apply All Pending Migrations (Recommended)

```bash
cd /Users/awwy/writing_system_backend
python3 manage.py migrate
```

### Option 2: Apply Specific Migrations

```bash
cd /Users/awwy/writing_system_backend

# Apply orders migration
python3 manage.py migrate orders

# Apply communications migration
python3 manage.py migrate communications
```

### Option 3: If Using Docker

```bash
# If backend is in Docker container
docker-compose exec web python manage.py migrate

# Or if using docker exec
docker exec -it <container_name> python manage.py migrate
```

## Verify Migrations Applied

After running migrations, verify with:

```bash
python3 manage.py showmigrations orders communications
```

All migrations should show `[X]` indicating they're applied.

## Expected Result

After applying migrations:
- ✅ `/admin/orders/order/` should work
- ✅ `/admin/communications/communicationthread/` should work
- ✅ `/admin/communications/flaggedmessage/` should work
- ✅ `/admin/communications/communicationlog/` should work

## Migration Files

The following migration files have been created/updated:
- `orders/migrations/0003_add_editing_fields.py` - Adds submitted_at, requires_editing, editing_skip_reason
- `communications/migrations/0005_add_content_type_fields.py` - Adds content_type and object_id

Make sure to commit these migration files to version control.

