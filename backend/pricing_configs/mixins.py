from rest_framework.exceptions import ValidationError
from .utils import get_website_from_request

class WebsiteScopedViewSetMixin:
    """
    Injects website into model instance on creation.
    Also optionally scopes queryset per website.
    """

    def get_website(self):
        website = get_website_from_request(self.request)
        if not website:
            raise ValidationError("Website could not be determined from request.")
        return website

    def perform_create(self, serializer):
        website = self.get_website()
        serializer.save(website=website)

    def get_queryset(self):
        """
        Optionally restrict the queryset by website
        """
        base_qs = super().get_queryset()
        website = self.get_website()
        return base_qs.filter(website=website)
