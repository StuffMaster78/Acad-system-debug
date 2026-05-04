from __future__ import annotations

from typing import cast, Any

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from class_management.api.permissions import ClassAccessPermission
from class_management.api.serializers.class_access_serializers import (
    ClassAccessDetailReadSerializer,
    ClassAccessDetailWriteSerializer,
    ClassAccessGrantSerializer,
    ClassAccessLogSerializer,
    ClassTwoFactorRequestSerializer,
    GrantAccessSerializer,
    ReplaceTwoFactorWindowsSerializer,
    RequestTwoFactorSerializer,
    ResolveTwoFactorSerializer,
    RevokeAccessSerializer,
    ViewAccessSerializer,
)
from class_management.models.class_access import ClassTwoFactorRequest
from class_management.selectors.class_access_selectors import (
    ClassAccessSelector,
)
from class_management.selectors.class_order_selectors import (
    ClassOrderSelector,
)
from class_management.api.throttles import ClassAccessViewThrottle
from rest_framework.exceptions import ValidationError
from class_management.services.class_access_service import (
    ClassAccessService,
)
from class_management.selectors.class_order_accessor import (
    ClassOrderAccessor,
)


class ClassAccessViewSet(viewsets.GenericViewSet):
    """
    API endpoints for protected class access details.
    """

    permission_classes = [IsAuthenticated, ClassAccessPermission]
    throttle_classes = [ClassAccessViewThrottle]

    def get_website(self):
        """Returns the website """
        return getattr(cast(Any, self.request), "website")
    
    def get_access_detail(self, *, class_order):
        """
        Return class access detail or raise validation error.
        """
        access_detail = ClassOrderAccessor.access_detail(
            class_order=class_order,
        )

        if access_detail is None:
            raise ValidationError(
                "This class order has no access details."
            )

        return access_detail
    

    def get_class_order(self):
        class_order = ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )
        self.check_object_permissions(self.request, class_order)
        return class_order

    @action(detail=False, methods=["put", "patch"])
    def details(self, request, *args, **kwargs):
        """
        Create or update protected access details.
        """
        class_order = self.get_class_order()

        serializer = ClassAccessDetailWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        access_detail = ClassAccessService.create_or_update_access_detail(
            class_order=class_order,
            actor=request.user,
            institution_name=data.get("institution_name", ""),
            institution_state=data.get("institution_state", ""),
            class_portal_url=data.get("class_portal_url", ""),
            class_name=data.get("class_name", ""),
            class_code=data.get("class_code", ""),
            login_username=data.get("login_username", ""),
            login_password=data.get("login_password", ""),
            requires_two_factor=data.get("requires_two_factor", False),
            two_factor_method=data.get("two_factor_method", ""),
            preferred_contact_method=data.get(
                "preferred_contact_method",
                "",
            ),
            extra_login_notes=data.get("extra_login_notes", ""),
            emergency_contact_notes=data.get("emergency_contact_notes", ""),
        )

        return Response(
            {
                "id": access_detail.pk,
                "class_order": access_detail.class_order.id,
                "updated": True,
            }
        )

    @action(detail=False, methods=["post"])
    def view_details(self, request, *args, **kwargs):
        """
        View decrypted access details.

        This always creates an access log.
        """
        class_order = self.get_class_order()

        serializer = ViewAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        result = ClassAccessService.view_access_detail(
            class_order=class_order,
            viewer=request.user,
            reason=data.get("reason", ""),
            ip_address=self._get_ip_address(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        output = ClassAccessDetailReadSerializer(result)
        return Response(output.data)

    @action(detail=False, methods=["put"])
    def two_factor_windows(self, request, *args, **kwargs):
        """
        Replace 2FA availability windows.
        """
        class_order = self.get_class_order()

        serializer = ReplaceTwoFactorWindowsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        access_detail = self.get_access_detail(
            class_order=class_order,
        )

        windows = ClassAccessService.replace_two_factor_windows(
            access_detail=access_detail,
            windows=data["windows"],
            actor=request.user,
        )

        return Response(
            {
                "count": len(windows),
                "updated": True,
            }
        )

    @action(detail=False, methods=["get"])
    def grants(self, request, *args, **kwargs):
        """
        List active access grants.
        """
        class_order = self.get_class_order()
        grants = ClassAccessSelector.active_grants_for_order(
            class_order=class_order,
        )

        return Response(ClassAccessGrantSerializer(grants, many=True).data)

    @action(detail=False, methods=["post"])
    def grant(self, request, *args, **kwargs):
        """
        Grant protected access to a user.
        """
        class_order = self.get_class_order()

        serializer = GrantAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        UserModel = get_user_model()
        user = UserModel.objects.get(pk=data["user_id"])

        grant = ClassAccessService.grant_access(
            class_order=class_order,
            user=user,
            granted_by=request.user,
            reason=data.get("reason", ""),
            expires_at=data.get("expires_at"),
        )

        return Response(
            ClassAccessGrantSerializer(grant).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def revoke(self, request, *args, **kwargs):
        """
        Revoke protected access from a user.
        """
        class_order = self.get_class_order()

        serializer = RevokeAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        UserModel = get_user_model()
        user = UserModel.objects.get(pk=data["user_id"])

        ClassAccessService.revoke_access(
            class_order=class_order,
            user=user,
            revoked_by=request.user,
            reason=data.get("reason", ""),
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def logs(self, request, *args, **kwargs):
        """
        List access view logs.
        """
        class_order = self.get_class_order()
        logs = ClassAccessSelector.access_logs_for_order(
            class_order=class_order,
        )

        return Response(ClassAccessLogSerializer(logs, many=True).data)

    @action(detail=False, methods=["get"])
    def two_factor_requests(self, request, *args, **kwargs):
        """
        List 2FA requests.
        """
        class_order = self.get_class_order()
        requests_qs = ClassAccessSelector.two_factor_requests_for_order(
            class_order=class_order,
        )

        return Response(
            ClassTwoFactorRequestSerializer(requests_qs, many=True).data
        )

    @action(detail=False, methods=["post"])
    def request_two_factor(self, request, *args, **kwargs):
        """
        Request 2FA help from the client.
        """
        class_order = self.get_class_order()

        serializer = RequestTwoFactorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        two_factor_request = ClassAccessService.request_two_factor(
            class_order=class_order,
            requested_by=request.user,
            needed_by=data.get("needed_by"),
            request_notes=data.get("request_notes", ""),
        )

        return Response(
            ClassTwoFactorRequestSerializer(two_factor_request).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="two-factor-requests/(?P<request_id>[^/.]+)/sent",
    )
    def mark_two_factor_sent(self, request, request_id=None, *args, **kwargs):
        """
        Mark a 2FA request as sent.
        """
        class_order = self.get_class_order()

        two_factor_request = ClassTwoFactorRequest.objects.get(
            pk=request_id,
            class_order=class_order,
        )

        serializer = ResolveTwoFactorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        updated = ClassAccessService.mark_two_factor_sent(
            request=two_factor_request,
            actor=request.user,
            notes=data.get("notes", ""),
        )

        return Response(ClassTwoFactorRequestSerializer(updated).data)

    @action(
        detail=False,
        methods=["post"],
        url_path="two-factor-requests/(?P<request_id>[^/.]+)/resolve",
    )
    def resolve_two_factor(self, request, request_id=None, *args, **kwargs):
        """
        Resolve a 2FA request.
        """
        class_order = self.get_class_order()

        two_factor_request = ClassTwoFactorRequest.objects.get(
            pk=request_id,
            class_order=class_order,
        )

        serializer = ResolveTwoFactorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        updated = ClassAccessService.resolve_two_factor_request(
            request=two_factor_request,
            resolved_by=request.user,
            notes=data.get("notes", ""),
        )

        return Response(ClassTwoFactorRequestSerializer(updated).data)

    @staticmethod
    def _get_ip_address(request) -> str | None:
        """
        Extract client IP address.
        """
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR")