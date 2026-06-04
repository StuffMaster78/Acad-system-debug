"""
Wagtail hooks for cms_service_pages.

Registers ServiceCategory snippet with tenant scoping
and service page publishing enhancements.
"""

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet
from wagtail import hooks

from cms_core.models import ServiceCategory
from cms_core.services.tenant_service import filter_queryset_by_user_sites


class ServiceCategorySnippetViewSet(SnippetViewSet):
    """Tenant-scoped service category admin."""

    model = ServiceCategory
    icon = "folder-open-inverse"
    menu_label = "Service Categories"
    menu_name = "service-categories"
    menu_order = 250
    add_to_admin_menu = True
    list_display = ["name", "slug", "site", "display_order"]
    list_filter = ["site"]
    search_fields = ["name", "description"]

    def get_queryset(self, request=None):
        qs = super().get_queryset()
        req = request or getattr(self, "request", None)
        user = getattr(req, "user", None)
        if user and user.is_authenticated:
            return filter_queryset_by_user_sites(qs, user)
        return qs


# Re-register with custom viewset
try:
    from wagtail.snippets.models import SNIPPET_MODELS

    if ServiceCategory in SNIPPET_MODELS:
        SNIPPET_MODELS.remove(ServiceCategory)
except Exception:
    pass

register_snippet(ServiceCategorySnippetViewSet)


@hooks.register("after_publish_page")
def update_service_substantive_timestamp(request, page):
    """Auto-set last_substantive_update on first publish of service pages."""
    from cms_service_pages.models import ServicePage

    if not isinstance(page.specific, ServicePage):
        return

    service_page = page.specific
    if service_page.last_substantive_update is None:
        from django.utils import timezone

        service_page.last_substantive_update = timezone.now()
        service_page.save(update_fields=["last_substantive_update"])