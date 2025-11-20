# Order Files System - Issues & Fixes

## Critical Issues Found

### 1. **CRITICAL: `payment_status` field doesn't exist on Order model**

**Location:** `order_files/models.py:91`

**Problem:**
```python
if self.category.is_final_draft and self.order.payment_status != "paid":
```

The `Order` model doesn't have a `payment_status` field. This will cause an `AttributeError` at runtime.

**Fix:** Check payment status via `OrderPayment` model or use `order.is_paid`:
```python
# Option 1: Use is_paid boolean field
if self.category.is_final_draft and not self.order.is_paid:
    return False

# Option 2: Check via OrderPayment model (more accurate)
from order_payments_management.models import OrderPayment
has_completed_payment = OrderPayment.objects.filter(
    order=self.order,
    status__in=['completed', 'succeeded']
).exists()
if self.category.is_final_draft and not has_completed_payment:
    return False
```

---

### 2. **BUG: OrderFilesConfig.get_config() uses hardcoded id=1**

**Location:** `order_files/models.py:28-31`

**Problem:**
```python
@classmethod
def get_config(cls):
    """Ensures there's always one OrderFilesConfig instance available"""
    config, created = cls.objects.get_or_create(id=1)
    return config
```

Issues:
- The model has a `website` ForeignKey, so configs should be website-specific
- Hardcoding `id=1` will fail if that ID doesn't exist or belongs to a different website
- In a multi-tenant system, each website needs its own config

**Fix:**
```python
@classmethod
def get_config(cls, website=None):
    """Get or create OrderFilesConfig for a website."""
    if website is None:
        # Try to get from thread-local or request context
        from core.tenant_context import get_current_website
        website = get_current_website()
    
    if not website:
        # Fallback: get first active website or create default
        website = Website.objects.filter(is_active=True).first()
        if not website:
            raise ValueError("No active website found")
    
    config, created = cls.objects.get_or_create(website=website)
    return config
```

---

### 3. **Potential NULL reference error**

**Location:** `order_files/models.py:91`

**Problem:**
```python
if self.category.is_final_draft and self.order.payment_status != "paid":
```

If `self.category` is `None` (since it's nullable), this will raise `AttributeError`.

**Fix:**
```python
if self.category and self.category.is_final_draft and not self.order.is_paid:
    return False
```

---

### 4. **BUG: ExtraServiceFile.__str__() references non-existent field**

**Location:** `order_files/models.py:236`

**Problem:**
```python
def __str__(self):
    return f"Extra Service File - {self.service_name} (Order {self.order.id})"
```

The model doesn't have a `service_name` field. It has `category` which is an FK to `OrderFileCategory`.

**Fix:**
```python
def __str__(self):
    category_name = self.category.name if self.category else "Unknown"
    return f"Extra Service File - {category_name} (Order {self.order.id})"
```

---

### 5. **Missing file extension validation**

**Location:** `order_files/views.py:27-36`

**Problem:**
The `perform_create` method only checks file size but doesn't validate file extensions against `OrderFilesConfig.allowed_extensions`.

**Fix:** Add extension validation:
```python
def perform_create(self, serializer):
    """Ensures file upload is done by authorized users only."""
    config = OrderFilesConfig.get_config()
    
    file_obj = self.request.FILES["file"]
    
    # Enforce file size limit
    max_size_mb = config.max_upload_size if config else 100
    if file_obj.size > max_size_mb * 1024 * 1024:
        raise serializers.ValidationError(
            f"File too large. Max size is {max_size_mb}MB."
        )
    
    # Validate file extension
    if config.allowed_extensions:
        file_ext = file_obj.name.split('.')[-1].lower()
        if file_ext not in [ext.lower() for ext in config.allowed_extensions]:
            raise serializers.ValidationError(
                f"File extension '{file_ext}' not allowed. "
                f"Allowed extensions: {', '.join(config.allowed_extensions)}"
            )
    
    serializer.save(uploaded_by=self.request.user)
```

---

### 6. **Missing website context in views**

**Location:** `order_files/views.py`

**Problem:**
Views don't filter by website or set website when creating files. In a multi-tenant system, files should be website-specific.

**Fix:** Add website filtering and setting:
```python
def get_queryset(self):
    """Filter files by current website."""
    website = self.get_website()  # Implement get_website method
    if website:
        return self.queryset.filter(website=website)
    return self.queryset

def perform_create(self, serializer):
    # ... existing validation ...
    website = self.get_website()
    if not website:
        raise serializers.ValidationError("Website context required")
    serializer.save(uploaded_by=self.request.user, website=website)
```

---

## Order Files System Overview

### Current Architecture

The order files system consists of:

1. **OrderFile**: Main file storage model
   - Links to Order via FK
   - Has categories (Final Draft, Order Instructions, etc.)
   - Tracks uploader, download permissions
   - **Related name:** `order.files.all()`

2. **OrderFileCategory**: File categories
   - Examples: "Final Draft", "Order Instructions", "Plagiarism Report"
   - Can mark categories as `is_final_draft` or `is_extra_service`

3. **OrderFilesConfig**: Admin configuration
   - File size limits
   - Allowed extensions
   - External link settings

4. **FileDownloadLog**: Download tracking
   - Audit trail of who downloaded what

5. **FileDeletionRequest**: Deletion workflow
   - Clients/writers request deletion
   - Admins approve/reject

6. **ExternalFileLink**: External file support
   - Google Drive, Dropbox links
   - Requires admin approval

7. **ExtraServiceFile**: Extra service files
   - Plagiarism reports, Smart Papers, etc.
   - Separate from regular order files

### API Endpoints

- `GET/POST /api/v1/order-files/` - List/upload files
- `GET /api/v1/order-files/{id}/` - Get file details
- `POST /api/v1/order-files/{id}/toggle_download/` - Toggle download permission
- `GET/POST /api/v1/file-deletion-requests/` - Deletion requests
- `GET/POST /api/v1/external-file-links/` - External links
- `GET/POST /api/v1/extra-service-files/` - Extra service files

### Integration Points

**Order Model:**
- `Order.files.all()` - Access files via related_name
- Files are linked via FK: `OrderFile.order`

**Notifications:**
- `order.file_uploaded` event is emitted (see `orders/notification_emitters.py`)
- Handlers notify clients/writers when files are uploaded

---

## Recommended Fixes Priority

1. **HIGH:** Fix `payment_status` reference (will crash)
2. **HIGH:** Fix `ExtraServiceFile.__str__()` (will crash)
3. **MEDIUM:** Fix NULL category check (potential crash)
4. **MEDIUM:** Fix `OrderFilesConfig.get_config()` to be website-aware
5. **LOW:** Add file extension validation
6. **LOW:** Add website filtering to views

