from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MediaAsset, MediaUsage
from .serializers import MediaAssetSerializer, MediaUsageSerializer


class IsAdminOrStaff(permissions.BasePermission):
    """
    Restrict media management to staff-like roles.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or getattr(user, "role", None) in ["admin", "superadmin"]:
            return True
        return False


class MediaAssetViewSet(viewsets.ModelViewSet):
    serializer_class = MediaAssetSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "alt_text", "caption", "tags"]

    def get_queryset(self):
        qs = MediaAsset.objects.filter(is_active=True)
        website_id = self.request.query_params.get("website_id")
        media_type = self.request.query_params.get("type")
        if website_id:
            qs = qs.filter(website_id=website_id)
        if media_type:
            qs = qs.filter(type=media_type)
        return qs

    def perform_destroy(self, instance):
        # Soft delete instead of removing the file to preserve references
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    @action(detail=False, methods=["get"])
    def types(self, request):
        """
        Return available media types for building filters & UI.
        """
        data = [
            {"value": value, "label": label}
            for value, label in MediaAsset.MediaType.choices
        ]
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def usages(self, request, pk=None):
        """Get all places where this media asset is used."""
        asset = self.get_object()
        usages = MediaUsage.get_usages_for_media(asset)
        serializer = MediaUsageSerializer(usages, many=True)
        return Response({
            'media_id': asset.id,
            'media_title': asset.title or str(asset),
            'usage_count': usages.count(),
            'usages': serializer.data
        }, status=200)
    
    @action(detail=True, methods=['get'])
    def can_delete(self, request, pk=None):
        """Check if this media asset can be safely deleted (no usages)."""
        asset = self.get_object()
        usages = MediaUsage.get_usages_for_media(asset)
        usage_count = usages.count()
        
        return Response({
            'media_id': asset.id,
            'media_title': asset.title or str(asset),
            'can_delete': usage_count == 0,
            'usage_count': usage_count,
            'warning': f'This file is used in {usage_count} place(s). Deleting may break content.' if usage_count > 0 else None
        }, status=200)


class MediaUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing media usage tracking."""
    queryset = MediaUsage.objects.all()
    serializer_class = MediaUsageSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [filters.SearchFilter]
    
    def get_queryset(self):
        """Filter by media or entity if provided."""
        queryset = super().get_queryset().select_related(
            'media_content_type', 'entity_content_type', 'website'
        )
        
        # Filter by media type and ID
        media_type = self.request.query_params.get('media_content_type')
        media_id = self.request.query_params.get('media_object_id')
        if media_type and media_id:
            from django.contrib.contenttypes.models import ContentType
            try:
                ct = ContentType.objects.get(model=media_type.lower())
                queryset = queryset.filter(
                    media_content_type=ct,
                    media_object_id=media_id
                )
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        
        # Filter by entity type and ID
        entity_type = self.request.query_params.get('entity_content_type')
        entity_id = self.request.query_params.get('entity_object_id')
        if entity_type and entity_id:
            from django.contrib.contenttypes.models import ContentType
            try:
                ct = ContentType.objects.get(model=entity_type.lower())
                queryset = queryset.filter(
                    entity_content_type=ct,
                    entity_object_id=entity_id
                )
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        return queryset


