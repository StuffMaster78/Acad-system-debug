# Bugs Fixed - January 30, 2026

## Summary
Fixed critical bugs across the application:
- `UnboundLocalError` in admin dashboard causing 500 errors
- Invalid `related_name` causing Django system check failure
- Import errors causing Celery worker and beat containers to crash
- Missing model exports and properties

## Bugs Fixed

### 1. ❌ **Critical: UnboundLocalError in AdminDashboardView**

**Location:** `backend/admin_management/views.py:129`

**Error:**
```
UnboundLocalError: cannot access local variable 'cache_key' where it is not associated with a value
```

**Problem:**
```python
# WRONG - cache_key only defined inside if block
if request.query_params.get('refresh') == 'true':
    cache_key = DashboardMetricsService.get_cache_key(request.user, "summary")
    cache.delete(cache_key)

# Later, outside the if block...
cached_result = cache.get(cache_key)  # ❌ cache_key not defined if refresh != 'true'
```

The `cache_key` variable was only being defined inside the `if` block when `refresh='true'`, but it was being used outside the block. When a normal dashboard request came in (without `refresh='true'`), the variable was never defined, causing the error.

**Fix:**
```python
# CORRECT - cache_key defined before if block
cache_key = DashboardMetricsService.get_cache_key(request.user, "summary")

if request.query_params.get('refresh') == 'true':
    cache.delete(cache_key)

# Later...
cached_result = cache.get(cache_key)  # ✅ cache_key always defined
```

**Impact:** This was causing the admin dashboard to crash with a 500 Internal Server Error for all users trying to access `/api/v1/admin-management/dashboard/`.

---

### 2. ❌ **Critical: Invalid related_name in CTABlock Model**

**Location:** `backend/blog_pages_management/models/content_blocks.py:42`

**Error:**
```
blog_pages_management.CTABlock.website: (fields.E306) The name 'cta-blocks' is invalid related_name for field CTABlock.website
HINT: Related name must be a valid Python identifier or end with a '+'
```

**Problem:**
```python
# WRONG - hyphen is not valid in Python identifier
website = models.ForeignKey(
    'websites.Website',
    on_delete=models.CASCADE,
    related_name='cta-blocks'
)
```

The `related_name` contained a hyphen (`cta-blocks`), which is not a valid Python identifier. Related names are used to access the reverse relationship from the related model (e.g., `website.cta_blocks.all()`), so they must follow Python variable naming rules.

**Fix:**
```python
# CORRECT - underscore is valid
website = models.ForeignKey(
    'websites.Website',
    on_delete=models.CASCADE,
    related_name='cta_blocks'
)
```

**Impact:** This was causing Django's system check to fail, preventing the web server from starting.

---

### 3. ❌ **Critical: Incorrect Import in analytics_models.py**

**Location:** `backend/blog_pages_management/models/analytics_models.py:9`

**Error:**
```python
ModuleNotFoundError: No module named 'workflow_models'
```

**Problem:**
```python
# WRONG - absolute import
from workflow_models import WorkflowTransition
```

The import was using an absolute import path `from workflow_models import` instead of a relative import. Since `workflow_models.py` is in the same package (`blog_pages_management/models/`), it should use a relative import.

**Fix:**
```python
# CORRECT - relative import
from .workflow_models import WorkflowTransition
```

**Impact:** This was causing both Celery worker and beat containers to crash on startup, preventing all background task processing.

---

### 4. ❌ **Missing Model Exports in __init__.py**

**Location:** `backend/blog_pages_management/models/__init__.py`

**Problem:**
Several models from `analytics_models.py` were not being exported in the models package `__init__.py`, making them inaccessible to other parts of the application (like tasks.py).

**Missing Models:**
- `WebsiteContentMetrics`
- `WebsitePublishingTarget`
- `CategoryPublishingTarget`
- `ContentFreshnessReminder`

**Fix:**
Updated the import statement in `__init__.py`:
```python
from .analytics_models import (
    EditorAnalytics,
    BlogPostAnalytics,
    ContentPerformanceMetrics,
    WebsiteContentMetrics,           # ✅ Added
    WebsitePublishingTarget,         # ✅ Added
    CategoryPublishingTarget,        # ✅ Added
    ContentFreshnessReminder,        # ✅ Added
)
```

Also updated the `__all__` list to include these models.

**Impact:** Tasks in `tasks.py` that use these models (e.g., `recalculate_website_content_metrics`, `send_content_freshness_reminders`, `send_monthly_publishing_reminders`) would fail with `AttributeError` or `ImportError`.

