# Blog Author/Persona Selection Feature

## Overview

Added the ability to select blog authors/personas when creating or updating blog posts. Authors are filtered by website to ensure multi-tenant compliance.

---

## Features

### 1. **Author Selection Field** ✅

**New Field in BlogPostSerializer:**
- `author_ids` (write-only, array) - Select one or more authors when creating/updating blog posts
- `authors` (read-only) - Returns full author information for display

**Usage:**
```json
POST /api/v1/blog-pages-management/blogs/
{
  "website_id": 1,
  "title": "My Blog Post",
  "content": "...",
  "author_ids": [1, 2, 3]  // Array of author IDs
}
```

### 2. **Available Authors Endpoint** ✅

**API Endpoint:**
```
GET /api/v1/blog-pages-management/blogs/available_authors/?website_id=1
```

**Query Parameters:**
- `website_id` (optional) - Filter authors by website. If not provided:
  - Superadmins: see all authors
  - Regular admins: see authors from their assigned website

**Response:**
```json
{
  "authors": [
    {
      "id": 1,
      "name": "John Doe",
      "bio": "Expert writer...",
      "profile_picture": "/media/...",
      "designation": "Senior Writer",
      "website_name": "Website 1",
      "post_count": 15,
      ...
    }
  ],
  "count": 5
}
```

### 3. **Website-Based Filtering** ✅

- Authors are automatically filtered by the selected website
- When `website_id` is provided, only authors from that website are available
- When updating, authors are validated against the blog post's website
- Serializer dynamically sets the author queryset based on website context

### 4. **Validation** ✅

- **Website Validation:** Ensures selected authors belong to the selected website
- **Active Authors Only:** Only active authors are available for selection
- **Permission Check:** Authors are filtered based on user permissions
- **Multi-Author Support:** Can select multiple authors for a single blog post

---

## Permission Logic

### **Superadmins**
- ✅ Can see all authors from all websites
- ✅ Can select authors from any website (when website_id is provided)
- ✅ If no website_id in query, see all authors

### **Regular Admins**
- ✅ Can only see authors from their assigned website
- ✅ Can only select authors from their assigned website
- ✅ Authors are automatically filtered by their website

---

## API Examples

### Create Blog Post with Author Selection

```json
POST /api/v1/blog-pages-management/blogs/
{
  "website_id": 1,
  "title": "New Blog Post",
  "content": "Content here...",
  "author_ids": [1, 2],  // Select multiple authors
  "status": "draft"
}
```

### Get Available Authors

**With website_id:**
```bash
GET /api/v1/blog-pages-management/blogs/available_authors/?website_id=1
```

**Without website_id (uses user's website):**
```bash
GET /api/v1/blog-pages-management/blogs/available_authors/
```

**Response:**
```json
{
  "authors": [
    {
      "id": 1,
      "name": "John Doe",
      "bio": "Expert content writer...",
      "profile_picture": "/media/author_images/john.jpg",
      "designation": "Senior Writer",
      "website_name": "Website 1",
      "post_count": 15,
      "is_active": true,
      "display_order": 1,
      ...
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "bio": "SEO specialist...",
      ...
    }
  ],
  "count": 2
}
```

### Update Blog Post Authors

```json
PATCH /api/v1/blog-pages-management/blogs/123/
{
  "author_ids": [2, 3]  // Update authors
}
```

---

## Frontend Integration Notes

1. **Get Available Authors:**
   - Call `GET /blogs/available_authors/?website_id=X` when website is selected
   - Store the list for dropdown/multi-select component

2. **Display Author Selector:**
   - Show multi-select dropdown with author names
   - Display author profile pictures if available
   - Show author designation/bio as tooltip or helper text

3. **Website Change Handling:**
   - When website changes, refresh the available authors list
   - Clear selected authors if they don't belong to the new website

4. **Validation:**
   - Frontend should validate that selected authors belong to the selected website
   - Show error message if validation fails

5. **Author Display:**
   - When displaying blog post, show all selected authors
   - Display author profile pictures, names, and designations

---

## Updated Files

### Serializers
- ✅ `blog_pages_management/_legacy_serializers.py`
  - Added `author_ids` field (write-only, many=True)
  - Added `__init__()` method to dynamically set author queryset based on website
  - Authors are filtered by website and active status

### Views
- ✅ `blog_pages_management/_legacy_views.py`
  - Added `available_authors` endpoint
  - Added author validation in `perform_create()`
  - Added author validation in `perform_update()`
  - Authors are validated against the selected website

---

## Validation Rules

1. **Author Website Match:**
   - Selected authors must belong to the selected website
   - Validation error if authors from different website are selected

2. **Active Authors Only:**
   - Only active authors (`is_active=True`) are available for selection
   - Inactive authors are filtered out automatically

3. **Permission-Based Filtering:**
   - Non-superadmins can only see/select authors from their website
   - Superadmins can see all authors but must respect website selection

4. **Multi-Author Support:**
   - Can select multiple authors (ManyToMany relationship)
   - All selected authors must belong to the same website

---

## Workflow

1. **User selects website** → Frontend calls `available_authors?website_id=X`
2. **Frontend displays authors** → User selects one or more authors
3. **User creates/updates post** → Includes `author_ids` in request
4. **Backend validates** → Ensures authors belong to selected website
5. **Post saved** → Authors are associated with the blog post

---

## Error Handling

**Invalid Author IDs:**
```json
{
  "author_ids": ["Some selected authors do not belong to the selected website."]
}
```

**Invalid Website:**
```json
{
  "website_id": ["Invalid website ID."]
}
```

**No Authors Available:**
- If no authors exist for the selected website, the `available_authors` endpoint returns an empty array
- Frontend should show appropriate message

---

## Security

- ✅ Permission validation prevents unauthorized author selection
- ✅ Website-based filtering ensures multi-tenant isolation
- ✅ Active author filtering prevents selection of inactive authors
- ✅ Validation errors provide clear feedback

---

**Status:** ✅ **Complete and Ready for Use!**

Staff can now select blog authors/personas when creating or updating blog posts, with proper website-based filtering and validation.

