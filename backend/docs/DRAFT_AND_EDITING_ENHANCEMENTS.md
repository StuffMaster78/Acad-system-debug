# Draft and Editing Enhancements Guide

## Overview

This document outlines comprehensive draft and editing enhancements for blog posts and service pages, including auto-save, revisions, preview links, edit locks, and collaborative editing features.

## ✅ Completed Features

### 1. **Status Management** ✅
- ✅ `status` field added to `BlogPost` model
- ✅ Status choices: `draft`, `scheduled`, `published`, `archived`
- ✅ Status sync with `is_published` flag
- ✅ Status-based validation (links validation only for published/scheduled)

### 2. **Revision System** ✅
- ✅ `BlogPostRevision` model - Full snapshots of blog posts
- ✅ `ServicePageRevision` model - Full snapshots of service pages
- ✅ Sequential revision numbering
- ✅ Store all content and relationships (authors, tags, category)
- ✅ Mark current revision
- ✅ Revision comparison/diff functionality
- ✅ Restore to previous revision

### 3. **Auto-Save** ✅
- ✅ `BlogPostAutoSave` model - Auto-saved drafts
- ✅ `ServicePageAutoSave` model - Auto-saved service pages
- ✅ Auto-save draft content periodically
- ✅ Recover lost work from autosaves
- ✅ Track recovery status
- ✅ Cleanup old autosaves (Celery task)

### 4. **Edit Locks** ✅
- ✅ `BlogPostEditLock` model - Prevent concurrent editing
- ✅ `ServicePageEditLock` model - Service page edit locks
- ✅ Lock expiration (default: 30 minutes)
- ✅ Lock extension
- ✅ Lock release
- ✅ Automatic cleanup of expired locks

### 5. **Preview System** ✅
- ✅ `BlogPostPreview` model - Preview tokens for draft posts
- ✅ `ServicePagePreview` model - Preview tokens for service pages
- ✅ Secure token-based preview links
- ✅ Token expiration
- ✅ View tracking
- ✅ Deactivate previews

### 6. **API Endpoints** ✅
- ✅ `POST /api/v1/blog/blogs/{id}/create_revision/` - Create revision
- ✅ `POST /api/v1/blog/blogs/{id}/publish/` - Publish blog
- ✅ `POST /api/v1/blog/blogs/{id}/unpublish/` - Unpublish blog
- ✅ `POST /api/v1/blog/blogs/{id}/archive/` - Archive blog
- ✅ `GET /api/v1/blog/blog-revisions/` - List revisions
- ✅ `POST /api/v1/blog/blog-revisions/{id}/restore/` - Restore revision
- ✅ `GET /api/v1/blog/blog-revisions/{id}/diff/` - Get diff
- ✅ `POST /api/v1/blog/blog-autosaves/save_draft/` - Auto-save draft
- ✅ `GET /api/v1/blog/blog-autosaves/latest/` - Get latest autosave
- ✅ `POST /api/v1/blog/blog-autosaves/{id}/recover/` - Recover autosave
- ✅ `POST /api/v1/blog/blog-edit-locks/acquire/` - Acquire edit lock
- ✅ `POST /api/v1/blog/blog-edit-locks/{id}/extend/` - Extend lock
- ✅ `POST /api/v1/blog/blog-edit-locks/{id}/release/` - Release lock
- ✅ `GET /api/v1/blog/blog-edit-locks/check/` - Check lock status
- ✅ `POST /api/v1/blog/blog-previews/create_token/` - Create preview token
- ✅ `POST /api/v1/blog/blog-previews/{id}/deactivate/` - Deactivate preview

### 7. **Celery Tasks** ✅
- ✅ `cleanup_expired_edit_locks()` - Clean up expired locks
- ✅ `cleanup_old_autosaves()` - Clean up old autosaves (7+ days)
- ✅ `auto_publish_scheduled_blogs()` - Auto-publish scheduled posts

### 8. **Admin Interface** ✅
- ✅ Admin for revisions with content view
- ✅ Admin for autosaves
- ✅ Admin for edit locks with expiration status
- ✅ Admin for preview tokens

## Models

### BlogPostRevision
- Stores complete snapshot of blog post at a point in time
- Includes all content fields and relationships
- Sequential revision numbering
- Marks current published version

### BlogPostAutoSave
- Periodic auto-saves of work-in-progress
- User-specific autosaves
- Recovery tracking
- Time-stamped saves

### BlogPostEditLock
- Prevents concurrent editing
- Time-based expiration
- User ownership
- Automatic cleanup

### BlogPostPreview
- Secure token-based previews
- Expiration support
- View tracking
- Share preview links without publishing

## Status Workflow

```
draft → scheduled → published → archived
  ↓        ↓            ↓
  └────────┴────────────┘
      (can unpublish back to draft)
```

### Status Transitions

1. **Draft**: Initial state, work in progress
   - Can be edited freely
   - Not visible to public
   - Internal links validation skipped

