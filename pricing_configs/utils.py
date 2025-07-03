# utils.py
from websites.models import Website
from rest_framework.exceptions import ValidationError
from .utils import get_website_from_request

def get_website_from_request(request):
    if request.user.is_authenticated:
        return getattr(request.user, "website", None)

    host = request.get_host().split(":")[0]
    return Website.objects.filter(domain__iexact=host).first()