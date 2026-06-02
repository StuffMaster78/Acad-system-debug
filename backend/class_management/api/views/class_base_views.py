from __future__ import annotations

from typing import Any, cast

from rest_framework.exceptions import NotFound

from class_management.models.class_order import ClassOrder


class ClassTenantViewMixin:
    """
    Shared helpers for tenant scoped class views.
    """

    def get_website(self):
        """
        Return middleware injected website safely.
        Superadmins return None to signal cross-website access.
        """
        view = cast(Any, self)
        user = getattr(view.request, "user", None)
        if user and (user.is_superuser or getattr(user, "role", None) == "superadmin"):
            return None
        return getattr(view.request, "website")

    def get_class_order(self) -> ClassOrder:
        """
        Return class order. Superadmins bypass website scoping.
        """
        view = cast(Any, self)
        class_order_pk = view.kwargs.get("class_order_pk")
        pk = view.kwargs.get("pk")
        lookup_pk = class_order_pk or pk

        website = self.get_website()
        qs = ClassOrder.objects.filter(pk=lookup_pk)
        if website is not None:
            qs = qs.filter(website=website)

        class_order = qs.first()
        if class_order is None:
            raise NotFound("Class order not found.")

        return class_order