from .models import Website


def get_primary_website():
    return Website.objects.filter(is_active=True, is_deleted=False).order_by("id").first()

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
        "notification": site.notification_sender_email,
        "default": site.default_sender_email,
    }

    email = email_map.get(purpose, site.default_sender_email) or "no-reply@localhost"

    return name, email