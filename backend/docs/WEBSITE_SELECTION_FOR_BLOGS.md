# Website Selection for Blog Posts and Service Pages

## Overview

Added website selection capability for blog posts and service pages in the multi-tenant system. Users can now explicitly select which website a blog post or service page belongs to when creating or updating.

---

## Features

### 1. **Website Selection in Blog Posts** ✅

**API Endpoint:** `/api/v1/blog-pages-management/blogs/`

**New Field:**
- `website_id` (write-only) - Select website when creating/updating blog posts
- `website` (read-only) - Returns website info (id, name, domain) for display

**Usage:**
```json
POST /api/v1/blog-pages-management/blogs/
{
  "website_id": 1,
  "title": "My Blog Post",
  "content": "...",
  ...
}
```

### 2. **Website Selection in Service Pages** ✅

**API Endpoint:** `/api/v1/service-pages-management/service-pages/`

**New Field:**
- `website_id` (write-only) - Select website when creating/updating service pages
- `website` (read-only) - Returns website info (id, name, domain) for display

**Usage:**
```json
POST /api/v1/service-pages-management/service-pages/
{
  "website_id": 1,
  "title": "My Service Page",
  "content": "...",
  ...
}
```

### 3. **Available Websites Endpoint** ✅

**Blog Posts:**
```
GET /api/v1/blog-pages-management/blogs/available_websites/
```

**Service Pages:**
```
GET /api/v1/service-pages-management/service-pages/available_websites/
```

**Response:**
```json
{
  "websites": [
    {
      "id": 1,
      "name": "Website Name",
      "domain": "example.com",
      ...
    }
  ],
  "can_select_website": true  // true for superadmin, false for regular admin
}
```

---

## Permission Logic

### **Superadmins**
- ✅ Can select **any** active website
- ✅ Can see all websites in the available_websites endpoint
- ✅ Can change website when updating posts/pages

### **Regular Admins**
- ✅ Can only select their **assigned website**
- ✅ See only their website in the available_websites endpoint
- ✅ Cannot change website to a different one
- ✅ If no website_id provided, auto-assigned to their website
- ❌ Cannot create posts/pages for other websites

---

## Auto-Assignment

If `website_id` is not provided:
- **Superadmins:** Must provide website_id (validation error)
- **Regular Admins:** Auto-assigned to their website
- **Users without website:** Validation error asking to select website

---

## Validation

1. **Website Existence:** Validates that the provided website_id exists
2. **Website Status:** Only allows selection of active, non-deleted websites
3. **Permission Check:** Validates user has permission to use the selected website
4. **Queryset Filtering:** Serializer automatically filters available websites based on user role

---

## Updated Files

### Blog Posts
- ✅ `blog_pages_management/_legacy_serializers.py`
  - Added `website_id` field (write-only)
  - Enhanced `website` field (read-only, returns object)
  
- ✅ `blog_pages_management/_legacy_views.py`
  - Added `perform_create()` with website selection logic
  - Added `perform_update()` with website change validation
  - Added `available_websites` endpoint
  - Updated `get_queryset()` to filter by website for non-superadmins

### Service Pages
- ✅ `service_pages_management/_legacy_serializers.py`
  - Added `website_id` field (write-only, dynamic queryset)
  - Enhanced `website` field (read-only, returns object)
  - Added `__init__()` to set queryset based on user role
  
- ✅ `service_pages_management/_legacy_views.py`
  - Added `perform_create()` with website selection logic
  - Added `perform_update()` with website change validation
  - Added `available_websites` endpoint
  - Updated `get_queryset()` to filter by website for non-superadmins

---

## API Examples

### Create Blog Post with Website Selection

**Superadmin:**
```json
POST /api/v1/blog-pages-management/blogs/
{
  "website_id": 2,
  "title": "New Blog Post",
  "content": "Content here...",
  "status": "draft"
}
```

**Regular Admin (auto-assigned):**
```json
POST /api/v1/blog-pages-management/blogs/
{
  "title": "New Blog Post",
  "content": "Content here...",
  "status": "draft"
  // website_id not needed - auto-assigned to admin's website
}
```

### Get Available Websites

```bash
GET /api/v1/blog-pages-management/blogs/available_websites/
```

**Response (Superadmin):**
```json
{
  "websites": [
    {"id": 1, "name": "Website 1", "domain": "site1.com"},
    {"id": 2, "name": "Website 2", "domain": "site2.com"}
  ],
  "can_select_website": true
}
```

**Response (Regular Admin):**
```json
{
  "websites": [
    {"id": 1, "name": "My Website", "domain": "mywebsite.com"}
  ],
  "can_select_website": false
}
```

---

## Frontend Integration Notes

1. **Check `can_select_website`** to show/hide website selector
2. **If `can_select_website: false`**, don't show website dropdown (auto-assigned)
3. **If `can_select_website: true`**, show website dropdown with all available websites
4. **Call `available_websites` endpoint** to populate the dropdown
5. **Include `website_id`** in POST/PUT requests when website is selected

---

## Security

- ✅ Permission validation prevents unauthorized website assignment
- ✅ Queryset filtering ensures users only see their allowed websites
- ✅ Validation errors provide clear feedback
- ✅ All actions are logged (via existing activity logging)

---

**Status:** ✅ **Complete and Ready for Use!**

Staff can now explicitly select which website a blog post or service page belongs to, with proper permission validation and multi-tenant support.

