"""
1. get_serializer_class: missing # type: ignore[override]
2. get_queryset: missing # type: ignore[override]
3. self.request.query_params → self.request.GET
   (query_params is DRF-only; HttpRequest stubs only expose .GET)
"""

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from writer_management.services.resource_service import ResourceService
from writer_management.models.resources import WriterResource, WriterResourceCategory
from writer_management.api.permissions import IsAdminUser, IsWriterUser, _resolve_website
from writer_management.utils import get_writer_profile_for_website


def _admin_website(request):
    website = _resolve_website(request)
    website_id = request.GET.get("website_id")
    if website_id and getattr(request.user, "role", None) == "superadmin":
        from websites.models import Website
        try:
            return Website.objects.get(pk=website_id)
        except Website.DoesNotExist:
            return None
    return website


def _resource_queryset_for_website(website) -> QuerySet[WriterResource]:
    return WriterResource.objects.select_related(
        "category",
        "created_by",
        "updated_by",
    ).filter(website=website).order_by("display_order", "-created_at")


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
        website = _resolve_website(request)
        try:
            resource = WriterResource.objects.select_related("category").get(
                pk=pk, is_active=True, website=website
            )
        except WriterResource.DoesNotExist:
            return Response({"detail": "Resource not found."}, status=404)

        profile = get_writer_profile_for_website(request.user, website)
        if profile:
            ResourceService.record_view(writer=profile, resource=resource)

        return Response(WriterResourceSerializer(resource).data)


class DownloadResourceView(APIView):
    """POST /api/writer-management/resources/<pk>/download/"""
    permission_classes = [IsWriterUser]

    def post(self, request, pk):
        website = _resolve_website(request)
        try:
            resource = WriterResource.objects.get(pk=pk, is_active=True)
        except WriterResource.DoesNotExist:
            return Response({"detail": "Resource not found."}, status=404)
        if resource.website_id != getattr(website, "pk", None):
            return Response({"detail": "Resource not found."}, status=404)

        profile = get_writer_profile_for_website(request.user, website)
        if profile:
            ResourceService.record_download(writer=profile, resource=resource)

        file_url = resource.file_url or resource.external_url
        if resource.files_app_file_id:
            try:
                from files_management.models import ManagedFile
                from files_management.services.storage_service import StorageService

                managed_file = ManagedFile.objects.get(
                    pk=resource.files_app_file_id,
                    website=resource.website,
                )
                file_url = StorageService.get_download_url(
                    managed_file,
                    force_download=True,
                )
            except Exception:
                file_url = resource.file_url or resource.external_url
        return Response({
            "detail": "Download recorded.",
            "file_url": file_url,
        })


class AdminWriterResourceCategoryListCreateView(APIView):
    """Admin/superadmin resource category board."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        from writer_management.api.serializers.resource_serializers import (
            WriterResourceCategorySerializer,
        )

        website = _admin_website(request)
        if website is None:
            return Response({"detail": "Website context is required."}, status=400)
        qs = WriterResourceCategory.objects.filter(website=website).order_by(
            "display_order",
            "name",
        )
        return Response(WriterResourceCategorySerializer(qs, many=True).data)

    def post(self, request):
        from writer_management.api.serializers.resource_serializers import (
            WriterResourceCategoryCreateSerializer,
            WriterResourceCategorySerializer,
        )

        website = _admin_website(request)
        if website is None:
            return Response({"detail": "Website context is required."}, status=400)
        serializer = WriterResourceCategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = WriterResourceCategory.objects.create(
            website=website,
            **serializer.validated_data,
        )
        return Response(
            WriterResourceCategorySerializer(category).data,
            status=status.HTTP_201_CREATED,
        )


class AdminWriterResourceListCreateView(APIView):
    """Admin/superadmin CRUD board for writer resources."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        from writer_management.api.serializers.resource_serializers import (
            WriterResourceAdminSerializer,
        )

        website = _admin_website(request)
        if website is None:
            return Response({"detail": "Website context is required."}, status=400)
        qs = _resource_queryset_for_website(website)
        resource_type = request.GET.get("resource_type")
        if resource_type:
            qs = qs.filter(resource_type=resource_type)
        active = request.GET.get("active")
        if active in {"true", "false"}:
            qs = qs.filter(is_active=(active == "true"))
        return Response(WriterResourceAdminSerializer(qs, many=True).data)

    def post(self, request):
        from writer_management.api.serializers.resource_serializers import (
            CreateWriterResourceSerializer,
            WriterResourceAdminSerializer,
        )

        website = _admin_website(request)
        if website is None:
            return Response({"detail": "Website context is required."}, status=400)
        serializer = CreateWriterResourceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.validated_data.get("category")
        if category is not None and category.website_id != website.pk:
            return Response(
                {"category": "Category does not belong to this website."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        resource = WriterResource.objects.create(
            website=website,
            created_by=request.user,
            updated_by=request.user,
            **serializer.validated_data,
        )
        return Response(
            WriterResourceAdminSerializer(resource).data,
            status=status.HTTP_201_CREATED,
        )


class AdminWriterResourceDetailView(APIView):
    """Update or retire an admin-managed writer resource."""

    permission_classes = [IsAdminUser]

    def _get_resource(self, request, pk):
        website = _admin_website(request)
        if website is None:
            return None
        return _resource_queryset_for_website(website).filter(pk=pk).first()

    def get(self, request, pk):
        from writer_management.api.serializers.resource_serializers import (
            WriterResourceAdminSerializer,
        )

        resource = self._get_resource(request, pk)
        if resource is None:
            return Response({"detail": "Resource not found."}, status=404)
        return Response(WriterResourceAdminSerializer(resource).data)

    def patch(self, request, pk):
        from writer_management.api.serializers.resource_serializers import (
            UpdateWriterResourceSerializer,
            WriterResourceAdminSerializer,
        )

        resource = self._get_resource(request, pk)
        if resource is None:
            return Response({"detail": "Resource not found."}, status=404)
        serializer = UpdateWriterResourceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = serializer.validated_data.get("category")
        if category is not None and category.website_id != resource.website_id:
            return Response(
                {"category": "Category does not belong to this website."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for field, value in serializer.validated_data.items():
            setattr(resource, field, value)
        resource.updated_by = request.user
        resource.save()
        return Response(WriterResourceAdminSerializer(resource).data)

    def delete(self, request, pk):
        resource = self._get_resource(request, pk)
        if resource is None:
            return Response({"detail": "Resource not found."}, status=404)
        resource.is_active = False
        resource.updated_by = request.user
        resource.save(update_fields=["is_active", "updated_by", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
