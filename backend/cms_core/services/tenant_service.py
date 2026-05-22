"""
Tenant Service — The Site ↔ Website Bridge
=============================================

THE single source of truth for resolving tenants.  Every app that needs
to know "which tenant am I working in?" calls these functions.  No app
should independently query Website or Site — use this bridge.

Two models represent a tenant:
    • ``wagtailcore.Site`` — Wagtail's concept.  Owns the page tree,
      handles URL routing, scopes admin permissions.
    • ``websites.Website`` — Your business model.  Owns branding,
      pricing, analytics IDs, and references from orders/writers/clients.

They are linked via ``Website.wagtail_site = OneToOneField(Site)``.

This service ensures you never have two diverging tenant lookups.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

if TYPE_CHECKING:
    from wagtail.models import Site

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------
# Core resolvers
# -----------------------------------------------------------------------

def get_website_for_site(site: Site):
    """
    Given a Wagtail Site, return the linked Website.
    Raises DoesNotExist if the bridge is broken.
    """
    try:
        return site.website_config  # reverse of Website.wagtail_site
    except Exception:
        # Try forward lookup if the related_name differs in your codebase
        from django.apps import apps

        Website = apps.get_model("websites", "Website")
        try:
            return Website.objects.get(wagtail_site=site)
        except Website.DoesNotExist:
            logger.error(
                "No Website linked to Wagtail Site '%s' (id=%s).  "
                "Run `python manage.py setup_tenants` to fix.",
                site.site_name,
                site.pk,
            )
            raise


def get_site_for_website(website) -> Site:
    """
    Given a Website, return the linked Wagtail Site.
    Raises ValueError if the bridge is broken.
    """
    site = getattr(website, "wagtail_site", None)
    if site is None:
        from wagtail.models import Site

        try:
            # Fallback: match by domain/hostname
            domain = getattr(website, "domain", "") or ""
            hostname = domain.split("//")[-1].split("/")[0].split(":")[0]
            site = Site.objects.get(hostname=hostname)
        except Site.DoesNotExist:
            raise ValueError(
                f"No Wagtail Site linked to Website '{website}' (id={website.pk}).  "
                f"Run `python manage.py setup_tenants` to fix."
            )
    return site


# -----------------------------------------------------------------------
# Request-based resolution (used by middleware and views)
# -----------------------------------------------------------------------

def get_current_site(request: HttpRequest) -> Site:
    """
    Return the Wagtail Site for the current request.
    Wagtail normally attaches this via its own middleware, but this
    function works even if Wagtail's middleware hasn't run yet.
    """
    from wagtail.models import Site

    # Wagtail's middleware sets request.site (if SiteMiddleware is active)
    site = getattr(request, "site", None)
    if site is not None:
        return site

    # Fallback: resolve from hostname
    site = Site.find_for_request(request)
    if site is not None:
        return site

    # Last resort: default site
    return Site.objects.filter(is_default_site=True).first()


def get_current_website(request: HttpRequest):
    """
    Return the Website for the current request.
    This is the function most views and viewsets should call.
    """
    site = get_current_site(request)
    if site is None:
        return None
    try:
        return get_website_for_site(site)
    except Exception:
        return None


def get_current_tenant(request: HttpRequest) -> dict:
    """
    Return both Site and Website in one call.  Useful when you need
    both (e.g., to pass ``site`` to a Wagtail queryset AND ``website``
    to a business-domain queryset).
    """
    site = get_current_site(request)
    website = None
    if site:
        try:
            website = get_website_for_site(site)
        except Exception:
            pass
    return {"site": site, "website": website}


# -----------------------------------------------------------------------
# Admin context helpers
# -----------------------------------------------------------------------

def get_sites_for_user(user) -> list:
    """
    Return the list of Wagtail Sites a user has page permissions on.
    Superusers get all sites.
    """
    from wagtail.models import Site

    if user.is_superuser:
        return list(Site.objects.all())

    # Get all page tree roots the user has any permission on
    from wagtail.models import GroupPagePermission

    permitted_page_ids = (
        GroupPagePermission.objects.filter(group__in=user.groups.all())
        .values_list("page_id", flat=True)
        .distinct()
    )

    # Find which Sites have root pages that are ancestors of (or equal to)
    # the permitted pages
    site_ids = set()
    for site in Site.objects.select_related("root_page").all():
        root_path = site.root_page.path
        # Check if any permitted page is under this site's root
        from wagtail.models import Page

        if Page.objects.filter(
            pk__in=permitted_page_ids,
            path__startswith=root_path,
        ).exists():
            site_ids.add(site.pk)

    return list(Site.objects.filter(pk__in=site_ids))


def get_websites_for_user(user) -> list:
    """
    Return the Websites a user has CMS access to.
    """
    sites = get_sites_for_user(user)
    websites = []
    for site in sites:
        try:
            websites.append(get_website_for_site(site))
        except Exception:
            pass
    return websites


# -----------------------------------------------------------------------
# Snippet queryset scoping (for SnippetViewSet overrides)
# -----------------------------------------------------------------------

def filter_queryset_by_user_sites(queryset, user, site_field="site"):
    """
    Filter any queryset that has a ``site`` FK to only show records
    belonging to sites the user has access to.

    Usage in a SnippetViewSet:

        def get_queryset(self):
            qs = super().get_queryset()
            return filter_queryset_by_user_sites(qs, self.request.user)
    """
    if user.is_superuser:
        return queryset

    sites = get_sites_for_user(user)
    return queryset.filter(**{f"{site_field}__in": sites})


# -----------------------------------------------------------------------
# Validation helpers
# -----------------------------------------------------------------------

def validate_all_tenants_bridged():
    """
    Check that every Website has a linked Wagtail Site and vice versa.
    Called by a management command or health check.
    Returns a list of issues.
    """
    from wagtail.models import Site
    from django.apps import apps

    issues = []

    Website = apps.get_model("websites", "Website")

    # Check: every active Website should have a Wagtail Site
    for website in Website.objects.filter(is_active=True):
        site = getattr(website, "wagtail_site", None)
        if site is None:
            issues.append(
                f"Website '{website}' (id={website.pk}) has no linked Wagtail Site"
            )

    # Check: every Wagtail Site should have a Website
    for site in Site.objects.all():
        try:
            get_website_for_site(site)
        except Exception:
            issues.append(
                f"Wagtail Site '{site.site_name}' (id={site.pk}) has no linked Website"
            )

    return issues