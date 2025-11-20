# Handling Migration Prompts

## Current Situation

When running `makemigrations`, Django is asking you:

1. **FineAppeal.created_at → submitted_at**: Answer `y` (yes)
2. **BlogCategory.created_at default**: Needs a default value for existing rows

## Solution

### Step 1: Run makemigrations

```bash
docker-compose exec web python manage.py makemigrations
```

### Step 2: Answer Prompts

**Prompt 1: FineAppeal field rename**
```
Was fineappeal.created_at renamed to fineappeal.submitted_at (a DateTimeField)? [y/N]
```
**Answer**: `y` (yes)

**Prompt 2: BlogCategory default value**
```
It is impossible to add the field 'created_at' with 'auto_now_add=True' to blogcategory without providing a default.
 1) Provide a one-off default now which will be set on all existing rows
 2) Quit and manually define a default value in models.py.
Select an option:
```
**Answer**: `1` (provide one-off default)

Then it will ask for the default value:
```
Please enter the default value now, as valid Python
You can accept the default 'timezone.now' by pressing 'Enter' or you can provide another value.
The datetime and django.utils.timezone modules are available, so you can do e.g. timezone.now
[default: timezone.now]: 
```
**Answer**: Press `Enter` to accept `timezone.now` (or type `timezone.now`)

### Step 3: Apply Migrations

After makemigrations completes successfully:

```bash
docker-compose exec web python manage.py migrate
```

## Alternative: Skip BlogCategory Default (If No Existing Data)

If you don't have any existing BlogCategory records, you can temporarily make the field nullable:

```python
# In blog_pages_management/_legacy_models.py
created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
```

Then after migration:
1. Populate existing rows with `timezone.now()`
2. Make the field NOT NULL again

But the recommended approach is to provide the default during migration (option 1 above).

## Complete Command Sequence

```bash
# 1. Create migrations
docker-compose exec web python manage.py makemigrations

# Answer prompts:
# - FineAppeal rename? [y]
# - BlogCategory default? [1]
# - Default value? [Enter for timezone.now]

# 2. Apply migrations
docker-compose exec web python manage.py migrate

# 3. Verify
docker-compose exec web python manage.py showmigrations
```

## What These Migrations Do

1. **FineAppeal**: Renames `created_at` to `submitted_at` to match the model
2. **BlogCategory**: Adds `created_at` field with `timezone.now` default for existing rows
3. **Communications**: Adds `content_type_id` and `object_id` fields
4. **Orders**: Adds `submitted_at`, `requires_editing`, `editing_skip_reason` fields

After completing these, all admin errors should be resolved!

