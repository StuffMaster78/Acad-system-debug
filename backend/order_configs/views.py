from rest_framework import viewsets, permissions, status
from django.db.models import Q
from django.utils import timezone
from .models import (
    AcademicLevel, PaperType, FormattingandCitationStyle, Subject,
    TypeOfWork, EnglishType, WriterDeadlineConfig,
    RevisionPolicyConfig, EditingRequirementConfig
)
from .serializers import (
    AcademicLevelSerializer,
    PaperTypeSerializer,
    FormattingStyleSerializer,
    SubjectSerializer,
    TypeOfWorkSerializer,
    EnglishTypeSerializer,
    WriterDeadlineConfigSerializer,
    RevisionPolicyConfigSerializer,
    EditingRequirementConfigSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from authentication.permissions import IsAdminOrSuperAdmin
from websites.models import Website

class AcademicLevelViewSet(viewsets.ModelViewSet):
    queryset = AcademicLevel.objects.all()
    serializer_class = AcademicLevelSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset.select_related('website')


class PaperTypeViewSet(viewsets.ModelViewSet):
    queryset = PaperType.objects.all()
    serializer_class = PaperTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset.select_related('website')


class FormattingStyleViewSet(viewsets.ModelViewSet):
    queryset = FormattingandCitationStyle.objects.all()
    serializer_class = FormattingStyleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset.select_related('website')


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset.select_related('website')


class TypeOfWorkViewSet(viewsets.ModelViewSet):
    queryset = TypeOfWork.objects.all()
    serializer_class = TypeOfWorkSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset.select_related('website')


class EnglishTypeViewSet(viewsets.ModelViewSet):
    queryset = EnglishType.objects.all()
    serializer_class = EnglishTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset.select_related('website')


class WriterDeadlineConfigViewSet(viewsets.ModelViewSet):
    queryset = WriterDeadlineConfig.objects.all()
    serializer_class = WriterDeadlineConfigSerializer


class RevisionPolicyConfigViewSet(viewsets.ModelViewSet):
    queryset = RevisionPolicyConfig.objects.all().order_by('-created_at')
    serializer_class = RevisionPolicyConfigSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can manage revision configs

    def perform_create(self, serializer):
        # Ensure the new config is set to active and others are deactivated
        instance = serializer.save()
        if instance.active:
            RevisionPolicyConfig.objects.exclude(pk=instance.pk).update(active=False)

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.active:
            RevisionPolicyConfig.objects.exclude(pk=instance.pk).update(active=False)

    @action(detail=True, methods=['post'], url_path='activate')
    def activate_policy(self, request, pk=None):
        config = self.get_object()

        # Deactivate all other policies for the same website
        RevisionPolicyConfig.objects.filter(website=config.website, active=True).exclude(pk=config.pk).update(active=False)

        # Activate this one
        config.active = True
        config.save()

        return Response(
            {"message": f"Revision policy '{config.name}' is now active for website '{config.website.name}'."},
            status=status.HTTP_200_OK
        )
    
    def save(self, *args, **kwargs):
        if self.active:
            RevisionPolicyConfig.objects.filter(website=self.website, active=True).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)


class EditingRequirementConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing editing requirement configurations.
    Admin-only endpoint.
    """
    queryset = EditingRequirementConfig.objects.select_related('website', 'created_by')
    serializer_class = EditingRequirementConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def get_config(self, request):
        """Get editing config for current website."""
        from websites.utils import get_current_website
        from editor_management.services.editing_decision_service import EditingDecisionService
        
        website = get_current_website(request)
        if not website:
            return Response(
                {"detail": "Website context required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        config = EditingDecisionService.get_config(website)
        if config:
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        else:
            # Return default config structure
            return Response({
                "website": website.id,
                "enable_editing_by_default": True,
                "skip_editing_for_urgent": True,
                "allow_editing_for_early_submissions": True,
                "early_submission_hours_threshold": 24,
                "editing_required_for_first_orders": True,
                "editing_required_for_high_value": True,
                "high_value_threshold": "300.00",
                "message": "No custom configuration - using defaults"
            })


class OrderConfigManagementViewSet(viewsets.ViewSet):
    """
    ViewSet for managing order configurations (populate defaults, etc.)
    Admin-only endpoint.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    @action(detail=False, methods=['get'], url_path='dropdown-options')
    def dropdown_options(self, request):
        """
        Get all order configuration options for dropdowns.
        Filtered by website_id query parameter or user's website.
        """
        website_id = request.query_params.get('website_id')
        user_website = None
        
        # Get user's website if not superadmin
        if request.user.role != 'superadmin':
            user_website = getattr(request.user, 'website', None)
            if user_website:
                website_id = str(user_website.id)
        
        website_filter = Q()
        if website_id:
            website_filter = Q(website_id=website_id)
        elif user_website:
            website_filter = Q(website=user_website)
        
        return Response({
            'paper_types': [
                {'id': pt.id, 'name': pt.name, 'website_id': pt.website_id}
                for pt in PaperType.objects.filter(website_filter).select_related('website').order_by('name')
            ],
            'formatting_styles': [
                {'id': fs.id, 'name': fs.name, 'website_id': fs.website_id}
                for fs in FormattingandCitationStyle.objects.filter(website_filter).select_related('website').order_by('name')
            ],
            'subjects': [
                {'id': s.id, 'name': s.name, 'is_technical': s.is_technical, 'website_id': s.website_id}
                for s in Subject.objects.filter(website_filter).select_related('website').order_by('name')
            ],
            'academic_levels': [
                {'id': al.id, 'name': al.name, 'website_id': al.website_id}
                for al in AcademicLevel.objects.filter(website_filter).select_related('website').order_by('name')
            ],
            'types_of_work': [
                {'id': tow.id, 'name': tow.name, 'website_id': tow.website_id}
                for tow in TypeOfWork.objects.filter(website_filter).select_related('website').order_by('name')
            ],
            'english_types': [
                {'id': et.id, 'name': et.name, 'code': et.code, 'website_id': et.website_id}
                for et in EnglishType.objects.filter(website_filter).select_related('website').order_by('name')
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='available-default-sets')
    def available_default_sets(self, request):
        """
        Get list of available default sets that can be cloned.
        """
        from order_configs.services.default_configs import get_available_default_sets
        return Response(get_available_default_sets(), status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='populate-defaults')
    def populate_defaults(self, request):
        """
        Populate default configurations for a website.
        Requires website_id in request data.
        Optional: default_set ('general', 'nursing', 'technical')
        """
        website_id = request.data.get('website_id')
        default_set = request.data.get('default_set', 'general')
        
        if not website_id:
            return Response(
                {"detail": "website_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from order_configs.services.default_configs import populate_default_configs_for_website
        
        try:
            counts = populate_default_configs_for_website(website, skip_existing=True, default_set=default_set)
            return Response({
                "message": f"Default configurations ({default_set}) populated successfully",
                "website": {
                    "id": website.id,
                    "name": website.name,
                    "domain": website.domain
                },
                "default_set": default_set,
                "created": counts,
                "summary": {
                    "total_created": sum(counts.values()),
                    "paper_types": counts['paper_types'],
                    "formatting_styles": counts['formatting_styles'],
                    "academic_levels": counts['academic_levels'],
                    "subjects": counts['subjects'],
                    "types_of_work": counts['types_of_work'],
                    "english_types": counts['english_types'],
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"Error populating defaults: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='clone-from-defaults')
    def clone_from_defaults(self, request):
        """
        Clone configurations from a default set to a website.
        Allows admins to select which default set to use and optionally
        clear existing configs before cloning.
        
        Requires:
        - website_id: The target website
        - default_set: Which default set to clone ('general', 'nursing', 'technical')
        
        Optional:
        - clear_existing: If True, delete existing configs before cloning (default: False)
        """
        website_id = request.data.get('website_id')
        default_set = request.data.get('default_set', 'general')
        clear_existing = request.data.get('clear_existing', False)
        
        if not website_id:
            return Response(
                {"detail": "website_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if default_set not in ['general', 'nursing', 'technical']:
            return Response(
                {"detail": "default_set must be one of: 'general', 'nursing', 'technical'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from order_configs.services.default_configs import populate_default_configs_for_website
        
        try:
            # Clear existing configs if requested
            if clear_existing:
                PaperType.objects.filter(website=website).delete()
                FormattingandCitationStyle.objects.filter(website=website).delete()
                AcademicLevel.objects.filter(website=website).delete()
                Subject.objects.filter(website=website).delete()
                TypeOfWork.objects.filter(website=website).delete()
                EnglishType.objects.filter(website=website).delete()
            
            # Populate with selected default set
            counts = populate_default_configs_for_website(
                website,
                skip_existing=not clear_existing,
                default_set=default_set
            )
            
            return Response({
                "message": f"Configurations cloned from '{default_set}' default set successfully",
                "website": {
                    "id": website.id,
                    "name": website.name,
                    "domain": website.domain
                },
                "default_set": default_set,
                "clear_existing": clear_existing,
                "created": counts,
                "summary": {
                    "total_created": sum(counts.values()),
                    "paper_types": counts['paper_types'],
                    "formatting_styles": counts['formatting_styles'],
                    "academic_levels": counts['academic_levels'],
                    "subjects": counts['subjects'],
                    "types_of_work": counts['types_of_work'],
                    "english_types": counts['english_types'],
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            return Response(
                {
                    "detail": f"Error cloning defaults: {str(e)}",
                    "error_details": traceback.format_exc() if hasattr(e, '__traceback__') else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='usage-analytics')
    def usage_analytics(self, request):
        """
        Get usage analytics for order configurations.
        Shows how many orders use each configuration item.
        Requires website_id query parameter.
        """
        website_id = request.query_params.get('website_id')
        if not website_id:
            return Response(
                {"detail": "website_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from orders.models import Order
        from django.db.models import Count, Q
        
        # Get usage counts for each config type
        analytics = {
            'paper_types': [],
            'formatting_styles': [],
            'academic_levels': [],
            'subjects': [],
            'types_of_work': [],
            'english_types': [],
        }
        
        # Paper Types
        paper_types = PaperType.objects.filter(website=website).annotate(
            usage_count=Count('order', filter=Q(order__website=website))
        ).order_by('-usage_count', 'name')
        analytics['paper_types'] = [
            {
                'id': pt.id,
                'name': pt.name,
                'usage_count': pt.usage_count,
                'is_used': pt.usage_count > 0
            }
            for pt in paper_types
        ]
        
        # Formatting Styles
        formatting_styles = FormattingandCitationStyle.objects.filter(website=website).annotate(
            usage_count=Count('order', filter=Q(order__website=website))
        ).order_by('-usage_count', 'name')
        analytics['formatting_styles'] = [
            {
                'id': fs.id,
                'name': fs.name,
                'usage_count': fs.usage_count,
                'is_used': fs.usage_count > 0
            }
            for fs in formatting_styles
        ]
        
        # Academic Levels
        academic_levels = AcademicLevel.objects.filter(website=website).annotate(
            usage_count=Count('order', filter=Q(order__website=website))
        ).order_by('-usage_count', 'name')
        analytics['academic_levels'] = [
            {
                'id': al.id,
                'name': al.name,
                'usage_count': al.usage_count,
                'is_used': al.usage_count > 0
            }
            for al in academic_levels
        ]
        
        # Subjects
        subjects = Subject.objects.filter(website=website).annotate(
            usage_count=Count('order', filter=Q(order__website=website))
        ).order_by('-usage_count', 'name')
        analytics['subjects'] = [
            {
                'id': s.id,
                'name': s.name,
                'is_technical': s.is_technical,
                'usage_count': s.usage_count,
                'is_used': s.usage_count > 0
            }
            for s in subjects
        ]
        
        # Types of Work
        types_of_work = TypeOfWork.objects.filter(website=website).annotate(
            usage_count=Count('order', filter=Q(order__website=website))
        ).order_by('-usage_count', 'name')
        analytics['types_of_work'] = [
            {
                'id': tow.id,
                'name': tow.name,
                'usage_count': tow.usage_count,
                'is_used': tow.usage_count > 0
            }
            for tow in types_of_work
        ]
        
        # English Types
        english_types = EnglishType.objects.filter(website=website).annotate(
            usage_count=Count('order', filter=Q(order__website=website))
        ).order_by('-usage_count', 'name')
        analytics['english_types'] = [
            {
                'id': et.id,
                'name': et.name,
                'code': et.code,
                'usage_count': et.usage_count,
                'is_used': et.usage_count > 0
            }
            for et in english_types
        ]
        
        # Summary statistics
        total_configs = sum(len(v) for v in analytics.values())
        unused_configs = sum(sum(1 for item in v if not item['is_used']) for v in analytics.values())
        used_configs = total_configs - unused_configs
        
        return Response({
            'website': {
                'id': website.id,
                'name': website.name,
                'domain': website.domain
            },
            'analytics': analytics,
            'summary': {
                'total_configs': total_configs,
                'used_configs': used_configs,
                'unused_configs': unused_configs,
                'usage_percentage': round((used_configs / total_configs * 100) if total_configs > 0 else 0, 2)
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        Bulk delete order configurations.
        Requires:
        - config_type: Type of config ('paper-types', 'subjects', etc.)
        - ids: List of config IDs to delete
        - website_id: Website ID (optional, for validation)
        """
        config_type = request.data.get('config_type')
        ids = request.data.get('ids', [])
        website_id = request.data.get('website_id')
        
        if not config_type or not ids:
            return Response(
                {"detail": "config_type and ids are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map config types to models
        model_map = {
            'paper-types': PaperType,
            'formatting-styles': FormattingandCitationStyle,
            'academic-levels': AcademicLevel,
            'subjects': Subject,
            'types-of-work': TypeOfWork,
            'english-types': EnglishType,
        }
        
        if config_type not in model_map:
            return Response(
                {"detail": f"Invalid config_type. Must be one of: {', '.join(model_map.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Model = model_map[config_type]
        
        # Check for usage before deletion
        from orders.models import Order
        from django.db.models import Q
        
        queryset = Model.objects.filter(id__in=ids)
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        # Check which configs are in use
        # Map config types to Order model field names
        field_map = {
            'paper-types': 'paper_type',
            'formatting-styles': 'formatting_style',
            'academic-levels': 'academic_level',
            'subjects': 'subject',
            'types-of-work': 'type_of_work',
            'english-types': 'english_type',
        }
        
        field_name = field_map.get(config_type)
        if not field_name:
            return Response(
                {"detail": "Invalid config_type."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        used_configs = []
        for config in queryset:
            usage_count = Order.objects.filter(**{field_name: config}).count()
            if usage_count > 0:
                used_configs.append({
                    'id': config.id,
                    'name': getattr(config, 'name', str(config)),
                    'usage_count': usage_count
                })
        
        # If any configs are in use, return error with details
        if used_configs:
            return Response(
                {
                    "detail": f"Cannot delete {len(used_configs)} configuration(s) that are in use.",
                    "used_configs": used_configs,
                    "message": f"{len(used_configs)} of {len(ids)} configuration(s) cannot be deleted because they are used in existing orders."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete configs
        deleted_count = queryset.delete()[0]
        
        return Response({
            "message": f"Successfully deleted {deleted_count} configuration(s).",
            "deleted_count": deleted_count
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='preview-clone')
    def preview_clone(self, request):
        """
        Preview what will be added/removed when cloning from defaults.
        Requires:
        - website_id: Target website
        - default_set: Which default set to clone ('general', 'nursing', 'technical')
        - clear_existing: Whether to clear existing configs first
        """
        website_id = request.data.get('website_id')
        default_set = request.data.get('default_set', 'general')
        clear_existing = request.data.get('clear_existing', False)
        
        if not website_id:
            return Response(
                {"detail": "website_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if default_set not in ['general', 'nursing', 'technical']:
            return Response(
                {"detail": "default_set must be one of: 'general', 'nursing', 'technical'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from order_configs.services.default_configs import DEFAULT_SETS
        
        if default_set not in DEFAULT_SETS:
            return Response(
                {"detail": "Invalid default set."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        config_set = DEFAULT_SETS[default_set]
        preview = {
            'paper_types': {'to_add': [], 'to_remove': [], 'to_keep': []},
            'formatting_styles': {'to_add': [], 'to_remove': [], 'to_keep': []},
            'academic_levels': {'to_add': [], 'to_remove': [], 'to_keep': []},
            'subjects': {'to_add': [], 'to_remove': [], 'to_keep': []},
            'types_of_work': {'to_add': [], 'to_remove': [], 'to_keep': []},
            'english_types': {'to_add': [], 'to_remove': [], 'to_keep': []},
        }
        
        # Helper function to check what will be added/removed
        def analyze_configs(model_class, default_list, existing_queryset):
            existing_names = set(existing_queryset.values_list('name', flat=True))
            default_names = set(default_list)
            
            to_add = list(default_names - existing_names)
            to_remove = list(existing_names - default_names) if clear_existing else []
            to_keep = list(existing_names & default_names)
            
            return {
                'to_add': sorted(to_add),
                'to_remove': sorted(to_remove),
                'to_keep': sorted(to_keep)
            }
        
        # Analyze each config type
        preview['paper_types'] = analyze_configs(
            PaperType,
            config_set['paper_types'],
            PaperType.objects.filter(website=website)
        )
        
        preview['formatting_styles'] = analyze_configs(
            FormattingandCitationStyle,
            config_set['formatting_styles'],
            FormattingandCitationStyle.objects.filter(website=website)
        )
        
        preview['academic_levels'] = analyze_configs(
            AcademicLevel,
            config_set['academic_levels'],
            AcademicLevel.objects.filter(website=website)
        )
        
        # Subjects need special handling (tuples)
        existing_subjects = set(Subject.objects.filter(website=website).values_list('name', flat=True))
        default_subjects = set(name for name, _ in config_set['subjects'])
        preview['subjects'] = {
            'to_add': sorted(default_subjects - existing_subjects),
            'to_remove': sorted(existing_subjects - default_subjects) if clear_existing else [],
            'to_keep': sorted(existing_subjects & default_subjects)
        }
        
        preview['types_of_work'] = analyze_configs(
            TypeOfWork,
            config_set['types_of_work'],
            TypeOfWork.objects.filter(website=website)
        )
        
        # English types need special handling (tuples)
        existing_english = set(EnglishType.objects.filter(website=website).values_list('name', flat=True))
        default_english = set(name for name, _ in config_set['english_types'])
        preview['english_types'] = {
            'to_add': sorted(default_english - existing_english),
            'to_remove': sorted(existing_english - default_english) if clear_existing else [],
            'to_keep': sorted(existing_english & default_english)
        }
        
        # Calculate totals
        total_to_add = sum(len(v['to_add']) for v in preview.values())
        total_to_remove = sum(len(v['to_remove']) for v in preview.values())
        total_to_keep = sum(len(v['to_keep']) for v in preview.values())
        
        return Response({
            'website': {
                'id': website.id,
                'name': website.name,
                'domain': website.domain
            },
            'default_set': default_set,
            'clear_existing': clear_existing,
            'preview': preview,
            'summary': {
                'total_to_add': total_to_add,
                'total_to_remove': total_to_remove,
                'total_to_keep': total_to_keep,
                'total_changes': total_to_add + total_to_remove
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='export')
    def export_configs(self, request):
        """
        Export order configurations to JSON.
        Requires website_id query parameter.
        """
        website_id = request.query_params.get('website_id')
        if not website_id:
            return Response(
                {"detail": "website_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from django.utils import timezone
        
        export_data = {
            'website': {
                'id': website.id,
                'name': website.name,
                'domain': website.domain
            },
            'exported_at': timezone.now().isoformat(),
            'configs': {
                'paper_types': [
                    {'name': pt.name} for pt in PaperType.objects.filter(website=website).order_by('name')
                ],
                'formatting_styles': [
                    {'name': fs.name} for fs in FormattingandCitationStyle.objects.filter(website=website).order_by('name')
                ],
                'academic_levels': [
                    {'name': al.name} for al in AcademicLevel.objects.filter(website=website).order_by('name')
                ],
                'subjects': [
                    {'name': s.name, 'is_technical': s.is_technical}
                    for s in Subject.objects.filter(website=website).order_by('name')
                ],
                'types_of_work': [
                    {'name': tow.name} for tow in TypeOfWork.objects.filter(website=website).order_by('name')
                ],
                'english_types': [
                    {'name': et.name, 'code': et.code}
                    for et in EnglishType.objects.filter(website=website).order_by('name')
                ],
            }
        }
        
        return Response(export_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='import')
    def import_configs(self, request):
        """
        Import order configurations from JSON.
        Requires:
        - website_id: Target website
        - configs: JSON object with config arrays
        - skip_existing: Whether to skip existing configs (default: True)
        """
        website_id = request.data.get('website_id')
        configs = request.data.get('configs', {})
        skip_existing = request.data.get('skip_existing', True)
        
        if not website_id:
            return Response(
                {"detail": "website_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from django.utils import timezone
        
        results = {
            'paper_types': {'created': 0, 'skipped': 0, 'errors': []},
            'formatting_styles': {'created': 0, 'skipped': 0, 'errors': []},
            'academic_levels': {'created': 0, 'skipped': 0, 'errors': []},
            'subjects': {'created': 0, 'skipped': 0, 'errors': []},
            'types_of_work': {'created': 0, 'skipped': 0, 'errors': []},
            'english_types': {'created': 0, 'skipped': 0, 'errors': []},
        }
        
        # Import Paper Types
        for item in configs.get('paper_types', []):
            name = item.get('name', '').strip()
            if not name:
                continue
            if skip_existing and PaperType.objects.filter(website=website, name=name).exists():
                results['paper_types']['skipped'] += 1
                continue
            try:
                PaperType.objects.get_or_create(website=website, name=name)
                results['paper_types']['created'] += 1
            except Exception as e:
                results['paper_types']['errors'].append(f"{name}: {str(e)}")
        
        # Import Formatting Styles
        for item in configs.get('formatting_styles', []):
            name = item.get('name', '').strip()
            if not name:
                continue
            if skip_existing and FormattingandCitationStyle.objects.filter(website=website, name=name).exists():
                results['formatting_styles']['skipped'] += 1
                continue
            try:
                FormattingandCitationStyle.objects.get_or_create(website=website, name=name)
                results['formatting_styles']['created'] += 1
            except Exception as e:
                results['formatting_styles']['errors'].append(f"{name}: {str(e)}")
        
        # Import Academic Levels
        for item in configs.get('academic_levels', []):
            name = item.get('name', '').strip()
            if not name:
                continue
            if skip_existing and AcademicLevel.objects.filter(website=website, name=name).exists():
                results['academic_levels']['skipped'] += 1
                continue
            try:
                AcademicLevel.objects.get_or_create(website=website, name=name)
                results['academic_levels']['created'] += 1
            except Exception as e:
                results['academic_levels']['errors'].append(f"{name}: {str(e)}")
        
        # Import Subjects
        for item in configs.get('subjects', []):
            name = item.get('name', '').strip()
            if not name:
                continue
            is_technical = item.get('is_technical', False)
            if skip_existing and Subject.objects.filter(website=website, name=name).exists():
                results['subjects']['skipped'] += 1
                continue
            try:
                Subject.objects.get_or_create(
                    website=website,
                    name=name,
                    defaults={'is_technical': is_technical}
                )
                results['subjects']['created'] += 1
            except Exception as e:
                results['subjects']['errors'].append(f"{name}: {str(e)}")
        
        # Import Types of Work
        for item in configs.get('types_of_work', []):
            name = item.get('name', '').strip()
            if not name:
                continue
            if skip_existing and TypeOfWork.objects.filter(website=website, name=name).exists():
                results['types_of_work']['skipped'] += 1
                continue
            try:
                TypeOfWork.objects.get_or_create(website=website, name=name)
                results['types_of_work']['created'] += 1
            except Exception as e:
                results['types_of_work']['errors'].append(f"{name}: {str(e)}")
        
        # Import English Types
        for item in configs.get('english_types', []):
            name = item.get('name', '').strip()
            code = item.get('code', '').strip()
            if not name:
                continue
            if skip_existing and EnglishType.objects.filter(website=website, name=name).exists():
                results['english_types']['skipped'] += 1
                continue
            try:
                EnglishType.objects.get_or_create(
                    website=website,
                    name=name,
                    defaults={'code': code} if code else {}
                )
                results['english_types']['created'] += 1
            except Exception as e:
                results['english_types']['errors'].append(f"{name}: {str(e)}")
        
        total_created = sum(r['created'] for r in results.values())
        total_skipped = sum(r['skipped'] for r in results.values())
        total_errors = sum(len(r['errors']) for r in results.values())
        
        return Response({
            'website': {
                'id': website.id,
                'name': website.name,
                'domain': website.domain
            },
            'results': results,
            'summary': {
                'total_created': total_created,
                'total_skipped': total_skipped,
                'total_errors': total_errors
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='export')
    def export_configs(self, request):
        """
        Export order configurations to JSON.
        Requires website_id query parameter.
        """
        website_id = request.query_params.get('website_id')
        if not website_id:
            return Response(
                {"detail": "website_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Collect all configs
        export_data = {
            'website': {
                'id': website.id,
                'name': website.name,
                'domain': website.domain
            },
            'exported_at': timezone.now().isoformat() if hasattr(timezone, 'now') else str(timezone.now()),
            'configurations': {
                'paper_types': [
                    {'name': pt.name} for pt in PaperType.objects.filter(website=website).order_by('name')
                ],
                'formatting_styles': [
                    {'name': fs.name} for fs in FormattingandCitationStyle.objects.filter(website=website).order_by('name')
                ],
                'academic_levels': [
                    {'name': al.name} for al in AcademicLevel.objects.filter(website=website).order_by('name')
                ],
                'subjects': [
                    {'name': s.name, 'is_technical': s.is_technical} 
                    for s in Subject.objects.filter(website=website).order_by('name')
                ],
                'types_of_work': [
                    {'name': tow.name} for tow in TypeOfWork.objects.filter(website=website).order_by('name')
                ],
                'english_types': [
                    {'name': et.name, 'code': et.code} 
                    for et in EnglishType.objects.filter(website=website).order_by('name')
                ],
            }
        }
        
        return Response(export_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='import')
    def import_configs(self, request):
        """
        Import order configurations from JSON.
        Requires website_id and configurations data.
        """
        website_id = request.data.get('website_id')
        configurations = request.data.get('configurations', {})
        skip_existing = request.data.get('skip_existing', True)
        
        if not website_id:
            return Response(
                {"detail": "website_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        results = {
            'paper_types': {'created': 0, 'skipped': 0, 'errors': []},
            'formatting_styles': {'created': 0, 'skipped': 0, 'errors': []},
            'academic_levels': {'created': 0, 'skipped': 0, 'errors': []},
            'subjects': {'created': 0, 'skipped': 0, 'errors': []},
            'types_of_work': {'created': 0, 'skipped': 0, 'errors': []},
            'english_types': {'created': 0, 'skipped': 0, 'errors': []},
        }
        
        # Import Paper Types
        for item in configurations.get('paper_types', []):
            name = item.get('name')
            if not name:
                continue
            if skip_existing and PaperType.objects.filter(website=website, name=name).exists():
                results['paper_types']['skipped'] += 1
                continue
            try:
                PaperType.objects.get_or_create(website=website, name=name)
                results['paper_types']['created'] += 1
            except Exception as e:
                results['paper_types']['errors'].append(f"{name}: {str(e)}")
        
        # Import Formatting Styles
        for item in configurations.get('formatting_styles', []):
            name = item.get('name')
            if not name:
                continue
            if skip_existing and FormattingandCitationStyle.objects.filter(website=website, name=name).exists():
                results['formatting_styles']['skipped'] += 1
                continue
            try:
                FormattingandCitationStyle.objects.get_or_create(website=website, name=name)
                results['formatting_styles']['created'] += 1
            except Exception as e:
                results['formatting_styles']['errors'].append(f"{name}: {str(e)}")
        
        # Import Academic Levels
        for item in configurations.get('academic_levels', []):
            name = item.get('name')
            if not name:
                continue
            if skip_existing and AcademicLevel.objects.filter(website=website, name=name).exists():
                results['academic_levels']['skipped'] += 1
                continue
            try:
                AcademicLevel.objects.get_or_create(website=website, name=name)
                results['academic_levels']['created'] += 1
            except Exception as e:
                results['academic_levels']['errors'].append(f"{name}: {str(e)}")
        
        # Import Subjects
        for item in configurations.get('subjects', []):
            name = item.get('name')
            if not name:
                continue
            is_technical = item.get('is_technical', False)
            if skip_existing and Subject.objects.filter(website=website, name=name).exists():
                results['subjects']['skipped'] += 1
                continue
            try:
                Subject.objects.get_or_create(website=website, name=name, defaults={'is_technical': is_technical})
                results['subjects']['created'] += 1
            except Exception as e:
                results['subjects']['errors'].append(f"{name}: {str(e)}")
        
        # Import Types of Work
        for item in configurations.get('types_of_work', []):
            name = item.get('name')
            if not name:
                continue
            if skip_existing and TypeOfWork.objects.filter(website=website, name=name).exists():
                results['types_of_work']['skipped'] += 1
                continue
            try:
                TypeOfWork.objects.get_or_create(website=website, name=name)
                results['types_of_work']['created'] += 1
            except Exception as e:
                results['types_of_work']['errors'].append(f"{name}: {str(e)}")
        
        # Import English Types
        for item in configurations.get('english_types', []):
            name = item.get('name')
            code = item.get('code', '')
            if not name:
                continue
            if skip_existing and EnglishType.objects.filter(website=website, name=name).exists():
                results['english_types']['skipped'] += 1
                continue
            try:
                EnglishType.objects.get_or_create(website=website, name=name, defaults={'code': code})
                results['english_types']['created'] += 1
            except Exception as e:
                results['english_types']['errors'].append(f"{name}: {str(e)}")
        
        total_created = sum(r['created'] for r in results.values())
        total_skipped = sum(r['skipped'] for r in results.values())
        total_errors = sum(len(r['errors']) for r in results.values())
        
        return Response({
            'message': f'Import completed: {total_created} created, {total_skipped} skipped, {total_errors} errors',
            'website': {
                'id': website.id,
                'name': website.name,
                'domain': website.domain
            },
            'results': results,
            'summary': {
                'total_created': total_created,
                'total_skipped': total_skipped,
                'total_errors': total_errors
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='check-defaults')
    def check_defaults(self, request):
        """
        Check which configurations are defaults vs custom for a website.
        Requires website_id query parameter.
        """
        website_id = request.query_params.get('website_id')
        if not website_id:
            return Response(
                {"detail": "website_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {"detail": "Website not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from order_configs.services.default_configs import (
            is_default_paper_type, is_default_formatting_style,
            is_default_academic_level, is_default_subject,
            is_default_type_of_work, is_default_english_type
        )
        
        # Check paper types
        paper_types = PaperType.objects.filter(website=website)
        paper_types_data = [
            {"id": pt.id, "name": pt.name, "is_default": is_default_paper_type(pt.name)}
            for pt in paper_types
        ]
        
        # Check formatting styles
        formatting_styles = FormattingandCitationStyle.objects.filter(website=website)
        formatting_styles_data = [
            {"id": fs.id, "name": fs.name, "is_default": is_default_formatting_style(fs.name)}
            for fs in formatting_styles
        ]
        
        # Check academic levels
        academic_levels = AcademicLevel.objects.filter(website=website)
        academic_levels_data = [
            {"id": al.id, "name": al.name, "is_default": is_default_academic_level(al.name)}
            for al in academic_levels
        ]
        
        # Check subjects
        subjects = Subject.objects.filter(website=website)
        subjects_data = [
            {"id": s.id, "name": s.name, "is_technical": s.is_technical, "is_default": is_default_subject(s.name)}
            for s in subjects
        ]
        
        # Check types of work
        types_of_work = TypeOfWork.objects.filter(website=website)
        types_of_work_data = [
            {"id": tow.id, "name": tow.name, "is_default": is_default_type_of_work(tow.name)}
            for tow in types_of_work
        ]
        
        # Check English types
        english_types = EnglishType.objects.filter(website=website)
        english_types_data = [
            {"id": et.id, "name": et.name, "code": et.code, "is_default": is_default_english_type(et.name)}
            for et in english_types
        ]
        
        return Response({
            "website": {
                "id": website.id,
                "name": website.name,
                "domain": website.domain
            },
            "configurations": {
                "paper_types": paper_types_data,
                "formatting_styles": formatting_styles_data,
                "academic_levels": academic_levels_data,
                "subjects": subjects_data,
                "types_of_work": types_of_work_data,
                "english_types": english_types_data,
            },
            "summary": {
                "paper_types": {
                    "total": len(paper_types_data),
                    "defaults": sum(1 for pt in paper_types_data if pt["is_default"]),
                    "custom": sum(1 for pt in paper_types_data if not pt["is_default"])
                },
                "formatting_styles": {
                    "total": len(formatting_styles_data),
                    "defaults": sum(1 for fs in formatting_styles_data if fs["is_default"]),
                    "custom": sum(1 for fs in formatting_styles_data if not fs["is_default"])
                },
                "academic_levels": {
                    "total": len(academic_levels_data),
                    "defaults": sum(1 for al in academic_levels_data if al["is_default"]),
                    "custom": sum(1 for al in academic_levels_data if not al["is_default"])
                },
                "subjects": {
                    "total": len(subjects_data),
                    "defaults": sum(1 for s in subjects_data if s["is_default"]),
                    "custom": sum(1 for s in subjects_data if not s["is_default"])
                },
                "types_of_work": {
                    "total": len(types_of_work_data),
                    "defaults": sum(1 for tow in types_of_work_data if tow["is_default"]),
                    "custom": sum(1 for tow in types_of_work_data if not tow["is_default"])
                },
                "english_types": {
                    "total": len(english_types_data),
                    "defaults": sum(1 for et in english_types_data if et["is_default"]),
                    "custom": sum(1 for et in english_types_data if not et["is_default"])
                },
            }
        }, status=status.HTTP_200_OK)
