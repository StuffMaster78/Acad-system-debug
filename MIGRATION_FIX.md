# Fix: Missing Database Columns Error

## Error Message
```
ProgrammingError: column orders_order.submitted_at does not exist
```

## Root Cause
The migration files exist but haven't been applied to the database yet.

## Solution

### If Running Locally (Not Docker)

```bash
cd /Users/awwy/writing_system_backend

# Apply all pending migrations
python3 manage.py migrate

# OR apply specific apps
python3 manage.py migrate orders
python3 manage.py migrate communications
```

### If Running in Docker

Based on your error message showing `/app` path, you're likely in Docker:

```bash
# Option 1: Using docker-compose
docker-compose exec web python manage.py migrate

# Option 2: Using docker exec directly
# First, find your container name:
docker ps

# Then run:
docker exec -it <container_name> python manage.py migrate

# Option 3: If using docker-compose with specific service name
docker-compose exec <service_name> python manage.py migrate
```

### Verify Migrations Applied

After running migrations, verify:

```bash
# Local
python3 manage.py showmigrations orders communications

# Docker
docker-compose exec web python manage.py showmigrations orders communications
```

You should see `[X]` (checked) for all migrations, not `[ ]` (unchecked).

## Expected Result

After applying migrations, these columns will exist:
- ✅ `orders_order.submitted_at`
- ✅ `orders_order.requires_editing`
- ✅ `orders_order.editing_skip_reason`
- ✅ `communications_communicationthread.content_type_id`
- ✅ `communications_communicationthread.object_id`

## Admin Pages That Will Work

After migrations:
- ✅ `/admin/orders/order/`
- ✅ `/admin/communications/communicationthread/`
- ✅ `/admin/communications/communicationthread/add/`
- ✅ `/admin/communications/flaggedmessage/`
- ✅ `/admin/communications/communicationlog/`

## Migration Files

These migration files need to be applied:
1. `orders/migrations/0003_add_editing_fields.py`
2. `communications/migrations/0005_add_content_type_fields.py`

## Troubleshooting

### If migrations fail with "table already exists"
The migrations might have been partially applied. Check which migrations are actually applied:
```bash
python3 manage.py showmigrations
```

### If you see "No migrations to apply"
But still get the error, the migration might not be detected. Try:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### If using Docker and can't access container
Make sure the container is running:
```bash
docker ps
docker-compose ps
```

