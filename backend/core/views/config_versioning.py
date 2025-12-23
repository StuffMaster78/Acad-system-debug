"""
API endpoints for configuration versioning.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from core.models.config_versioning import ConfigVersion
from core.services.config_versioning_service import ConfigVersioningService
from admin_management.permissions import IsAdmin


class ConfigVersioningViewSet(viewsets.ViewSet):
    """
    ViewSet for managing configuration versions.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='history')
    def get_version_history(self, request):
        """
        Get version history for a configuration object.
        
        Query params:
        - config_type: Model name (e.g., 'pricingconfiguration', 'writerconfig')
        - config_id: ID of the config object
        - limit: Number of versions to return (default: 50)
        """
        config_type = request.query_params.get('config_type')
        config_id = request.query_params.get('config_id')
        limit = int(request.query_params.get('limit', 50))
        
        if not config_type or not config_id:
            return Response(
                {"detail": "config_type and config_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get ContentType for the model
            content_type = ContentType.objects.get(model=config_type.lower())
        except ContentType.DoesNotExist:
            return Response(
                {"detail": f"Invalid config_type: {config_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get version history
        versions = ConfigVersion.get_version_history(
            content_type, int(config_id), limit=limit
        )
        
        # Serialize versions
        version_data = []
        for version in versions:
            version_data.append({
                'id': version.id,
                'version_number': version.version_number,
                'created_at': version.created_at.isoformat(),
                'created_by': {
                    'id': version.created_by.id,
                    'username': version.created_by.username,
                    'email': version.created_by.email
                } if version.created_by else None,
                'change_type': version.change_type,
                'change_summary': version.change_summary,
                'changed_fields': version.changed_fields,
                'notes': version.notes,
                'is_current': version.is_current,
                'config_data': version.config_data,
            })
        
        return Response({
            'config_type': config_type,
            'config_id': int(config_id),
            'versions': version_data,
            'total_versions': ConfigVersion.objects.filter(
                content_type=content_type,
                object_id=int(config_id)
            ).count()
        })
    
    @action(detail=False, methods=['get'], url_path='version/(?P<version_id>[^/.]+)')
    def get_version(self, request, version_id=None):
        """Get a specific version by ID."""
        try:
            version = ConfigVersion.objects.select_related(
                'created_by', 'content_type', 'previous_version'
            ).get(id=version_id)
        except ConfigVersion.DoesNotExist:
            return Response(
                {"detail": "Version not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'id': version.id,
            'version_number': version.version_number,
            'created_at': version.created_at.isoformat(),
            'created_by': {
                'id': version.created_by.id,
                'username': version.created_by.username,
                'email': version.created_by.email
            } if version.created_by else None,
            'change_type': version.change_type,
            'change_summary': version.change_summary,
            'changed_fields': version.changed_fields,
            'notes': version.notes,
            'is_current': version.is_current,
            'config_data': version.config_data,
            'config_type': version.content_type.model,
            'config_id': version.object_id,
            'previous_version_id': version.previous_version.id if version.previous_version else None,
        })
    
    @action(detail=False, methods=['post'], url_path='restore')
    def restore_version(self, request):
        """
        Restore a configuration to a previous version.
        
        Body:
        - version_id: ID of the version to restore
        - notes: Optional notes about the restoration
        """
        version_id = request.data.get('version_id')
        notes = request.data.get('notes', '')
        
        if not version_id:
            return Response(
                {"detail": "version_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            version = ConfigVersion.objects.select_related(
                'content_type', 'created_by'
            ).get(id=version_id)
        except ConfigVersion.DoesNotExist:
            return Response(
                {"detail": "Version not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if config object still exists
        if not version.config_object:
            return Response(
                {"detail": "Cannot restore: configuration object no longer exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Restore the version
            new_version = ConfigVersioningService.restore_version(
                version,
                restored_by=request.user,
                notes=notes
            )
            
            return Response({
                "detail": f"Configuration restored to version {version.version_number}.",
                "new_version": {
                    'id': new_version.id,
                    'version_number': new_version.version_number,
                    'created_at': new_version.created_at.isoformat(),
                },
                "restored_from": {
                    'id': version.id,
                    'version_number': version.version_number,
                }
            })
        except Exception as e:
            return Response(
                {"detail": f"Error restoring version: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='compare')
    def compare_versions(self, request):
        """
        Compare two versions of a configuration.
        
        Query params:
        - version1_id: ID of first version
        - version2_id: ID of second version
        """
        version1_id = request.query_params.get('version1_id')
        version2_id = request.query_params.get('version2_id')
        
        if not version1_id or not version2_id:
            return Response(
                {"detail": "version1_id and version2_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            version1 = ConfigVersion.objects.get(id=version1_id)
            version2 = ConfigVersion.objects.get(id=version2_id)
        except ConfigVersion.DoesNotExist:
            return Response(
                {"detail": "One or both versions not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Compare config data
        data1 = version1.config_data
        data2 = version2.config_data
        
        # Find differences
        all_keys = set(data1.keys()) | set(data2.keys())
        differences = {}
        
        for key in all_keys:
            val1 = data1.get(key)
            val2 = data2.get(key)
            
            if val1 != val2:
                differences[key] = {
                    'old_value': val1,
                    'new_value': val2,
                }
        
        return Response({
            'version1': {
                'id': version1.id,
                'version_number': version1.version_number,
                'created_at': version1.created_at.isoformat(),
            },
            'version2': {
                'id': version2.id,
                'version_number': version2.version_number,
                'created_at': version2.created_at.isoformat(),
            },
            'differences': differences,
            'total_differences': len(differences),
        })

