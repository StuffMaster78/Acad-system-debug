from rest_framework import viewsets, permissions
from .models import (
    PaperType, FormattingandCitationStyle, Subject,
    TypeOfWork, EnglishType, WriterDeadlineConfig,
    RevisionPolicyConfig
)
from .serializers import (
    PaperTypeSerializer,
    FormattingStyleSerializer,
    SubjectSerializer,
    TypeOfWorkSerializer,
    EnglishTypeSerializer,
    WriterDeadlineConfigSerializer,
    RevisionPolicyConfigSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response

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
