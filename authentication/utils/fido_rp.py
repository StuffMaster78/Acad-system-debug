from django.shortcuts import get_object_or_404
from websites.models import Website
from fido2.server import Fido2Server # type: ignore
from fido2.webauthn import PublicKeyCredentialRpEntity # type: ignore
from django.conf import settings

def get_rp_info(request) -> dict:
    """
    Retrieve relying party (RP) info from the domain in the request.

    Returns:
        dict: {
            "id": domain,
            "name": site name
        }
    """
    domain = request.get_host().split(":")[0]
    site = get_object_or_404(Website, domain=domain)

    return {
        "id": site.domain,
        "name": site.name,
    }

# FIDO2 Server setup
def get_fido_server(request):
    """
    Create and return a FIDO2 server instance for the given request.
    """
    rp_info = get_rp_info(request)
    rp = PublicKeyCredentialRpEntity(
        rp_info["id"],  # RP ID is the domain
        rp_info["name"],  # RP name is the site name
    )

    return Fido2Server(rp)

# Initialize FIDO2 server based on the current request
fido_server = get_fido_server