2. **Scheduled**: Ready to publish at future date
   - Auto-publishes when `scheduled_publish_date` arrives
   - Internal links validated

3. **Published**: Live and visible
   - Visible to public
   - Internal links validated
   - Can be viewed via preview if needed

4. **Archived**: No longer active
   - Not visible to public
   - Can be restored to draft

## Usage Examples

### Creating a Revision
```python
from blog_pages_management.services.draft_editing_service import DraftEditingService

# Create revision before major changes
revision = DraftEditingService.create_revision(
    blog=blog_post,
    user=request.user,
    change_summary="Updated content and added new section"
)
```

### Restoring a Revision
```python
# Via API
POST /api/v1/blog/blog-revisions/{revision_id}/restore/

# Or programmatically
DraftEditingService.restore_revision(blog, revision, user)
```

### Auto-Saving a Draft
```python
# Via API
POST /api/v1/blog/blog-autosaves/save_draft/
{
    "blog_id": 1,
    "title": "Draft title",
    "content": "Draft content...",
    "meta_title": "Meta title",
    "authors": [1, 2],
    "tags": [3, 4]
}

# Or programmatically
DraftEditingService.auto_save_draft(
    blog=blog_post,
    user=request.user,
    data={
        'title': 'Draft title',
        'content': 'Draft content...'
    }
)
```

### Acquiring Edit Lock
```python
# Via API
POST /api/v1/blog/blog-edit-locks/acquire/
{
    "blog_id": 1,
    "duration_minutes": 30
}

# Response:
{
    "acquired": true,
    "lock": {
        "id": 1,
        "blog": 1,
        "locked_by": 1,
        "expires_at": "2024-01-01T12:30:00Z",
        "time_remaining": "30m"
    }
}

# Or programmatically
lock, acquired = DraftEditingService.acquire_edit_lock(blog, user, 30)
if not acquired:
    print(f"Locked by {lock.locked_by.username}")
```

### Creating Preview Link
```python
# Via API
POST /api/v1/blog/blog-previews/create_token/
{
    "blog_id": 1,
    "expires_hours": 24
}

# Response:
{
    "id": 1,
    "token": "abc123...",
    "preview_url": "https://example.com/blog/preview/abc123.../",
    "expires_at": "2024-01-02T12:00:00Z"
}

# Or programmatically
preview = DraftEditingService.create_preview_token(blog, user, 24)
print(f"Preview URL: {preview.preview_url}")
```

### Publishing/Unpublishing
```python
# Via API
POST /api/v1/blog/blogs/{id}/publish/
POST /api/v1/blog/blogs/{id}/unpublish/
POST /api/v1/blog/blogs/{id}/archive/
```

### Getting Revision Diff
```python
# Via API
GET /api/v1/blog/blog-revisions/{id}/diff/?compare_to={other_revision_id}

# Response:
{
    "from_revision": 1,
    "to_revision": 2,
    "diffs": {
        "content": "--- Revision 1\n+++ Revision 2\n...",
        "title": "- Old Title\n+ New Title"
    }
}
```

## Frontend Integration

### Auto-Save Implementation
```javascript
// Auto-save draft every 30 seconds
let autoSaveInterval;

function startAutoSave(blogId) {
    autoSaveInterval = setInterval(() => {
        const draftData = {
            blog_id: blogId,
            title: document.getElementById('title').value,
            content: editor.getContent(), // From rich text editor
            meta_title: document.getElementById('meta_title').value,
            meta_description: document.getElementById('meta_description').value
        };
        
        fetch('/api/v1/blog/blog-autosaves/save_draft/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(draftData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Draft saved at', data.saved_at);
        })
        .catch(error => {
            console.error('Auto-save failed:', error);
        });
    }, 30000); // 30 seconds
}

function stopAutoSave() {
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
    }
}

// Check for autosave on page load
window.addEventListener('load', () => {
    const blogId = getBlogIdFromURL();
    fetch(`/api/v1/blog/blog-autosaves/latest/?blog_id=${blogId}`)
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                if (confirm('Found an unsaved draft. Recover it?')) {
                    fetch(`/api/v1/blog/blog-autosaves/${data.id}/recover/`, {
                        method: 'POST'
                    })
                    .then(() => location.reload());
                }
            }
        });
});
```

### Edit Lock Implementation
```javascript
// Acquire lock when starting to edit
function startEditing(blogId) {
    fetch('/api/v1/blog/blog-edit-locks/acquire/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            blog_id: blogId,
            duration_minutes: 30
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.acquired) {
            alert(`This post is being edited by ${data.lock.locked_by_username}`);
            return false;
        }
        
        // Extend lock every 20 minutes
        setInterval(() => {
            extendLock(data.lock.id);
        }, 20 * 60 * 1000);
        
        return true;
    });
}

// Release lock when done editing
function stopEditing(lockId) {
    fetch(`/api/v1/blog/blog-edit-locks/${lockId}/release/`, {
        method: 'POST'
    });
}

function extendLock(lockId) {
    fetch(`/api/v1/blog/blog-edit-locks/${lockId}/extend/`, {
        method: 'POST',
        body: JSON.stringify({ duration_minutes: 30 })
    });
}
```

