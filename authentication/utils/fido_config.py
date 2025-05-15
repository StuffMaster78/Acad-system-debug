# utils/fido_config.py

from fido2.server import Fido2Server  # type: ignore
from fido2.rp import RelyingParty  # type: ignore
from django.shortcuts import get_object_or_404
from websites.models import Website


def get_fido_server(request):
    """
    Dynamically create a Fido2Server based on the domain in the request.
    """
    host = request.get_host().split(":")[0]
    site = get_object_or_404(Website, domain=host)
    
    rp = RelyingParty(id=site.domain, name=site.name)
    return Fido2Server(rp)