---

### 5. ❌ **Missing Property in ContentFreshnessReminder Model**

**Location:** `backend/blog_pages_management/models/analytics_models.py` (ContentFreshnessReminder model)

**Problem:**
The `send_content_freshness_reminders` task in `tasks.py` was referencing `reminder.days_since_update` (lines 596 and 603), but the `ContentFreshnessReminder` model didn't have this property defined.

**Fix:**
Added the missing property to the `ContentFreshnessReminder` model:
```python
@property
def days_since_update(self):
    """Calculate days since the blog post was last updated."""
    if self.blog_post.updated_at:
        delta = timezone.now() - self.blog_post.updated_at
        return delta.days
    return 0
```

**Impact:** The `send_content_freshness_reminders` Celery task would crash with `AttributeError: 'ContentFreshnessReminder' object has no attribute 'days_since_update'`.

---

## ✅ Not Bugs (Verified as Correct)

### String References to 'websites.Website'

**Status:** ✅ **CORRECT - NOT A BUG**

Throughout the codebase, there are many ForeignKey fields that reference `'websites.Website'` as a string:
```python
website = models.ForeignKey('websites.Website', on_delete=models.CASCADE)
```

**Why this is correct:**
This is the recommended Django pattern for referencing models from other apps. It prevents circular import issues and allows Django to resolve the reference during the app loading process.

**Alternative (not recommended):**
```python
from websites.models import Website
website = models.ForeignKey(Website, on_delete=models.CASCADE)
```
This can cause circular import errors if both apps reference each other's models.

**Reference:** Django Documentation - [Lazy relationships](https://docs.djangoproject.com/en/stable/ref/models/fields/#foreignkey)

---

## Testing Recommendations

Before deploying, verify the fixes by:

1. **Test Celery Worker:**
   ```bash
   docker-compose up celery
   ```
   Should start without `ModuleNotFoundError`.

2. **Test Celery Beat:**
   ```bash
   docker-compose up beat
   ```
   Should start without import errors.

3. **Test Task Imports:**
   ```bash
   docker-compose exec celery python manage.py shell
   ```
   Then in the shell:
   ```python
   from blog_pages_management.models import (
       WorkflowTransition,
       WebsiteContentMetrics,
       ContentFreshnessReminder,
       WebsitePublishingTarget,
       CategoryPublishingTarget
   )
   print("All imports successful!")
   ```

4. **Test Analytics Tasks:**
   ```bash
   docker-compose exec celery python manage.py shell
   ```
   Then:
   ```python
   from blog_pages_management.tasks import (
       recalculate_website_content_metrics,
       send_content_freshness_reminders,
       send_monthly_publishing_reminders
   )
   print("Task imports successful!")
   ```

---

## Files Modified

1. `backend/admin_management/views.py`
   - Fixed `UnboundLocalError` by moving `cache_key` definition outside if block (line 108-113)

2. `backend/blog_pages_management/models/content_blocks.py`
   - Fixed invalid `related_name` from `'cta-blocks'` to `'cta_blocks'` (line 42)

3. `backend/blog_pages_management/models/analytics_models.py`
   - Fixed import statement (line 9)
   - Added `days_since_update` property to `ContentFreshnessReminder` model

4. `backend/blog_pages_management/models/__init__.py`
   - Added missing model imports from `analytics_models`
   - Updated `__all__` list

---

## Root Cause Analysis

The issues occurred because:

1. **Import Pattern Inconsistency:** The codebase uses relative imports throughout, but one absolute import slipped through in `analytics_models.py`.

2. **Incomplete Model Exports:** When new models were added to `analytics_models.py`, they weren't exported in the package's `__init__.py`, making them invisible to the rest of the application.

3. **Missing Property:** A property was referenced in tasks before it was implemented in the model, indicating that the task was written or updated without the corresponding model changes.

---

## Prevention Strategies

To prevent similar issues in the future:

1. **Consistent Import Patterns:** Always use relative imports within the same app (e.g., `from .workflow_models import ...`)

2. **Complete Model Exports:** When adding new models to submodules, always update the package `__init__.py` to export them

3. **Test Imports Early:** Run Django checks after adding models:
   ```bash
   python manage.py check
   ```

4. **Linting:** Consider using tools like `pylint` or `flake8` to catch import issues early

---

## Status: ✅ RESOLVED

All identified bugs have been fixed. The Celery workers and beat scheduler should now start successfully without import errors.
