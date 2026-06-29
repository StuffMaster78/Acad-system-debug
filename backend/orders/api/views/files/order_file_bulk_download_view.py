from __future__ import annotations

import io
import zipfile

from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from files_management.enums import FileVisibility
from files_management.selectors import FileAttachmentSelector
from orders.api.views.files.order_file_views import OrderFileBaseView
from orders.services.order_file_download_service import OrderFileDownloadService


# Visibility sets by role — mirrors OrderFilesListView logic
_CLIENT_EXCLUDED = {
    FileVisibility.STAFF_ONLY,
    FileVisibility.INTERNAL_ONLY,
    FileVisibility.WRITER_AND_STAFF,
}
_WRITER_EXCLUDED = {
    FileVisibility.STAFF_ONLY,
    FileVisibility.INTERNAL_ONLY,
    FileVisibility.CLIENT_AND_STAFF,
}
_STAFF_ROLES = {"admin", "superadmin", "editor", "support"}


class OrderFileBulkDownloadView(OrderFileBaseView):
    """
    Stream a ZIP archive of all order files the requesting user can access.

    Skips: external links (no binary to zip), files that fail the delivery
    guard, files whose storage read fails.

    GET /orders/<id>/files/bulk-download/
    Optional query param: ?section=final|instructions|all (default: all)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, order_id: int) -> StreamingHttpResponse:
        order = self.get_order(request, order_id)
        user = request.user
        role = getattr(user, "role", None)
        section = request.query_params.get("section", "all")

        # Role-based visibility filter
        if role in _STAFF_ROLES:
            excluded_visibility: set = set()
        elif role == "writer":
            excluded_visibility = _WRITER_EXCLUDED
        else:
            excluded_visibility = _CLIENT_EXCLUDED

        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(order)
        attachments = (
            FileAttachmentSelector.for_object(
                content_type=ct,
                object_id=order.pk,
            )
            .filter(is_active=True, managed_file__isnull=False)
            .exclude(visibility__in=excluded_visibility)
            .select_related("managed_file")
        )

        if section == "final":
            attachments = attachments.filter(purpose="order_final")
        elif section == "instructions":
            attachments = attachments.filter(purpose__in=["order_instruction", "order_reference"])

        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")

        def _iter_zip():
            buf = io.BytesIO()
            seen_names: dict[str, int] = {}

            with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
                for att in attachments:
                    mf = att.managed_file
                    if not mf:
                        continue

                    # Try delivery guard — skip blocked files silently
                    try:
                        OrderFileDownloadService.get_download_url(
                            order=order,
                            user=user,
                            attachment=att,
                            ip_address=ip,
                            user_agent=ua,
                        )
                    except Exception:
                        continue

                    # Read file bytes
                    data = _read_managed_file(mf)
                    if not data:
                        continue

                    # De-duplicate filenames
                    name = mf.original_filename or f"file_{att.id}"
                    if name in seen_names:
                        seen_names[name] += 1
                        base, _, ext = name.rpartition(".")
                        name = f"{base}_{seen_names[name]}.{ext}" if ext else f"{name}_{seen_names[name]}"
                    else:
                        seen_names[name] = 0

                    zf.writestr(name, data)

            buf.seek(0)
            while chunk := buf.read(65536):
                yield chunk

        zip_name = f"order-{order_id}-files.zip"
        response = StreamingHttpResponse(
            _iter_zip(),
            content_type="application/zip",
        )
        response["Content-Disposition"] = f'attachment; filename="{zip_name}"'
        return response


def _read_managed_file(managed_file) -> bytes | None:
    """Read file bytes from local storage or Spaces."""
    try:
        if managed_file.file:
            managed_file.file.open("rb")
            data = managed_file.file.read()
            managed_file.file.close()
            return data
    except Exception:
        pass
    try:
        from files_management.services.storage_service import StorageService
        client = StorageService._get_client(managed_file.bucket)
        response = client.get_object(
            Bucket=managed_file.bucket.spaces_bucket_name,
            Key=managed_file.storage_key,
        )
        return response["Body"].read()
    except Exception:
        return None
