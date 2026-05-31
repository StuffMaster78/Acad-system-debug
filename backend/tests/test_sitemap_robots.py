"""
Tests for per-tenant sitemap.xml and robots.txt endpoints.

Verifies:
  - /sitemap.xml returns 200 and XML content
  - /robots.txt for client domain allows crawling + references sitemap
  - /robots.txt for staff/writer portals disallows all
  - robots.txt sitemap URL matches the request host
  - Tenant isolation: sitemap only references current tenant's pages
"""
import pytest
from rest_framework import status

from tests.factories import WebsiteFactory


def make_seo_page(website, slug, published=True):
    from seo_pages.models import SeoPage
    return SeoPage.objects.create(
        website=website,
        title=f"Page {slug}",
        slug=slug,
        meta_title="",
        meta_description="",
        blocks=[],
        is_published=published,
        is_deleted=False,
    )


@pytest.mark.django_db
class TestRobotsTxt:

    def test_client_domain_allows_crawling(self, client, db):
        """Client domain robots.txt permits crawling public content."""
        response = client.get("/robots.txt", HTTP_HOST="testsite.com")
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text/plain"
        body = response.content.decode()
        assert "User-agent: *" in body
        assert "Allow: /" in body

    def test_client_domain_blocks_internal_paths(self, client, db):
        """Client domain robots.txt blocks API, admin, auth, and portal paths."""
        response = client.get("/robots.txt", HTTP_HOST="testsite.com")
        body = response.content.decode()
        assert "Disallow: /api/" in body
        assert "Disallow: /cms-admin/" in body
        assert "Disallow: /client/" in body
        assert "Disallow: /auth/" in body

    def test_client_domain_includes_sitemap_url(self, client, db):
        """Client domain robots.txt references its own sitemap."""
        response = client.get("/robots.txt", HTTP_HOST="brand.example.com")
        body = response.content.decode()
        assert "Sitemap:" in body
        assert "brand.example.com/sitemap.xml" in body

    def test_staff_portal_disallows_all(self, db):
        """Staff portal robots.txt disallows all crawlers (no public content)."""
        from cms_core.robots_view import _STAFF_ROBOTS, robots_txt
        from unittest.mock import MagicMock

        portal = MagicMock()
        portal.code = "internal_admin"

        request = MagicMock()
        request.portal = portal
        request.website = None
        request.is_secure.return_value = False
        request.get_host.return_value = "staff.platform.com"

        response = robots_txt(request)
        body = response.content.decode()
        assert "Disallow: /" in body
        assert "Allow: /" not in body

    def test_writer_portal_disallows_all(self, db):
        """Writer portal robots.txt disallows all crawlers (no public content)."""
        from cms_core.robots_view import robots_txt
        from unittest.mock import MagicMock

        portal = MagicMock()
        portal.code = "writer_portal"

        request = MagicMock()
        request.portal = portal
        request.website = None
        request.is_secure.return_value = False
        request.get_host.return_value = "writers.platform.com"

        response = robots_txt(request)
        body = response.content.decode()
        assert "Disallow: /" in body
        assert "Allow: /" not in body


@pytest.mark.django_db
class TestSitemapXml:

    def test_sitemap_returns_200(self, client, db):
        """Sitemap endpoint returns 200 with XML content type."""
        response = client.get("/sitemap.xml", HTTP_HOST="testsite.com")
        # 200 (with content) or 200 (empty sitemap) are both acceptable.
        # 404 would mean the URL isn't wired.
        assert response.status_code == status.HTTP_200_OK

    def test_sitemap_is_xml(self, client, db):
        """Sitemap response has an XML content type."""
        response = client.get("/sitemap.xml", HTTP_HOST="testsite.com")
        assert "xml" in response["Content-Type"]

    def test_sitemap_seo_pages_are_tenant_scoped(self, db):
        """
        SEO page queryset inside SeoPageSitemap only returns the resolved
        website's pages — not another tenant's.
        """
        from cms_core.sitemaps import SeoPageSitemap

        site_a = WebsiteFactory(domain="sitemap-a.test", name="Sitemap A")
        site_b = WebsiteFactory(domain="sitemap-b.test", name="Sitemap B")

        page_a = make_seo_page(site_a, "page-a")
        page_b = make_seo_page(site_b, "page-b")

        sitemap_a = SeoPageSitemap(site_a)
        ids_a = list(sitemap_a.items().values_list("id", flat=True))

        assert page_a.id in ids_a
        assert page_b.id not in ids_a, "Sitemap must not expose another tenant's SEO pages"

    def test_sitemap_excludes_unpublished_seo_pages(self, db):
        """Unpublished SEO pages are not included in the sitemap."""
        from cms_core.sitemaps import SeoPageSitemap

        website = WebsiteFactory(domain="sitemap-draft.test", name="Draft Test")
        draft = make_seo_page(website, "my-draft", published=False)

        sitemap = SeoPageSitemap(website)
        ids = list(sitemap.items().values_list("id", flat=True))

        assert draft.id not in ids

    def test_sitemap_location_uses_slug(self, db):
        """SeoPageSitemap.location() returns /<slug>/ format."""
        from cms_core.sitemaps import SeoPageSitemap

        website = WebsiteFactory(domain="loc-test.test", name="Loc Test")
        page = make_seo_page(website, "nursing-essay-help")

        sitemap = SeoPageSitemap(website)
        location = sitemap.location(page)

        assert location == "/nursing-essay-help/"
