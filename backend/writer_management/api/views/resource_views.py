"""
1. get_serializer_class: missing # type: ignore[override]
2. get_queryset: missing # type: ignore[override]
3. self.request.query_params → self.request.GET
   (query_params is DRF-only; HttpRequest stubs only expose .GET)
"""

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from writer_management.services.resource_service import ResourceService
from writer_management.models.resources import WriterResource
from writer_management.api.permissions import IsWriterUser, _resolve_website
from writer_management.utils import get_writer_profile_for_website


class WriterResourceListView(ListAPIView):
    """GET /api/writer-management/resources/"""
    permission_classes = [IsWriterUser]

    def get_serializer_class(self): # type: ignore[override]
        from writer_management.api.serializers.resource_serializers import (
            WriterResourceSerializer,
        )
        return WriterResourceSerializer

    def get_queryset(self): # type: ignore[override]
        website = _resolve_website(self.request)

        # Fix 3: use .GET — HttpRequest always has it; query_params is DRF-only
        category_id = self.request.GET.get("category")
        category = None
        if category_id:
            from writer_management.models.resources import WriterResourceCategory
            try:
                category = WriterResourceCategory.objects.get(pk=category_id)
            except WriterResourceCategory.DoesNotExist:
                pass

        return ResourceService.get_active_resources(
            website=website,
            category=category,
        )


class WriterResourceDetailView(APIView):
    """
    GET /api/writer-management/resources/<pk>/
    Records a view when retrieved.
    """
    permission_classes = [IsWriterUser]

    def get(self, request, pk):
        from writer_management.api.serializers.resource_serializers import (
            WriterResourceSerializer,
        )
        try:
            resource = WriterResource.objects.select_related("category").get(
                pk=pk, is_active=True
            )
        except WriterResource.DoesNotExist:
            return Response({"detail": "Resource not found."}, status=404)

        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
        if profile:
            ResourceService.record_view(writer=profile, resource=resource)

        return Response(WriterResourceSerializer(resource).data)


class DownloadResourceView(APIView):
    """POST /api/writer-management/resources/<pk>/download/"""
    permission_classes = [IsWriterUser]

    def post(self, request, pk):
        try:
            resource = WriterResource.objects.get(pk=pk, is_active=True)
        except WriterResource.DoesNotExist:
            return Response({"detail": "Resource not found."}, status=404)

        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
        if profile:
            ResourceService.record_download(writer=profile, resource=resource)

        file_url = resource.file_url or resource.external_url
        return Response({
            "detail": "Download recorded.",
            "file_url": file_url,
        })