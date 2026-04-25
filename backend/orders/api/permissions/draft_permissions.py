from typing import Any

from rest_framework.permissions import BasePermission

from rest_framework.request import Request
from rest_framework.views import APIView

class CanSubmitDraft(BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj) -> Any:
        user = request.user

        if not user.is_authenticated:
            return False

        if getattr(user, "is_staff", False):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments:
            assignment = assignments.filter(is_current=True).first()
            if assignment:
                return assignment.writer == user

        return getattr(obj, "preferred_writer", None) == user


class CanReviewDraft(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> Any:
        return bool(request.user and request.user.is_staff)