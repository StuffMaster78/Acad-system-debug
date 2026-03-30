from __future__ import annotations

from typing import Any, Mapping, cast

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from users.api.serializers.profile_update import (
    ProfileUpdateRequestSerializer,
    SubmitProfileUpdateRequestSerializer,
)
from users.selectors.profile_update_selector import (
    get_profile_update_request_by_id,
    list_profile_update_requests_for_user,
)
from users.services.profile_update_service import ProfileUpdateService


class ProfileUpdateRequestViewSet(viewsets.ViewSet):
    """
    Handles profile update request lifecycle.
    """

    permission_classes = [permissions.IsAuthenticated]

    def _require_pk(self, pk: str | None) -> int:
        """
        Return pk as an integer or raise a clear error.
        """
        if pk is None:
            raise ValueError("Request id is required.")
        return int(pk)

    def _request_data(self, request: Request) -> Mapping[str, Any]:
        """
        Return request data as a mapping for safer static typing.
        """
        return cast(Mapping[str, Any], request.data)

    def list(self, request: Request) -> Response:
        """
        List the current user's profile update requests.
        """
        qs = list_profile_update_requests_for_user(request.user.id)
        serializer = ProfileUpdateRequestSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request: Request) -> Response:
        """
        Submit a new profile update request.
        """
        serializer = SubmitProfileUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        requested_changes_raw = validated_data.get("requested_changes", {})
        requested_changes = cast(dict[str, Any], requested_changes_raw)

        submitted_note_raw = validated_data.get("submitted_note", "")
        submitted_note = cast(str, submitted_note_raw)

        request_obj = ProfileUpdateService.submit_request(
            user=request.user,
            requested_changes=requested_changes,
            submitted_note=submitted_note,
        )

        response_serializer = ProfileUpdateRequestSerializer(request_obj)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request: Request, pk: str | None = None) -> Response:
        """
        Approve a profile update request.
        """
        obj = get_profile_update_request_by_id(self._require_pk(pk))

        obj = ProfileUpdateService.approve(
            request_obj=obj,
            reviewer=request.user,
        )

        serializer = ProfileUpdateRequestSerializer(obj)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request: Request, pk: str | None = None) -> Response:
        """
        Reject a profile update request.
        """
        obj = get_profile_update_request_by_id(self._require_pk(pk))

        data = self._request_data(request)
        review_note_raw = data.get("review_note", "")
        review_note = cast(str, review_note_raw)

        obj = ProfileUpdateService.reject(
            request_obj=obj,
            reviewer=request.user,
            review_note=review_note,
        )

        serializer = ProfileUpdateRequestSerializer(obj)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def apply(self, request: Request, pk: str | None = None) -> Response:
        """
        Apply an approved profile update request.
        """
        obj = get_profile_update_request_by_id(self._require_pk(pk))

        obj = ProfileUpdateService.apply_approved_request(
            request_obj=obj,
        )

        serializer = ProfileUpdateRequestSerializer(obj)
        return Response(serializer.data)