# How to Create a Superuser

## Option 1: Interactive Command (Recommended)

Run this command in your terminal (without the `-T` flag to allow interactive input):

```bash
docker-compose exec web python manage.py createsuperuser
```

This will prompt you to enter:
- Username
- Email address
- Password (twice)

## Option 2: Using Environment Variables (Non-Interactive)

If you prefer a non-interactive approach, you can create a superuser using environment variables:

```bash
docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='your_secure_password_here'
)
print('Superuser created successfully!')
EOF
```

Replace:
- `'admin'` with your desired username
- `'admin@example.com'` with your email
- `'your_secure_password_here'` with a secure password

## Option 3: Using Django Shell Directly

```bash
docker-compose exec web python manage.py shell
```

Then in the Python shell:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='your_secure_password_here'
)
exit()
```

## After Creating Superuser

Once created, you can:

1. **Access Django Admin:**
   ```
   http://localhost:8000/admin/
   ```

2. **Login with your credentials:**
   - Username: (the one you entered)
   - Password: (the one you entered)

3. **Access API endpoints** (after logging in and getting JWT token):
   ```
   http://localhost:8000/api/v1/docs/swagger/
   ```

## Verify Superuser Creation

To verify the superuser was created:

```bash
docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(f'Superusers: {User.objects.filter(is_superuser=True).count()}')"
```

