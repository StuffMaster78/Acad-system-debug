# core/tenant_context.py
import contextvars
from websites.models import Website
from celery import shared_task

_current_site = contextvars.ContextVar("current_site", default=None)
def set_current_website(site): _current_site.set(site)
def get_current_website(): return _current_site.get()

# middleware
class WebsiteMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        site = Website.resolve_from_request(request)  # your logic
        set_current_website(site)
        request.website = site
        return self.get_response(request)
    

# Celery task pattern
@shared_task
def send_invoice(order_id, website_id):
    set_current_website(Website.objects.get(pk=website_id))
    ...