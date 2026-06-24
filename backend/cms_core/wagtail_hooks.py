"""
Wagtail Hooks for CMS Core
============================

Registers:
- Pre-publish validation (before_publish_page) — three-tier blocker/warning/suggestion
- Post-publish audit (after_publish_page) — queues a Celery task to verify page health
- Reserved slug enforcement (before_publish_page)
- Slug change tracking with auto-redirect creation (after_edit_page)
- Tenant-scoped admin filtering (construct_explorer_page_queryset, etc.)
- Admin branding
"""

import logging

from django.contrib import messages
from django.shortcuts import redirect
from wagtail import hooks

from cms_core.models import ReservedSlug
from cms_core.validators import validate_page_for_publish

logger = logging.getLogger(__name__)


# ===========================================================================
# PRE-PUBLISH VALIDATION
# ===========================================================================

@hooks.register("before_publish_page")
def run_pre_publish_validators(request, page):
    """Run the three-tier validation before any page is published.

    Blockers prevent publish and redirect back with error messages.
    Warnings and suggestions are displayed but don't prevent publish.
    """
    result = validate_page_for_publish(page)

    if not result.is_publishable:
        for blocker in result.blockers:
            messages.error(request, f"Cannot publish: {blocker['message']}")

        return redirect(
            page.get_edit_url() if hasattr(page, "get_edit_url") else "/"
        )

    for warning in result.warnings:
        messages.warning(request, f"Publishing note: {warning['message']}")
        logger.info("Publish warning on page %s: %s", page.id, warning["message"])

    for suggestion in result.suggestions:
        logger.debug("Publish suggestion on page %s: %s", page.id, suggestion["message"])


@hooks.register("before_publish_page")
def enforce_reserved_slugs(request, page):
    """Prevent publishing a page whose slug collides with frontend-owned paths."""
    site = page.get_site()
    if site is None:
        return

    if ReservedSlug.objects.filter(site=site, slug=page.slug).exists():
        messages.error(
            request,
            f"Cannot publish: the slug '{page.slug}' is reserved by the frontend. "
            f"Choose a different slug.",
        )
        return redirect(
            page.get_edit_url() if hasattr(page, "get_edit_url") else "/"
        )


# ===========================================================================
# POST-PUBLISH AUDIT
# ===========================================================================

@hooks.register("after_publish_page")
def schedule_post_publish_audit(request, page):
    """Queue a post-publish audit to run 2 hours after publication.

    The audit checks: SEO metadata, internal link health, schema readiness,
    author assignment, featured image, service route. Issues are logged
    and surfaced as FreshnessAlerts in the dashboard.
    """
    try:
        from cms_core.tasks import post_publish_audit

        # Schedule 2 hours from now
        post_publish_audit.apply_async(
            args=[page.pk],
            countdown=7200, # 2 hours
        )
        logger.info(
            "Post-publish audit scheduled for page '%s' (id=%s) in 2 hours",
            page.title,
            page.pk,
        )
    except Exception as exc:
        # Don't let task scheduling failures break publishing
        logger.warning("Failed to schedule post-publish audit: %s", exc)


# ===========================================================================
# SLUG CHANGE TRACKING
# ===========================================================================

@hooks.register("after_create_page")
def track_slug_on_create(request, page):
    """Log the initial slug for future redirect tracking."""
    logger.debug("Page created: %s with slug: %s", page.id, page.slug)


@hooks.register("after_edit_page")
def track_slug_changes(request, page):
    """Detect slug changes and record in SlugHistory for auto-redirects."""
    from django.contrib.contenttypes.models import ContentType

    from cms_core.models import SlugHistory

    try:
        revisions = page.revisions.order_by("-created_at")
        if revisions.count() < 2:
            return

        previous_revision = revisions[1]
        previous_content = previous_revision.content
        old_slug = previous_content.get("slug", "")

        if not old_slug or old_slug == page.slug:
            return

        site = page.get_site()
        if not site:
            return

        SlugHistory.objects.create(
            content_type=ContentType.objects.get_for_model(page),
            object_id=page.id,
            old_slug=old_slug,
            new_slug=page.slug,
            site=site,
        )
        logger.info("Slug changed for page %s: %s → %s", page.id, old_slug, page.slug)

        # Auto-create Wagtail redirect
        try:
            from wagtail.contrib.redirects.models import Redirect

            # Build the old path from the page's parent URL + old slug
            parent = page.get_parent()
            if parent:
                parent_url = parent.url or ""
                old_path = f"{parent_url}{old_slug}/"
            else:
                old_path = f"/{old_slug}/"

            Redirect.objects.get_or_create(
                old_path=old_path,
                site=site,
                defaults={
                    "redirect_page": page,
                    "is_permanent": True,
                },
            )
            logger.info("Auto-created 301 redirect: %s → page %s", old_path, page.pk)

        except ImportError:
            logger.warning(
                "wagtail.contrib.redirects not installed — "
                "slug change redirect not created"
            )

    except Exception as exc:
        logger.error("Error tracking slug change for page %s: %s", page.id, exc)


