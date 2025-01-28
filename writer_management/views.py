from rest_framework import generics, permissions
from .models import (
    WriterProfile,
    WriterLeave,
    WriterActionLog,
    WriterEducation,
    PaymentHistory,
    WriterReward,
    WriterRating,
)
from .serializers import (
    WriterProfileSerializer,
    WriterLeaveSerializer,
    WriterActionLogSerializer,
    WriterEducationSerializer,
    PaymentHistorySerializer,
    WriterRewardSerializer,
    WriterRatingSerializer,
)
from .permissions import IsAdminOrSuperAdmin, IsWriter


class WriterProfileDetailView(generics.RetrieveAPIView):
    """
    Retrieve the profile of a specific writer.
    """
    queryset = WriterProfile.objects.all()
    serializer_class = WriterProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsWriter]


class WriterLeaveListCreateView(generics.ListCreateAPIView):
    """
    List or create leave requests for writers.
    """
    queryset = WriterLeave.objects.all()
    serializer_class = WriterLeaveSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


class WriterActionLogListView(generics.ListAPIView):
    """
    List action logs for writers.
    """
    queryset = WriterActionLog.objects.all()
    serializer_class = WriterActionLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


class WriterEducationListCreateView(generics.ListCreateAPIView):
    """
    List or create writer education records.
    """
    queryset = WriterEducation.objects.all()
    serializer_class = WriterEducationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


class PaymentHistoryListView(generics.ListAPIView):
    """
    List payment history for writers.
    """
    queryset = PaymentHistory.objects.all()
    serializer_class = PaymentHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


class WriterRewardListCreateView(generics.ListCreateAPIView):
    """
    List or create rewards for writers.
    """
    queryset = WriterReward.objects.all()
    serializer_class = WriterRewardSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


class WriterRatingListView(generics.ListAPIView):
    """
    List all ratings for writers.
    """
    queryset = WriterRating.objects.all()
    serializer_class = WriterRatingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
