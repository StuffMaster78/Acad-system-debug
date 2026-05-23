# Getting Started — CMS Platform Developer Guide

## Quick Start

```bash
# 1. Install dependencies
pip install wagtail modelcluster django-taggit Pillow boto3

# 2. Add to INSTALLED_APPS (in order)
# See settings section below

# 3. Run migrations
python manage.py migrate

# 4. Create tenant sites
python manage.py setup_tenants

# 5. Create a superuser
python manage.py createsuperuser

# 6. Start the server
python manage.py runserver

# 7. Open Wagtail admin
# http://localhost:8000/cms-admin/
```

## Architecture in 30 Seconds

```
Vue/Nuxt Frontend (public sites)
    ↓ consumes
Wagtail API v2 (/api/v2/pages/) + CMS API (/cms-api/)
    ↓ served by
Django + Wagtail (publishing engine)
    ↓ stores in
PostgreSQL (one database, multi-tenant via site FK)
    ↓ files in
DigitalOcean Spaces (via files_management)
```

**The funnel:** Blog posts → Service pages → Orders.
Everything in the platform serves this funnel.

## The 11 Apps

| App | What it does | Key model |
|---|---|---|
| `cms_core` | Foundation — blocks, validators, tenant bridge, permissions, workflow | TenantHomePage |
| `cms_authors` | Real authors with credentials | Author (Snippet) |
| `cms_blog` | Blog posts (top of funnel) | BlogPostPage (Wagtail Page) |
| `cms_service_pages` | Service/landing pages (bottom of funnel) | ServicePage (Wagtail Page) |
| `cms_content_graph` | Pillars, funnels, internal linking | ContentPillar |
| `cms_references` | External sources cited in posts | Reference (Snippet) |
| `cms_attachments` | Downloadable files with gating | Attachment (Snippet) |
| `cms_engagement` | Views, reactions, shares, bookmarks | PageView |
| `cms_intelligence` | GSC/GA4, freshness, diagnostics | ContentPerformanceSnapshot |
| `cms_newsletters` | Email subscribers, automation | Subscriber |
| `files_management` | Centralized file storage | ManagedFile |

## Page Tree Structure

```
Root Page
├── NurseMyGrade Home
│   ├── Blog
│   │   ├── How to Write a Care Plan (BlogPostPage)
│   │   └── ...
│   ├── Services
│   │   ├── Nursing Essay Writing Help (ServicePage)
│   │   └── ...
│   ├── Authors
│   └── Resources
├── GradeCrest Home
│   ├── Blog / Services / Authors / Resources
└── EssayManiacs Home
    ├── Blog / Services / Authors / Resources
```

## Settings Required

```python
INSTALLED_APPS = [
    # Wagtail (before django.contrib)
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.embeds", "wagtail.sites", "wagtail.users",
    "wagtail.snippets", "wagtail.documents", "wagtail.images",
    "wagtail.search", "wagtail.admin", "wagtail",
    "modelcluster", "taggit",

    # Django
    "django.contrib.admin", "django.contrib.auth",
    "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles",

    # CMS apps (dependency order)
    "files_management",
    "cms_core",
    "cms_authors",
    "cms_blog",
    "cms_service_pages",
    "cms_content_graph",
    "cms_references",
    "cms_attachments",
    "cms_engagement",
    "cms_intelligence",
    "cms_newsletters",

    # Your existing apps...
]

MIDDLEWARE = [
    # ... existing ...
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "cms_core.middleware.TenantMiddleware",
]

# Celery beat
CELERY_BEAT_SCHEDULE = {
    "tenant-health-check": {
        "task": "cms_core.tasks.tenant_health_check",
        "schedule": 86400,
    },
    "recalculate-file-quotas": {
        "task": "files_management.tasks.recalculate_all_quotas",
        "schedule": 86400,
    },
    "cleanup-expired-files": {
        "task": "files_management.tasks.cleanup_expired_files",
        "schedule": 86400,
    },
    "compute-engagement-summaries": {
        "task": "cms_engagement.tasks.compute_engagement_summaries",
        "schedule": 86400,
    },
    "pull-gsc-data": {
        "task": "cms_intelligence.tasks.pull_gsc_data",
        "schedule": 86400,
    },
    "pull-ga4-data": {
        "task": "cms_intelligence.tasks.pull_ga4_data",
        "schedule": 86400,
    },
    "compute-performance-snapshots": {
        "task": "cms_intelligence.tasks.compute_performance_snapshots",
        "schedule": 86400,
    },
    "scan-content-freshness": {
        "task": "cms_intelligence.tasks.scan_freshness",
        "schedule": 86400,
    },
}
```

## URLs Required

```python
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from cms_core.api import api_router

urlpatterns = [
    path("admin/", admin.site.urls),           # Django admin
    path("cms-admin/", include(wagtailadmin_urls)),  # Wagtail admin
    path("api/v2/", api_router.urls),           # Wagtail headless API
    path("cms-api/", include("cms_core.urls")), # CMS business logic API
    # ... your existing URLs ...
    path("", include(wagtail_urls)),            # Wagtail page serving (LAST)
]
```

## Running Tests

```bash
pip install pytest pytest-django factory-boy
pytest cms_core/ cms_blog/ cms_content_graph/ cms_engagement/
```

## Common Tasks

### Create a blog post (Wagtail admin)
1. Go to `/cms-admin/`
2. Navigate to Pages → [Tenant] Home → Blog
3. Click "Add child page" → "Blog Post"
4. Fill in title, author, content blocks, service route
5. Submit for moderation or publish directly

### Create a service page
Same flow, under Services instead of Blog.

### Set up a content pillar
1. Django admin → Content Pillars → Add
2. Name the pillar, select the service page, optionally set hub post
3. On each blog post in the pillar, set the `pillar` field

### Add an author
1. Wagtail admin → Snippets → Authors → Add
2. Fill credentials, bio, external links
3. Create an Author Page under Authors index for the public profile

### Upload a file
```python
from files_management.services import StorageService

managed_file = StorageService.upload(
    file_obj=my_file,
    bucket=bucket,
    website=website,
    uploaded_by=user,
    file_kind="cms_attachment",
)
```

### Check content freshness
```bash
python manage.py shell
>>> from cms_intelligence.tasks import scan_freshness
>>> scan_freshness()
```
