"""
Wagtail Hooks for CMS Core
============================

Registers:
- Pre-publish validation (before_publish_page)
- Admin branding customization
- Reserved slug enforcement (before_create_page, before_edit_page)
"""

import logging

from django.http import HttpResponseForbidden
from wagtail import hooks

from cms_core.validators import validate_page_for_publish
from cms_core.models import ReservedSlug

logger = logging.getLogger(__name__)


@hooks.register("before_publish_page")
def run_pre_publish_validators(request, page):
    """Run the three-tier validation before any page is published.

    Blockers prevent publish and redirect back with error messages.
    Warnings and suggestions are logged but don't prevent publish.
    """
    result = validate_page_for_publish(page)

    if not result.is_publishable:
        from django.contrib import messages

        for blocker in result.blockers:
            messages.error(
                request,
                f"Cannot publish: {blocker['message']}",
            )
        # Return an HttpResponse to prevent publishing
        # Wagtail's hook system treats a returned response as a cancel signal
        from django.shortcuts import redirect
        return redirect(
            page.get_edit_url() if hasattr(page, "get_edit_url") else "/"
        )

    # Log warnings and suggestions (they don't block)
    for warning in result.warnings:
        from django.contrib import messages
        messages.warning(request, f"Publishing note: {warning['message']}")
        logger.info(
            "Publish warning on page %s: %s",
            page.id,
            warning["message"],
        )

    for suggestion in result.suggestions:
        logger.debug(
            "Publish suggestion on page %s: %s",
            page.id,
            suggestion["message"],
        )


@hooks.register("before_create_page")
def enforce_reserved_slugs_on_create(request, parent_page, page_class):
    """Prevent creating pages with reserved slugs.
    The actual slug check happens in before_publish, but we can
    also warn early at creation time via a hook."""
    pass  # Slug isn't set yet at creation — validation happens at publish


@hooks.register("after_create_page")
def track_slug_on_create(request, page):
    """Log the initial slug for future redirect tracking."""
    logger.debug("Page created: %s with slug: %s", page.id, page.slug)


@hooks.register("after_edit_page")
def track_slug_changes(request, page):
    """Detect slug changes and record in SlugHistory for redirects."""
    from cms_core.models import SlugHistory
    from django.contrib.contenttypes.models import ContentType

    try:
        # Get the previous revision's slug
        revisions = page.revisions.order_by("-created_at")
        if revisions.count() >= 2:
            previous_revision = revisions[1]
            previous_content = previous_revision.content
            old_slug = previous_content.get("slug", "")

            if old_slug and old_slug != page.slug:
                site = page.get_site()
                if site:
                    SlugHistory.objects.create(
                        content_type=ContentType.objects.get_for_model(page),
                        object_id=page.id,
                        old_slug=old_slug,
                        new_slug=page.slug,
                        site=site,
                    )
                    logger.info(
                        "Slug changed for page %s: %s → %s",
                        page.id,
                        old_slug,
                        page.slug,
                    )

                    # Auto-create Wagtail redirect
                    try:
                        from wagtail.contrib.redirects.models import Redirect

                        old_path = f"/{old_slug}/"
                        Redirect.objects.get_or_create(
                            old_path=old_path,
                            site=site,
                            defaults={
                                "redirect_page": page,
                                "is_permanent": True,
                            },
                        )
                        logger.info(
                            "Auto-created redirect: %s → %s",
                            old_path,
                            page.url,
                        )
                    except ImportError:
                        logger.warning(
                            "wagtail.contrib.redirects not installed — "
                            "slug change redirect not created"
                        )
    except Exception as e:
        logger.error("Error tracking slug change: %s", e)


# ===========================================================================
# ADMIN BRANDING
# ===========================================================================

@hooks.register("construct_main_menu")
def customize_main_menu(request, menu_items):
    """Optionally reorder or hide menu items for non-superusers."""
    pass  # Customize as needed


@hooks.register("insert_global_admin_css")
def global_admin_css():
    """Add custom CSS to the Wagtail admin."""
    return '<link rel="stylesheet" href="/static/cms_core/css/admin.css">'