"""
Tenant Resolution Middleware
==============================

Sets ``request.site`` (Wagtail Site) and ``request.website`` (your
Website model) on every incoming request.  Downstream code can rely on
both being present without performing lookups.

Add to MIDDLEWARE after Wagtail's own ``SiteMiddleware`` (or as a
replacement if you prefer a single middleware):

    MIDDLEWARE = [
        ...
        # 'wagtail.contrib.legacy.sitemiddleware.SiteMiddleware',  # optional
        'cms_core.middleware.TenantMiddleware',
        ...
    ]
"""

from __future__ import annotations

import logging
from typing import Callable

from django.http import HttpRequest, HttpResponse

from cms_core.services.tenant_service import get_current_site, get_website_for_site

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """
    Resolve Site + Website for every request.

    After this middleware:
        request.site     -> wagtailcore.Site instance (or None)
        request.website  -> websites.Website instance (or None)
        request.tenant   -> dict with both for convenience
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Resolve Wagtail Site
        site = get_current_site(request)
        request.site = site

        # Resolve Website via the bridge
        website = None
        if site is not None:
            try:
                website = get_website_for_site(site)
            except Exception:
                logger.debug(
                    "Could not resolve Website for Site '%s' — "
                    "bridge may not be configured yet.",
                    site.site_name if site else "None",
                )

        request.website = website
        request.tenant = {"site": site, "website": website}

        return self.get_response(request)