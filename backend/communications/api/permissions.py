from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from communications.constants import CommunicationMessageStatus
from communications.models.message import CommunicationMessage
from communications.models.thread import CommunicationThread
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)


class CommunicationPermissionHelpers:
    """
    Shared permission helpers for communication API permissions.
    """

    @staticmethod
    def get_request_website(*, request: Request) -> Any:
        """
        Return request website if available.
        """
        return getattr(request, "website", None)

    @staticmethod
    def is_authenticated(*, request: Request) -> bool:
        """
        Return whether request user is authenticated.
        """
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated)

    @staticmethod
    def has_platform_message_access(*, request: Request) -> bool:
        """
        Return whether user has platform wide communication access.
        """
        return CommunicationThreadGuardService._has_platform_access(
            user=request.user,
        )

    @staticmethod
    def is_admin_or_superadmin(*, request: Request) -> bool:
        """
        Return whether user can perform admin moderation actions.
        """
        user = request.user

        return bool(
            getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
        )

    @staticmethod
    def is_staff_operator(*, request: Request) -> bool:
        """
        Return whether user is admin, superadmin, or support.
        """
        user = request.user

        return bool(
            getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
            or getattr(user, "is_support", False)
        )

    @staticmethod
    def get_thread_from_obj(*, obj: Any) -> CommunicationThread | None:
        """
        Resolve a thread from different communication objects.
        """
        if isinstance(obj, CommunicationThread):
            return obj

        thread = getattr(obj, "thread", None)

        if isinstance(thread, CommunicationThread):
            return thread

        return None

    @staticmethod
    def can_view_thread_obj(*, request: Request, obj: Any) -> bool:
        """
        Return whether user can view an object's thread.
        """
        website = CommunicationPermissionHelpers.get_request_website(
            request=request,
        )
        thread = CommunicationPermissionHelpers.get_thread_from_obj(obj=obj)

        if thread is None:
            return False

        if website is None:
            website = thread.website

        return CommunicationThreadGuardService.can_view_thread(
            user=request.user,
            website=website,
            thread=thread,
        )

    @staticmethod
    def can_send_to_thread_obj(*, request: Request, obj: Any) -> bool:
        """
        Return whether user can send to an object's thread.
        """
        website = CommunicationPermissionHelpers.get_request_website(
            request=request,
        )
        thread = CommunicationPermissionHelpers.get_thread_from_obj(obj=obj)

        if thread is None:
            return False

        if website is None:
            website = thread.website

        return CommunicationThreadGuardService.can_send_message(
            user=request.user,
            website=website,
            thread=thread,
        )


class IsAuthenticatedForCommunications(BasePermission):
    """
    Require authenticated users for communications APIs.
    """

    message = "Authentication is required."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check authenticated user.
        """
        return CommunicationPermissionHelpers.is_authenticated(
            request=request,
        )


class CanViewCommunicationThread(BasePermission):
    """
    Allow users to view only threads they are allowed to access.
    """

    message = "You cannot access this conversation."

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check object level thread visibility.
        """
        return CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        )


class CanSendCommunicationMessage(BasePermission):
    """
    Allow sending only when the user can send in the thread.
    """

    message = "You cannot send messages in this conversation."

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check whether user can send to this thread.
        """
        return CommunicationPermissionHelpers.can_send_to_thread_obj(
            request=request,
            obj=obj,
        )


class CanManageCommunicationParticipants(BasePermission):
    """
    Allow participant management by platform operators.
    """

    message = "You cannot manage participants for this conversation."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check platform staff access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_staff_operator(
                request=request,
            )
        )

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check thread visibility before participant management.
        """
        return CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        )


class CanAssignCommunicationThread(BasePermission):
    """
    Allow staff thread assignment actions.
    """

    message = "You cannot assign this conversation."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check staff operator access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_staff_operator(
                request=request,
            )
        )

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check thread access.
        """
        return CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        )


class CanModerateCommunication(BasePermission):
    """
    Allow moderation actions for admin and superadmin.
    """

    message = "You cannot moderate this communication."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check admin level access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_admin_or_superadmin(
                request=request,
            )
        )

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check underlying thread access.
        """
        return CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        )


class CanViewModerationQueue(BasePermission):
    """
    Allow staff operators to view moderation queues.
    """

    message = "You cannot view moderation records."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Allow admin, superadmin, and support.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_staff_operator(
                request=request,
            )
        )


class CanManageScreeningRules(BasePermission):
    """
    Allow admin and superadmin to manage screening rules.
    """

    message = "You cannot manage screening rules."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check admin level access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_admin_or_superadmin(
                request=request,
            )
        )


class CanReviewCommunicationLinks(BasePermission):
    """
    Allow admin and superadmin to approve, reject, or block links.
    """

    message = "You cannot review communication links."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check admin level access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_admin_or_superadmin(
                request=request,
            )
        )

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check thread access for link review.
        """
        return CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        )


class CanManageSavedReplies(BasePermission):
    """
    Allow staff operators to manage saved replies.
    """

    message = "You cannot manage saved replies."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check staff operator access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_staff_operator(
                request=request,
            )
        )


class CanViewCommunicationAuditLogs(BasePermission):
    """
    Allow audit log access for admin and superadmin.
    """

    message = "You cannot view communication audit logs."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check admin level access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_admin_or_superadmin(
                request=request,
            )
        )


class CanEscalateCommunicationThread(BasePermission):
    """
    Allow staff operators to create and resolve escalations.
    """

    message = "You cannot escalate this conversation."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check staff operator access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_staff_operator(
                request=request,
            )
        )

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check thread access.
        """
        return CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        )


class CanViewCommunicationSLA(BasePermission):
    """
    Allow staff operators to view SLA tracking.
    """

    message = "You cannot view communication SLA records."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check staff operator access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_staff_operator(
                request=request,
            )
        )


class CanManageThreadTags(BasePermission):
    """
    Allow staff operators to manage thread tags.
    """

    message = "You cannot manage thread tags."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check staff operator access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_staff_operator(
                request=request,
            )
        )


class CanViewCommunicationObject(BasePermission):
    """
    Generic object permission for communication related objects.
    """

    message = "You cannot access this communication object."

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check object access through its thread.
        """
        return CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        )


class CanEditCommunicationMessage(BasePermission):
    """
    Allow message editing.

    Admin and superadmin may edit any visible message.
    Normal users may edit their own active messages only.
    """

    message = "You cannot edit this message."

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check message edit permission.
        """
        if not isinstance(obj, CommunicationMessage):
            return False

        if not CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        ):
            return False

        if CommunicationPermissionHelpers.is_admin_or_superadmin(
            request=request,
        ):
            return True

        return bool(
            getattr(obj.sender, "id", None) == request.user.id
            and obj.status == CommunicationMessageStatus.ACTIVE
        )


class CanHideOrWithdrawMessage(BasePermission):
    """
    Allow hiding or withdrawing messages.

    Only admin and superadmin should perform these actions.
    """

    message = "You cannot hide or withdraw this message."

    def has_permission( # type: ignore[override]
            self,
            request: Request,
            view: APIView
        ):
        """
        Check admin level access.
        """
        return (
            CommunicationPermissionHelpers.is_authenticated(request=request)
            and CommunicationPermissionHelpers.is_admin_or_superadmin(
                request=request,
            )
        )

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        """
        Check message visibility before action.
        """
        return CommunicationPermissionHelpers.can_view_thread_obj(
            request=request,
            obj=obj,
        )