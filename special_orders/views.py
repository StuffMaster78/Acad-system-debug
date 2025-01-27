from rest_framework.viewsets import ModelViewSet
from .models import (
    PredefinedSpecialOrderConfig, SpecialOrder, Milestone, ProgressLog, WriterBonus
)
from .serializers import (
    PredefinedSpecialOrderConfigSerializer, SpecialOrderSerializer, MilestoneSerializer, ProgressLogSerializer, WriterBonusSerializer
)


class PredefinedSpecialOrderConfigViewSet(ModelViewSet):
    """
    ViewSet for managing predefined-cost special orders.
    """
    queryset = PredefinedSpecialOrderConfig.objects.all()
    serializer_class = PredefinedSpecialOrderConfigSerializer

    def get_queryset(self):
        """
        Filter configs by website.
        """
        website = self.request.query_params.get('website')
        if website:
            return self.queryset.filter(website_id=website)
        return self.queryset


class SpecialOrderViewSet(ModelViewSet):
    """
    ViewSet for managing special orders.
    """
    queryset = SpecialOrder.objects.all()
    serializer_class = SpecialOrderSerializer

    def get_queryset(self):
        """
        Filter special orders based on user role and website.
        """
        user = self.request.user
        website = self.request.query_params.get('website')
        queryset = self.queryset

        if website:
            queryset = queryset.filter(website_id=website)

        if user.is_staff:
            return queryset.filter(is_approved=True, writer__isnull=True)
        elif user.role == 'writer':
            return queryset.filter(writer=user)
        return queryset.none()


class MilestoneViewSet(ModelViewSet):
    """
    ViewSet for managing milestones.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer

    def get_queryset(self):
        website = self.request.query_params.get('website')
        if website:
            return self.queryset.filter(website_id=website)
        return self.queryset


class ProgressLogViewSet(ModelViewSet):
    """
    ViewSet for managing progress logs.
    """
    queryset = ProgressLog.objects.all()
    serializer_class = ProgressLogSerializer

    def get_queryset(self):
        website = self.request.query_params.get('website')
        if website:
            return self.queryset.filter(website_id=website)
        return self.queryset


class WriterBonusViewSet(ModelViewSet):
    """
    ViewSet for managing writer bonuses.
    """
    queryset = WriterBonus.objects.all()
    serializer_class = WriterBonusSerializer

    def get_queryset(self):
        website = self.request.query_params.get('website')
        if website:
            return self.queryset.filter(website_id=website)
        return self.queryset