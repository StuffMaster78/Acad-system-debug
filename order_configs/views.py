from rest_framework import viewsets, permissions, status
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
    
    @action(detail=False, methods=['post'], url_path='populate-defaults')
    def populate_defaults(self, request):
        """
        Populate default configurations for a website.
        Requires website_id in request data.
        """
        website_id = request.data.get('website_id')
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
            counts = populate_default_configs_for_website(website, skip_existing=True)
            return Response({
                "message": "Default configurations populated successfully",
                "website": {
                    "id": website.id,
                    "name": website.name,
                    "domain": website.domain
                },
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
