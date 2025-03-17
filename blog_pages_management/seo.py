from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.cache import cache
from django.utils.timezone import now
from .models import Website, BlogPost
from django.core.paginator import Paginator

def robots_txt(request):
    """Dynamically generates robots.txt and caches it for 24 hours."""
    domain = request.get_host()
    cache_key = f"robots_txt_{domain}"
    cached_robots = cache.get(cache_key)

    if cached_robots:
        return HttpResponse(cached_robots, content_type="text/plain")

    website = Website.objects.filter(domain=domain).first()

    if not website:
        robots_content = "User-agent: *\nDisallow: /"
    else:
        robots_content = f"""
        User-agent: Googlebot
        Disallow: /admin/
        Disallow: /api/
        Allow: /blog/
        
        User-agent: Bingbot
        Disallow: /admin/
        Allow: /blog/
        
        User-agent: *
        Disallow: /admin/
        Disallow: /api/
        Allow: /blog/
        
        Sitemap: https://{domain}/sitemap.xml
        """.strip()

    cache.set(cache_key, robots_content, timeout=86400)  # Cache for 1 day
    return HttpResponse(robots_content, content_type="text/plain")


def blog_sitemap(request, website_id, page=1):
    """
    Generates a dynamic paginated sitemap for a website.
    """
    cache_key = f"sitemap_{website_id}_page_{page}"
    cached_sitemap = cache.get(cache_key)

    if cached_sitemap:
        return HttpResponse(cached_sitemap, content_type="application/xml")

    blogs = BlogPost.objects.filter(
        website_id=website_id, is_published=True
    ).only("slug", "updated_at")  # Optimize query performance

    paginator = Paginator(blogs, 50000)  # Google’s 50k URL limit per sitemap
    total_pages = paginator.num_pages

    try:
        paginated_blogs = paginator.page(page)
    except:
        return HttpResponse("Invalid Page", status=404)

    sitemap_content = render_to_string(
        "sitemap.xml", {"blogs": paginated_blogs, "website_id": website_id, "total_pages": total_pages}
    )

    cache.set(cache_key, sitemap_content, timeout=86400)  # Cache for 1 day
    return HttpResponse(sitemap_content, content_type="application/xml")


def sitemap_index(request):
    """
    Generates a dynamic sitemap index for multiple websites.
    """
    cache_key = "sitemap_index"
    cached_sitemap_index = cache.get(cache_key)

    if cached_sitemap_index:
        return HttpResponse(cached_sitemap_index, content_type="application/xml")

    websites = Website.objects.prefetch_related("blogs").all()
    
    for website in websites:
        latest_blog = BlogPost.objects.filter(website=website, is_published=True).order_by("-updated_at").first()
        website.last_updated = latest_blog.updated_at if latest_blog else now()

    sitemap_index_content = render_to_string("sitemap_index.xml", {"websites": websites})

    cache.set(cache_key, sitemap_index_content, timeout=86400)  # Cache for 1 day
    return HttpResponse(sitemap_index_content, content_type="application/xml")