# ===========================================================================
# TENANT-SCOPED ADMIN
# ===========================================================================

@hooks.register("construct_explorer_page_queryset")
def scope_explorer_to_tenant(parent_page, pages, request):
    """
    In the page explorer, non-superusers only see pages within
    their permitted sites. This is belt-and-suspenders on top of
    Wagtail's GroupPagePermission — it filters the queryset directly.
    """
    user = request.user
    if user.is_superuser:
        return pages

    from cms_core.services.tenant_service import get_sites_for_user

    permitted_sites = get_sites_for_user(user)
    if not permitted_sites:
        return pages.none()

    from django.db.models import Q

    q = Q()
    for site in permitted_sites:
        q |= Q(path__startswith=site.root_page.path)

    return pages.filter(q)


@hooks.register("construct_page_chooser_queryset")
def scope_page_chooser_to_tenant(pages, request):
    """
    When an editor picks a page (e.g., for an InternalLinkCardBlock),
    only show pages from their permitted tenants.
    """
    user = request.user
    if user.is_superuser:
        return pages

    from cms_core.services.tenant_service import get_sites_for_user

    permitted_sites = get_sites_for_user(user)
    if not permitted_sites:
        return pages.none()

    from django.db.models import Q

    q = Q()
    for site in permitted_sites:
        q |= Q(path__startswith=site.root_page.path)

    return pages.filter(q)


# ===========================================================================
# ADMIN BRANDING
# ===========================================================================

@hooks.register("construct_main_menu")
def customize_main_menu(request, menu_items):
    """Reorder or hide menu items for non-superusers."""
    # Future: hide settings, reports, etc. from writers
    pass


@hooks.register("insert_global_admin_css")
def global_admin_css():
    """Add custom CSS to the Wagtail admin."""
    return '<link rel="stylesheet" href="/static/cms_core/css/admin.css">'


# ===========================================================================
# CUSTOM INLINE RICH-TEXT STYLES
# Adds font-weight and colour toolbar buttons to the Draftail editor.
# Each style wraps selected text in a <span class="..."> in the stored HTML.
# The frontend renders these via CSS in each site's prose context.
# ===========================================================================

_INLINE_STYLES = [
    {
        "feature":     "inline-semibold",
        "type":        "INLINE_SEMIBOLD",
        "label":       "𝗦",
        "description": "Semibold — slightly heavier than normal, softer than bold",
        "editor_style": {"fontWeight": "600"},
        "css_class":   "inline-semibold",
    },
    {
        "feature":     "inline-brand",
        "type":        "INLINE_BRAND",
        "label":       "●",
        "description": "Brand colour — highlight key terms in the site accent colour",
        "editor_style": {"color": "#16a34a", "fontWeight": "500"},
        "css_class":   "inline-brand",
    },
    {
        "feature":     "inline-muted",
        "type":        "INLINE_MUTED",
        "label":       "—",
        "description": "Muted — secondary / parenthetical text, lower visual weight",
        "editor_style": {"color": "#94a3b8"},
        "css_class":   "inline-muted",
    },
    {
        "feature":     "inline-highlight",
        "type":        "INLINE_HIGHLIGHT",
        "label":       "◩",
        "description": "Highlight — yellow marker for very important terms",
        "editor_style": {"backgroundColor": "#fef9c3", "borderRadius": "2px", "padding": "0 2px"},
        "css_class":   "inline-highlight",
    },
]


@hooks.register("register_rich_text_features")
def register_custom_inline_styles(features):
    from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
    from wagtail.admin.rich_text.editors.draftail.features import InlineStyleFeature

    for s in _INLINE_STYLES:
        features.register_editor_plugin(
            "draftail",
            s["feature"],
            InlineStyleFeature({
                "type":        s["type"],
                "label":       s["label"],
                "description": s["description"],
                "style":       s["editor_style"],
            }),
        )
        features.register_converter_rule(
            "contentstate",
            s["feature"],
            {
                "from_database_format": {
                    f'span[class="{s["css_class"]}"]': InlineStyleElementHandler(s["type"]),
                },
                "to_database_format": {
                    "style_map": {
                        s["type"]: {
                            "element": "span",
                            "props":   {"class": s["css_class"]},
                        },
                    },
                },
            },
        )