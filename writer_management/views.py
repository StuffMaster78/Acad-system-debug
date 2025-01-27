from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import WriterLevel, PaymentHistory, WriterProgress, WriterOrderAssignment
from .serializers import WriterLevelSerializer, PaymentHistorySerializer, WriterProgressSerializer, WriterOrderAssignmentSerializer
from .permissions import IsWriter


class WriterLevelListView(generics.ListAPIView):
    """
    API endpoint to list all writer levels.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WriterLevelSerializer
    queryset = WriterLevel.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'base_pay_per_page']


class PaymentHistoryListView(generics.ListAPIView):
    """
    API endpoint to list payment history for a writer with filtering and pagination.
    """
    permission_classes = [IsAuthenticated, IsWriter]
    serializer_class = PaymentHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_date']
    ordering_fields = ['payment_date', 'amount']

    def get_queryset(self):
        """
        Returns payment history for the authenticated writer.
        """
        return PaymentHistory.objects.filter(writer=self.request.user)


class WriterProgressListView(generics.ListAPIView):
    """
    API endpoint to list progress updates for a writer with filtering and pagination.
    """
    permission_classes = [IsAuthenticated, IsWriter]
    serializer_class = WriterProgressSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order']
    ordering_fields = ['timestamp', 'progress']

    def get_queryset(self):
        """
        Returns progress updates for the authenticated writer.
        """
        return WriterProgress.objects.filter(writer=self.request.user)


class WriterOrderAssignmentListView(generics.ListAPIView):
    """
    API to list orders assigned to a writer with filtering and pagination.
    """
    permission_classes = [IsAuthenticated, IsWriter]
    serializer_class = WriterOrderAssignmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'order']
    ordering_fields = ['assigned_date', 'completed_date']

    def get_queryset(self):
        """
        Returns orders assigned to the authenticated writer.
        """
        return WriterOrderAssignment.objects.filter(writer=self.request.user)