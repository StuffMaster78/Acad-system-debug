from typing import Any, cast
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.session_serializers import (
    RevokeAllSessionsSerializer,
    RevokeSessionSerializer,
    SessionSerializer,
    CurrentSessionResponseSerializer,
    ExtendSessionResponseSerializer,
)
from authentication.selectors.login_session_selectors import (
    get_session_by_id,
    list_active_sessions,
)
from authentication.services.login_session_service import (
    LoginSessionService,
)


class SessionListView(APIView):
    """
    List active sessions for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sessions = list_active_sessions(
            user=request.user,
            website=website,
        )
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RevokeSessionView(APIView):
    """
    Revoke a single session for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RevokeSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session_id = validated_data["session_id"]

        session = get_session_by_id(
            session_id=session_id,
            user=request.user,
            website=website,
        )
        if session is None:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        success = LoginSessionService.revoke_session(
            user=request.user,
            session_id=session_id,
            website=website,
            revoked_by=request.user,
        )

        if not success:
            return Response(
                {"detail": "Session could not be revoked."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"success": True},
            status=status.HTTP_200_OK,
        )


class RevokeAllSessionsView(APIView):
    """
    Revoke all active sessions for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RevokeAllSessionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not validated_data["confirm"]:
            return Response(
                {"detail": "Confirmation required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        revoked_count = LoginSessionService.revoke_all_sessions(
            user=request.user,
            website=website,
            revoked_by=request.user,
        )

        return Response(
            {
                "success": True,
                "revoked_sessions_count": revoked_count,
            },
            status=status.HTTP_200_OK,
        )
    

class CurrentSessionView(APIView):
    """
    Return the current authenticated LoginSession.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = LoginSessionService.get_current_session_from_request(
            request=request,
        )
        if session is None:
            return Response(
                {"detail": "Current session could not be resolved."},
                status=status.HTTP_404_NOT_FOUND,
            )

        idle_timeout_seconds = LoginSessionService.get_idle_timeout_seconds(
            session=session,
        )
        idle_remaining_seconds = (
            LoginSessionService.get_idle_remaining_seconds(
                session=session,
            )
        )
        warning_time_seconds = getattr(
            settings,
            "SESSION_WARNING_TIME",
            5 * 60,
        )

        serializer = CurrentSessionResponseSerializer(
            {
                "session_id": session.pk,
                "session_type": session.session_type,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "device_name": session.device_name,
                "fingerprint_hash": session.fingerprint_hash,
                "logged_in_at": session.logged_in_at,
                "last_activity_at": session.last_activity_at,
                "expires_at": session.expires_at,
                "is_active": session.is_active,
                "idle_timeout_seconds": idle_timeout_seconds,
                "idle_remaining_seconds": idle_remaining_seconds,
                "warning_time_seconds": warning_time_seconds,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExtendSessionView(APIView):
    """
    Refresh the current session's activity timestamp.

    Any valid authenticated request already extends activity through
    middleware, but this gives the frontend an explicit endpoint for
    'stay signed in' actions.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = LoginSessionService.get_current_session_from_request(
            request=request,
        )
        if session is None:
            return Response(
                {"detail": "Current session could not be resolved."},
                status=status.HTTP_404_NOT_FOUND,
            )

        LoginSessionService.touch_session(session=session)

        idle_timeout_seconds = LoginSessionService.get_idle_timeout_seconds(
            session=session,
        )
        idle_remaining_seconds = (
            LoginSessionService.get_idle_remaining_seconds(
                session=session,
            )
        )

        serializer = ExtendSessionResponseSerializer(
            {
                "success": True,
                "session_id": session.pk,
                "idle_timeout_seconds": idle_timeout_seconds,
                "idle_remaining_seconds": idle_remaining_seconds,
                "message": "Session extended successfully.",
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)