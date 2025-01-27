from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WriterLevel, PaymentHistory, WriterProgress, WriterOrderAssignment, WriterAvailability, WriterReview, WriterPerformance
from .serializers import (
    WriterLevelSerializer,
    PaymentHistorySerializer,
    WriterProgressSerializer,
    WriterOrderAssignmentSerializer,
    WriterAvailabilitySerializer,
    WriterPerformanceSerializer,
    WriterReviewSerializer,
)
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
    ordering = ['name']

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

class WriterReviewListView(generics.ListAPIView):
    """
    API endpoint to list reviews for a writer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WriterReviewSerializer

    def get_queryset(self):
        """
        Returns reviews for the authenticated writer.
        """
        return WriterReview.objects.filter(writer=self.request.user)
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


class WriterAvailabilityListView(generics.ListCreateAPIView):
    """
    API view to list and create writer availability.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WriterAvailabilitySerializer

    def get_queryset(self):
        """
        Returns availability records for the authenticated writer.
        """
        return WriterAvailability.objects.filter(writer=self.request.user)

    def perform_create(self, serializer):
        """
        Associates the availability record with the authenticated writer.
        """
        serializer.save(writer=self.request.user)


class WriterAvailabilityDetailView(APIView):
    """
    API view to retrieve, update, or delete a specific availability record.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, writer):
        """
        Retrieve the specific availability record for the writer.
        """
        try:
            return WriterAvailability.objects.get(pk=pk, writer=writer)
        except WriterAvailability.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Retrieve a specific availability record.
        """
        availability = self.get_object(pk, request.user)
        if not availability:
            return Response({"error": "Availability not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WriterAvailabilitySerializer(availability)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update a specific availability record.
        """
        availability = self.get_object(pk, request.user)
        if not availability:
            return Response({"error": "Availability not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WriterAvailabilitySerializer(availability, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a specific availability record.
        """
        availability = self.get_object(pk, request.user)
        if not availability:
            return Response({"error": "Availability not found."}, status=status.HTTP_404_NOT_FOUND)
        availability.delete()
        return Response({"message": "Availability deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class WriterPerformanceDetailView(generics.RetrieveAPIView):
    """
    API to retrieve performance details for a writer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WriterPerformanceSerializer

    def get_queryset(self):
        """
        Returns performance details for the authenticated writer.
        """
        return WriterPerformance.objects.filter(writer=self.request.user)