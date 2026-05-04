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
        """
        view = cast(Any, self)
        return getattr(view.request, "website")

    def get_class_order(self) -> ClassOrder:
        """
        Return class order scoped to the current website.
        """
        view = cast(Any, self)
        class_order_pk = view.kwargs.get("class_order_pk")
        pk = view.kwargs.get("pk")

        lookup_pk = class_order_pk or pk

        class_order = ClassOrder.objects.filter(
            website=self.get_website(),
            pk=lookup_pk,
        ).first()

        if class_order is None:
            raise NotFound("Class order not found.")

        return class_order