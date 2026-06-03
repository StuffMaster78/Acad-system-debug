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
# Standard crawlers
User-agent: *
Allow: /
Disallow: /api/
Disallow: /cms-admin/
Disallow: /admin/
Disallow: /client/
Disallow: /writer/
Disallow: /auth/
Disallow: /search/

# ── AI / LLM crawlers — explicitly allowed on public content ─────────────────
# These crawlers power Perplexity, ChatGPT, Claude, Gemini answer engines.
# Allowing them on public content improves GEO (Generative Engine Optimisation)
# discoverability — your content can be cited as a source in AI answers.

User-agent: GPTBot
Allow: /blog/
Allow: /services/
Allow: /authors/
Allow: /resources/
Allow: /help/
Disallow: /api/
Disallow: /cms-admin/
Disallow: /client/
Disallow: /writer/
Disallow: /auth/

User-agent: PerplexityBot
Allow: /blog/
Allow: /services/
Allow: /authors/
Allow: /resources/
Allow: /help/
Disallow: /api/
Disallow: /cms-admin/
Disallow: /client/
Disallow: /writer/
Disallow: /auth/

User-agent: anthropic-ai
Allow: /blog/
Allow: /services/
Allow: /authors/
Allow: /resources/
Allow: /help/
Disallow: /api/
Disallow: /cms-admin/
Disallow: /client/
Disallow: /writer/
Disallow: /auth/

User-agent: ClaudeBot
Allow: /blog/
Allow: /services/
Allow: /authors/
Allow: /resources/
Allow: /help/
Disallow: /api/
Disallow: /cms-admin/
Disallow: /client/
Disallow: /writer/
Disallow: /auth/

User-agent: Google-Extended
Allow: /blog/
Allow: /services/
Allow: /authors/
Allow: /resources/
Allow: /help/
Disallow: /api/
Disallow: /cms-admin/
Disallow: /client/
Disallow: /writer/
Disallow: /auth/

User-agent: Bytespider
Disallow: /

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
