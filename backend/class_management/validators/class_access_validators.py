from __future__ import annotations

from class_management.exceptions import ClassAccessDeniedError


class ClassAccessValidator:
    @staticmethod
    def require_can_view(*, can_view: bool) -> None:
        if not can_view:
            raise ClassAccessDeniedError(
                "You do not have permission to view class access details."
            )

    @staticmethod
    def require_access_detail_exists(*, access_detail) -> None:
        if access_detail is None:
            raise ClassAccessDeniedError(
                "This class order has no access details."
            )