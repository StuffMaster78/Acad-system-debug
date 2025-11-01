# Discount Configuration Admin Access

## Summary

**Question:** Can superadmin and admin set the maximum discount caps and stacking rules?

**Answer:** 
- ✅ **Stacking Rules** - Yes, already available
- ✅ **Maximum Discount Caps** - Yes, now available (was missing, now added)
- ✅ **Individual Discount Settings** - Yes, already available

---

## What Admins Can Now Manage

### 1. **Discount Configuration (Global Settings)** ✅ NEWLY ADDED

**Admin Path:** Django Admin → Discount Configurations

**What Can Be Configured:**
- **Maximum Stackable Discounts** (`max_stackable_discounts`)
  - Default: 1
  - Controls how many discount codes can be applied to a single order
  
- **Maximum Discount Percent** (`max_discount_percent`)
  - Default: 30%
  - Maximum total discount percentage allowed per order
  
- **Discount Threshold** (`discount_threshold`)
  - Default: $100.00
  - Minimum order total required (after first discount) to allow stacking additional discounts
  
- **Enable Stacking** (`enable_stacking`)
  - Default: True
  - Master switch to enable/disable discount stacking
  
- **Allow Stack Across Events** (`allow_stack_across_events`)
  - Default: False
  - Allow stacking discounts from different promotional campaigns
  
- **Promotional Campaign Settings**
  - Enable/disable promotional discounts
  - Set promotional discount value

**Per-Website Configuration:**
- Each website can have its own `DiscountConfig`
- Settings are website-specific (OneToOne relationship)

---

### 2. **Discount Stacking Rules** ✅ ALREADY AVAILABLE

**Admin Path:** Django Admin → Discount Stacking Rules

**What Can Be Configured:**
- Define which specific discounts can be stacked together
- Set stacking priority
- Create explicit stacking relationships between discounts

**Example:**
- Discount A can stack with Discount B
- Discount B can stack with Discount C
- But Discount A cannot stack with Discount C (unless explicitly defined)

---

### 3. **Individual Discount Settings** ✅ ALREADY AVAILABLE

**Admin Path:** Django Admin → Discounts

**What Can Be Configured Per Discount:**
- `stackable` - Whether this discount can be stacked
- `stacking_priority` - Order of application (higher priority first)
- `max_discount_percent` - Per-discount maximum cap
- `max_stackable_uses_per_customer` - How many times customer can use this in a stack
- `stackable_with` - Which other discounts this can stack with

---

## Admin Interface Features

### DiscountConfigAdmin Features:

1. **Organized Fieldsets:**
   - Stacking Configuration
   - Discount Limits
   - Promotional Settings
   - User Experience
   - Audit Information

2. **List View:**
   - Shows key settings at a glance
   - Filterable by website, stacking settings
   - Searchable by website name/domain

3. **Audit Tracking:**
   - Automatically tracks `created_by` and `updated_by`
   - Shows `created_at` and `updated_at` timestamps

4. **Validation:**
   - One config per website (enforced by OneToOne relationship)
   - All fields have helpful descriptions

---

## Access Control

**By Default:**
- Users with `is_staff=True` can access Django admin
- Users with `is_superuser=True` have all permissions automatically
- Regular admins may need explicit permissions (depends on your permission setup)

**To Restrict Access Further:**
You can add custom permission checks in `DiscountConfigAdmin`:

```python
def has_change_permission(self, request, obj=None):
    # Only superusers and staff with specific permission
    if request.user.is_superuser:
        return True
    return request.user.has_perm('discounts.change_discountconfig')

def has_add_permission(self, request):
    if request.user.is_superuser:
        return True
    return request.user.has_perm('discounts.add_discountconfig')
```

---

## Configuration Priority

When discounts are applied, the system checks settings in this order:

1. **Global Config** (`DiscountConfig` for website)
   - Max stackable discounts
   - Max discount percent
   - Discount threshold
   - Stacking enabled/disabled

2. **Stacking Rules** (`DiscountStackingRule`)
   - Explicit rules about which discounts can stack

3. **Individual Discount Settings**
   - Per-discount stacking flags
   - Per-discount max percent

**Example Flow:**
```
1. Check DiscountConfig: max_stackable_discounts = 2 ✅
2. Check DiscountStackingRule: Can Discount A stack with Discount B? ✅
3. Check Discount A: stackable = True ✅
4. Check Discount B: stackable = True ✅
5. Apply discounts, checking max_discount_percent from DiscountConfig
```

---

## Creating a Discount Config

**Steps:**
1. Go to Django Admin → Discount Configurations
2. Click "Add Discount Configuration"
3. Select the website
4. Configure settings:
   - Set max stackable discounts (e.g., 2)
   - Set max discount percent (e.g., 30%)
   - Set discount threshold (e.g., $100)
   - Enable/disable stacking features
5. Save

**Note:** Each website can only have ONE DiscountConfig (OneToOne relationship).

---

## Testing Admin Access

To verify admins can manage settings:

1. **Test Discount Config Access:**
   ```python
   # In Django shell or test
   from discounts.models.discount_configs import DiscountConfig
   from websites.models import Website
   
   website = Website.objects.first()
   config, created = DiscountConfig.objects.get_or_create(
       website=website,
       defaults={
           'max_stackable_discounts': 3,
           'max_discount_percent': 40.00,
           'discount_threshold': 150.00,
       }
   )
   ```

2. **Test via Admin Interface:**
   - Log in as superadmin/admin
   - Navigate to `/admin/discounts/discountconfig/`
   - Create or edit a configuration
   - Verify changes take effect (they're cached for 5 minutes)

---

## Cache Considerations

**Note:** `DiscountConfig` values are cached for 5 minutes (300 seconds) for performance.

If admins change settings and want immediate effect:
- Wait 5 minutes for cache to expire, OR
- Restart the application server, OR
- Clear the cache manually in `DiscountConfigService._CACHE`

---

## Summary

✅ **Superadmins and Admins can now:**
- Set maximum discount caps per website
- Configure stacking rules (how many discounts, thresholds)
- Manage individual discount stacking settings
- Define explicit stacking relationships between discounts

All critical discount settings are now manageable through the Django admin interface!
