# Fix Celery Task Name Error

## Problem
The error `KeyError: 'notifications_system.tasks.send_daily_digest'` occurs because:
1. The task name in the database (PeriodicTask) is `send_daily_digest` (singular)
2. The actual task function is `send_daily_digests` (plural)

## Solution

### Option 1: Run Management Command (Recommended)

Run this command inside your Docker container:

```bash
docker-compose exec web python manage.py fix_daily_digest_task
```

This will automatically update any PeriodicTask records with the old task name.

### Option 2: Manual Database Update

If you prefer to update manually, connect to your database and run:

```sql
UPDATE django_celery_beat_periodictask 
SET task = 'notifications_system.tasks.send_daily_digests' 
WHERE task = 'notifications_system.tasks.send_daily_digest';
```

### Option 3: Django Shell

You can also fix it via Django shell:

```bash
docker-compose exec web python manage.py shell
```

Then in the shell:
```python
from django_celery_beat.models import PeriodicTask

# Find and update the task
tasks = PeriodicTask.objects.filter(task='notifications_system.tasks.send_daily_digest')
tasks.update(task='notifications_system.tasks.send_daily_digests')

print(f"Updated {tasks.count()} task(s)")
```

## After Fixing

1. **Restart Celery Worker:**
   ```bash
   docker-compose restart celery
   ```

2. **Restart Celery Beat (if running separately):**
   ```bash
   docker-compose restart celery-beat
   ```

## Verification

To verify the fix worked, check the PeriodicTask records:

```bash
docker-compose exec web python manage.py shell
```

```python
from django_celery_beat.models import PeriodicTask

# Check for the correct task name
tasks = PeriodicTask.objects.filter(task__icontains='send_daily_digest')
for task in tasks:
    print(f"{task.name}: {task.task}")
```

All tasks should show `notifications_system.tasks.send_daily_digests` (plural).

