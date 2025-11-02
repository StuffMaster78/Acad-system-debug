from rest_framework import viewsets, permissions, status
from .models import (
    PaperType, FormattingandCitationStyle, Subject,
    TypeOfWork, EnglishType, WriterDeadlineConfig,
    RevisionPolicyConfig, EditingRequirementConfig
)
from .serializers import (
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

class PaperTypeViewSet(viewsets.ModelViewSet):
    queryset = PaperType.objects.all()
    serializer_class = PaperTypeSerializer


class FormattingStyleViewSet(viewsets.ModelViewSet):
    queryset = FormattingandCitationStyle.objects.all()
    serializer_class = FormattingStyleSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class TypeOfWorkViewSet(viewsets.ModelViewSet):
    queryset = TypeOfWork.objects.all()
    serializer_class = TypeOfWorkSerializer


class EnglishTypeViewSet(viewsets.ModelViewSet):
    queryset = EnglishType.objects.all()
    serializer_class = EnglishTypeSerializer


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
