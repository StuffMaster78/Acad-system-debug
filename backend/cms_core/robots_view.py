"""
Per-tenant robots.txt view.

Serves a robots.txt that:
  - References the tenant's sitemap URL
  - Allows public content paths
  - Blocks all internal/API/admin paths from crawlers
"""
from __future__ import annotations

from django.http import HttpResponse


_ROBOTS_TEMPLATE = """\
User-agent: *
Allow: /
Disallow: /api/
Disallow: /cms-admin/
Disallow: /admin/
Disallow: /client/
Disallow: /writer/
Disallow: /auth/
Disallow: /search/

Sitemap: {sitemap_url}
"""

_STAFF_ROBOTS = """\
User-agent: *
Disallow: /
"""


def robots_txt(request):
    """
    Serve /robots.txt scoped to the current portal surface.

    - Client domains: allow public content, block internal paths, include sitemap.
    - Writer / staff domains: disallow all (no public content).
    """
    surface = "client"
    portal = getattr(request, "portal", None)
    if portal:
        code = portal.code
        if code in ("internal_admin", "writer_portal"):
            surface = "staff"

    if surface == "staff":
        return HttpResponse(_STAFF_ROBOTS, content_type="text/plain")

    scheme = "https" if request.is_secure() else "http"
    host = request.get_host()
    sitemap_url = f"{scheme}://{host}/sitemap.xml"

    body = _ROBOTS_TEMPLATE.format(sitemap_url=sitemap_url)
    return HttpResponse(body, content_type="text/plain")
