from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions.base import BasePlatformPermission
from core.utils.request_context import get_request_website
from files_management.models.file_access_log import FileAccessLog
from files_management.models.file_download_log import FileDownloadLog


class CanViewFileAudit(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "files.view_audit"
    require_tenant = False


class FileAccessLogListView(APIView):
    """
    List FileAccessLog entries for the resolved tenant.
    Supports filtering by managed_file_id, user_id, access_type.
    Returns most-recent-first, capped at 500 rows.
    """

    permission_classes = [permissions.IsAuthenticated, CanViewFileAudit]

    def get(self, request: Request) -> Response:
        website = get_request_website(request)

        qs = (
            FileAccessLog.objects
            .select_related("file", "user")
            .filter(file__bucket__isnull=False)
            .order_by("-created_at")
        )

        # Optional filters
        file_id = request.query_params.get("file_id")
        user_id = request.query_params.get("user_id")
        access_type = request.query_params.get("access_type")
        if file_id:
            qs = qs.filter(file__id=file_id)
        if user_id:
            qs = qs.filter(user__id=user_id)
        if access_type:
            qs = qs.filter(access_type=access_type)

        # Superadmin: all tenants; admin: own website only
        if getattr(request.user, "role", None) != "superadmin":
            qs = qs.filter(file__fileattachment__object__website=website).distinct()

        rows = qs[:500]

        data = [
            {
                "id": row.id,
                "file_id": row.file_id,
                "file_name": row.file.original_filename if row.file else "",
                "access_type": row.access_type,
                "user_id": row.user_id,
                "user_email": row.user.email if row.user else None,
                "ip_address": row.ip_address,
                "success": row.success,
                "error_detail": row.error_detail,
                "bytes_transferred": row.bytes_transferred,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]
        return Response(data)


class FileDownloadLogListView(APIView):
    """
    List FileDownloadLog entries for the resolved tenant.
    Returns most-recent-first, capped at 500 rows.
    """

    permission_classes = [permissions.IsAuthenticated, CanViewFileAudit]

    def get(self, request: Request) -> Response:
        qs = (
            FileDownloadLog.objects
            .select_related("file", "downloaded_by")
            .order_by("-downloaded_at")
        )

        file_id = request.query_params.get("file_id")
        user_id = request.query_params.get("user_id")
        if file_id:
            qs = qs.filter(file__id=file_id)
        if user_id:
            qs = qs.filter(downloaded_by__id=user_id)

        if getattr(request.user, "role", None) != "superadmin":
            website = get_request_website(request)
            qs = qs.filter(file__fileattachment__object__website=website).distinct()

        rows = qs[:500]

        data = [
            {
                "id": row.id,
                "file_id": row.file_id,
                "file_name": row.file.original_filename if row.file else "",
                "downloaded_by_id": row.downloaded_by_id,
                "downloaded_by_email": row.downloaded_by.email if row.downloaded_by else None,
                "ip_address": row.ip_address,
                "user_agent": row.user_agent,
                "downloaded_at": row.downloaded_at.isoformat() if row.downloaded_at else None,
            }
            for row in rows
        ]
        return Response(data)
