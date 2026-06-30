from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from files_management.api.permissions import IsTenantStaff
from files_management.models.file_version import FileVersion


class FileVersionListView(APIView):
    """
    List the version history of a managed file.
    Returns versions ordered most-recent-first.
    """

    permission_classes = [permissions.IsAuthenticated, IsTenantStaff]

    def get(self, request: Request, file_id: int) -> Response:
        versions = (
            FileVersion.objects
            .filter(file_id=file_id)
            .select_related("replaced_file", "created_by")
            .order_by("-version_number")
        )

        data = [
            {
                "id": v.id,
                "version_number": v.version_number,
                "replaced_file_id": v.replaced_file_id,
                "replaced_file_name": (
                    v.replaced_file.original_filename if v.replaced_file else None
                ),
                "created_by_email": v.created_by.email if v.created_by else None,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "notes": v.notes,
            }
            for v in versions
        ]
        return Response(data)
