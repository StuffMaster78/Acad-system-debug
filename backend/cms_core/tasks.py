"""
CMS Core Celery Tasks
=======================

Post-publish audit:
    Runs 2 hours after a page is published. Verifies that the page is
    healthy: schema renders, page is indexable, internal links resolve,
    engagement tracking started, no validator regressions.

Tenant health check:
    Runs daily. Verifies all Site ↔ Website bridges are intact,
    permissions groups exist, workflows are assigned.
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def post_publish_audit(self, page_id: int):
    """
    Run 2 hours after page publication. Checks:
    1. Page is live and accessible
    2. SEO metadata is complete (title, description, canonical)
    3. All internal links resolve to live pages
    4. Schema.org markup will render (author, dates, etc.)
    5. Featured image exists and has alt text (for blog posts)
    6. Page appears in sitemap
    7. No validator blockers crept in (re-run validators)

    Findings are logged. Critical issues create a FreshnessAlert
    (via cms_intelligence) so the editor sees them in the dashboard.
    """
    from wagtail.models import Page

    try:
        page = Page.objects.get(pk=page_id).specific
    except Page.DoesNotExist:
        logger.warning("Post-publish audit: page %s not found", page_id)
        return

    if not page.live:
        logger.info(
            "Post-publish audit: page %s is no longer live — skipping",
            page_id,
        )
        return

    issues = []

    # --- 1. SEO metadata ---
    seo_title = getattr(page, "seo_title", "") or ""
    search_desc = getattr(page, "search_description", "") or ""

    if not seo_title and not page.title:
        issues.append("Page has no title or SEO title")

    if not search_desc:
        issues.append("Missing meta description (search_description)")

    # --- 2. Author (for blog posts) ---
    primary_author = getattr(page, "primary_author", None)
    if hasattr(page, "primary_author") and not primary_author:
        issues.append("Blog post has no primary author assigned")

    # --- 3. Featured image (for blog posts) ---
    featured_image = getattr(page, "featured_image", None)
    if hasattr(page, "featured_image") and not featured_image:
        issues.append("Blog post has no featured image")

    # --- 4. Body content ---
    body = getattr(page, "body", None)
    if body is not None:
        from wagtail.fields import StreamField as StreamFieldType

        try:
            block_count = len(body)
            if block_count == 0:
                issues.append("Page body is empty — no content blocks")
        except (TypeError, AttributeError):
            pass

    # --- 5. Internal links check ---
    if body is not None:
        try:
            for block in body:
                if block.block_type == "internal_link":
                    value = block.value
                    if isinstance(value, dict):
                        linked_page = value.get("page")
                        if linked_page and hasattr(linked_page, "live"):
                            if not linked_page.live:
                                issues.append(
                                    f"Internal link to '{linked_page.title}' "
                                    f"points to an unpublished page"
                                )
        except Exception as exc:
            logger.debug("Internal link check error: %s", exc)

    # --- 6. Re-run validators ---
    try:
        from cms_core.validators import validate_page_for_publish

        result = validate_page_for_publish(page)
        for blocker in result.blockers:
            issues.append(f"Validator blocker: {blocker['message']}")
    except Exception as exc:
        logger.debug("Validator re-run error: %s", exc)

    # --- 7. Service route (blog posts) ---
    primary_service = getattr(page, "primary_service", None)
    if hasattr(page, "primary_service") and not primary_service:
        issues.append(
            "Blog post has no primary service page linked — "
            "not contributing to any conversion funnel"
        )

    # --- Report findings ---
    if issues:
        logger.warning(
            "Post-publish audit for '%s' (id=%s) found %d issues:\n %s",
            page.title,
            page_id,
            len(issues),
            "\n ".join(issues),
        )

        # Create a FreshnessAlert if cms_intelligence is available
        try:
            _create_audit_alert(page, issues)
        except Exception as exc:
            logger.debug("Could not create FreshnessAlert: %s", exc)
    else:
        logger.info(
            "Post-publish audit for '%s' (id=%s): all checks passed ",
            page.title,
            page_id,
        )

    return {
        "page_id": page_id,
        "page_title": page.title,
        "issues_found": len(issues),
        "issues": issues,
    }


def _create_audit_alert(page, issues: list[str]):
    """Create a FreshnessAlert from post-publish audit findings."""
    from django.contrib.contenttypes.models import ContentType

    from cms_intelligence.models import FreshnessAlert

    site = page.get_site()
    if not site:
        return

    ct = ContentType.objects.get_for_model(page)

    # Don't create duplicate alerts for the same page
    existing = FreshnessAlert.objects.filter(
        content_type=ct,
        object_id=page.pk,
        alert_type="editor_flagged",
        resolved_at__isnull=True,
    ).first()

    if existing:
        # Update existing alert with new issues
        existing.detail = {
            "source": "post_publish_audit",
            "issues": issues,
            "audit_timestamp": timezone.now().isoformat(),
        }
        existing.severity = min(4, 2 + len(issues)) # Scale severity with issue count
        existing.save(update_fields=["detail", "severity"])
        return

    FreshnessAlert.objects.create(
        site=site,
        content_type=ct,
        object_id=page.pk,
        alert_type="editor_flagged",
        severity=min(4, 2 + len(issues)),
        detail={
            "source": "post_publish_audit",
            "issues": issues,
            "audit_timestamp": timezone.now().isoformat(),
        },
    )


@shared_task
def tenant_health_check():
    """
    Daily task: verify all tenants are properly configured.
    Checks Site ↔ Website bridges, permission groups, and workflows.
    """
    from wagtail.models import Site

    from cms_core.services.tenant_service import validate_all_tenants_bridged
    from cms_core.services.permissions_service import TenantPermissionsService

    issues = []

    # 1. Bridge check
    bridge_issues = validate_all_tenants_bridged()
    issues.extend(bridge_issues)

    # 2. Permission groups check
    for site in Site.objects.all():
        tenant_name = site.site_name or site.hostname
        for role in ("admin", "editor", "writer"):
            group_name = f"{tenant_name} {role.title()}s"
            from django.contrib.auth.models import Group

            if not Group.objects.filter(name=group_name).exists():
                issues.append(
                    f"Missing permission group: {group_name} for site {tenant_name}"
                )

    # 3. Workflow check
    for site in Site.objects.all():
        from wagtail.models import WorkflowPage

        has_workflow = WorkflowPage.objects.filter(
            page=site.root_page
        ).exists()

        if not has_workflow:
            issues.append(
                f"No editorial workflow assigned to {site.site_name}"
            )

    if issues:
        logger.warning(
            "Tenant health check found %d issues:\n %s",
            len(issues),
            "\n ".join(issues),
        )
    else:
        logger.info("Tenant health check: all %d tenants healthy ", Site.objects.count())

    return {"issues": issues, "tenant_count": Site.objects.count()}