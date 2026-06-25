"""
Per-tenant sitemaps.

Each client domain resolves a Wagtail Site via PortalTenantResolverMiddleware.
These sitemap classes scope their querysets to that site/website so
/sitemap.xml always returns only the current tenant's live URLs.
"""
from __future__ import annotations

from django.contrib.sitemaps import Sitemap


class WagtailPageSitemap(Sitemap):
    """
    Live Wagtail pages (blog posts, service pages, public CMS pages)
    scoped to the Wagtail Site resolved from the request host.
    """

    changefreq = "weekly"
    priority = 0.7

    def __init__(self, site):
        self.site = site

    def items(self):
        from wagtail.models import Page

        if not self.site:
            return Page.objects.none()

        return (
            Page.objects.live()
            .in_site(self.site)
            .public()
            .order_by("-last_published_at")
        )

    def lastmod(self, page):
        return getattr(page, "last_published_at", None)

    def location(self, page):
        # Blog posts and service pages are served at flat /:slug URLs by Nuxt.
        specific = getattr(page, "specific", page)
        if hasattr(specific, "frontend_url"):
            # frontend_url returns the full URL; strip scheme+host for Django's sitemap loc.
            from urllib.parse import urlparse
            parsed = urlparse(specific.frontend_url)
            return parsed.path or f"/{specific.slug}"
        return page.url


class SeoPageSitemap(Sitemap):
    """
    Published SEO pages scoped to the Website resolved from the request host.
    """

    changefreq = "monthly"
    priority = 0.6

    def __init__(self, website):
        self.website = website

    def items(self):
        from seo_pages.models import SeoPage

        if not self.website:
            return SeoPage.objects.none()

        return SeoPage.objects.filter(
            website=self.website,
            is_published=True,
            is_deleted=False,
        ).order_by("-updated_at")

    def lastmod(self, page):
        return getattr(page, "updated_at", None)

    def location(self, page):
        # SEO pages are served by their slug at the domain root
        return f"/{page.slug}/"


def sitemap_view(request):
    """
    Render /sitemap.xml scoped to the current tenant.

    Uses the Site and Website resolved by PortalTenantResolverMiddleware.
    Falls back to empty sitemaps for writer/staff portals (they have no
    public-facing content).
    """
    from django.contrib.sitemaps.views import sitemap

    site = getattr(request, "site", None)
    website = getattr(request, "website", None)

    sitemaps = {}
    if site:
        sitemaps["pages"] = WagtailPageSitemap(site)
    if website:
        sitemaps["seo"] = SeoPageSitemap(website)

    return sitemap(request, sitemaps=sitemaps)
