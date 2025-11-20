from .models import Website


def get_primary_website():
    return Website.objects.filter(is_active=True, is_deleted=False).order_by("id").first()

def get_current_website(request):
    """
    Determines the current website based on the request.
    Priority:   1. request.website (set by middleware)
                2. request.user's website (if authenticated)
                3. domain from request host
                4. primary website as fallback
    """
    if hasattr(request, "website") and request.website:
        return request.website

    if request.user.is_authenticated:
        return getattr(request.user, "website", None)

    host = request.get_host().split(":")[0]
    site = Website.objects.filter(domain__iexact=host, is_active=True, is_deleted=False).first()
    if not site:
        site = get_primary_website()
    return site

def get_primary_domain():
    """
    Returns the primary domain for the website.
    Falls back to localhost if not set.
    """
    site = get_primary_website()
    return site.domain if site else "http://localhost:8000"

def get_email_sender_details(purpose="default"):
    site = get_primary_website()
    if not site:
        return "Gradecrest", "no-reply@localhost"

    name = site.default_sender_name or site.name or "Gradecrest"

    email_map = {
        "marketing": site.marketing_sender_email,
        "support": site.support_sender_email,
        "admin": site.admin_sender_email,
        "notification": site.notification_sender_email,
        "default": site.default_sender_email,
    }

    email = email_map.get(purpose, site.default_sender_email) or "no-reply@localhost"

    return name, email