### Revision Comparison UI
```javascript
// Show diff between revisions
function showRevisionDiff(revisionId1, revisionId2) {
    fetch(`/api/v1/blog/blog-revisions/${revisionId1}/diff/?compare_to=${revisionId2}`)
        .then(response => response.json())
        .then(data => {
            // Display diff using a diff viewer library
            displayDiff(data.diffs.content);
        });
}

// Restore revision
function restoreRevision(revisionId) {
    if (confirm('Restore this revision? This will create a new revision.')) {
        fetch(`/api/v1/blog/blog-revisions/${revisionId}/restore/`, {
            method: 'POST'
        })
        .then(() => {
            alert('Revision restored successfully');
            location.reload();
        });
    }
}
```

### Preview Link Sharing
```javascript
// Create preview link
function createPreviewLink(blogId) {
    fetch('/api/v1/blog/blog-previews/create_token/', {
        method: 'POST',
        body: JSON.stringify({
            blog_id: blogId,
            expires_hours: 24
        })
    })
    .then(response => response.json())
    .then(data => {
        // Copy preview URL to clipboard
        navigator.clipboard.writeText(data.preview_url);
        alert('Preview link copied to clipboard!');
    });
}
```

## Celery Task Configuration

Add to `celery.py` or scheduling:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-expired-locks': {
        'task': 'blog_pages_management.tasks.cleanup_expired_edit_locks',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'cleanup-old-autosaves': {
        'task': 'blog_pages_management.tasks.cleanup_old_autosaves',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'auto-publish-scheduled': {
        'task': 'blog_pages_management.tasks.auto_publish_scheduled_blogs',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}
```

## Admin Interface Features

### Revision Management
- View all revisions for a blog post
- See revision numbers, dates, and change summaries
- Restore revisions directly from admin
- View revision content

### Auto-Save Management
- View all autosaves for a blog post
- See save timestamps and recovery status
- Manually recover autosaves

### Edit Lock Management
- View active locks
- See lock owners and expiration times
- Manually release locks if needed
- View expired locks

### Preview Token Management
- View all preview tokens
- See expiration dates and view counts
- Manually deactivate previews
- Copy preview URLs

## Testing Checklist

- [ ] Create blog post revision
- [ ] Restore to previous revision
- [ ] Get diff between revisions
- [ ] Auto-save draft
- [ ] Recover autosave
- [ ] Acquire edit lock
- [ ] Extend edit lock
- [ ] Release edit lock
- [ ] Check lock status
- [ ] Create preview token
- [ ] View preview via token
- [ ] Deactivate preview
- [ ] Publish blog post
- [ ] Unpublish blog post
- [ ] Archive blog post
- [ ] Auto-publish scheduled blog
- [ ] Cleanup expired locks (Celery)
- [ ] Cleanup old autosaves (Celery)

## Migration Instructions

1. **Create Migrations**:
```bash
python manage.py makemigrations blog_pages_management
```

2. **Run Migrations**:
```bash
python manage.py migrate blog_pages_management
```

3. **Create Initial Revisions** (optional data migration):
```python
# Create initial revisions for existing published posts
from blog_pages_management.models import BlogPost
from blog_pages_management.services.draft_editing_service import DraftEditingService

for blog in BlogPost.objects.filter(is_published=True):
    DraftEditingService.create_revision(
        blog,
        blog.last_edited_by or blog.authors.first(),
        "Initial revision"
    )
```

## Production Considerations

### Performance
- Index revisions by blog and created_at
- Clean up old autosaves regularly
- Limit number of revisions kept per blog (configurable)
- Cache lock status checks

### Security
- Validate preview token expiration
- Limit preview token duration
- Rate limit auto-save requests
- Prevent lock hijacking (verify user ownership)

### User Experience
- Show lock status in UI
- Display "Last saved" indicator
- Warn before losing unsaved changes
- Auto-recover autosaves on page load
- Show revision comparison in side-by-side view

## Future Enhancements

1. **Revision Limits**: Keep only last N revisions, archive older ones
2. **Revision Comments**: Add comments to revisions explaining changes
3. **Collaborative Editing**: Real-time collaborative editing (WebSocket)
4. **Change Suggestions**: Suggest edits/review workflow
5. **Export Revisions**: Export revision as JSON/HTML
6. **Revision Branching**: Branch from specific revision
7. **Draft Templates**: Save drafts as templates for reuse
8. **Draft Sharing**: Share drafts with team members
9. **Auto-Save Throttling**: Throttle autosaves based on change frequency
10. **Visual Diff**: Visual diff viewer with syntax highlighting

