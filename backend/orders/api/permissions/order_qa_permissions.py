from __future__ import annotations

from typing import Any
from rest_framework.permissions import BasePermission

from rest_framework.request import Request
from rest_framework.views import APIView

class CanSubmitOrderForQA(BasePermission):
    """
    Allow the assigned writer or staff to submit an order for QA.
    """

    message = "You are not allowed to submit this order for QA."

    def has_object_permission(self, request:Request, view: APIView, obj) -> Any:
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "is_staff", False):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments is not None:
            current_assignment = assignments.filter(is_current=True).first()
            if current_assignment is not None:
                return current_assignment.writer == user

        return getattr(obj, "preferred_writer", None) == user


class CanReviewOrderQA(BasePermission):
    """
    Allow staff or QA users to approve or return QA submissions.
    """

    message = "You are not allowed to review this order for QA."

    def has_object_permission(self, request: Request, view: APIView, obj) -> Any:
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return False

        return bool(getattr(user, "is_staff", False))