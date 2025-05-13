from websites.models import Website
from django.http import HttpRequest


def get_fido2_rp_config(request: HttpRequest) -> dict:
    """
    Returns tenant-specific FIDO2 RP config using the Website model.
    """
    host = request.get_host().split(":")[0]
    
    try:
        website = Website.objects.get(domain=host)
        return {
            "id": website.domain,  # rp_id: domain
            "name": website.display_name or website.name,  # rp_name
        }
    except Website.DoesNotExist:
        return {
            "id": "default.com",
            "name": "Default RP",
        }
