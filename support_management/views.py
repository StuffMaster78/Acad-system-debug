from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import (
    SupportProfile,
    SupportActivityLog,
    SupportNotification,
    TicketAssignment,
    DisputeResolutionLog,
)
from .serializers import (
    SupportProfileSerializer,
    SupportActivityLogSerializer,
    SupportNotificationSerializer,
    TicketAssignmentSerializer,
    DisputeResolutionLogSerializer,
)
from .permissions import IsAdminOrSuperAdmin, IsSupportOrAdmin


class SupportProfileViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for SupportProfile.
    """
    queryset = SupportProfile.objects.all()
    serializer_class = SupportProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    def perform_create(self, serializer):
        serializer.save()
        return Response({"message": "Support profile created successfully."}, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.delete()
        return Response({"message": "Support profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class SupportActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles retrieval of activity logs for support staff.
    """
    queryset = SupportActivityLog.objects.all()
    serializer_class = SupportActivityLogSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]


class SupportNotificationViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for SupportNotification.
    """
    queryset = SupportNotification.objects.all()
    serializer_class = SupportNotificationSerializer
    permission_classes = [IsAuthenticated, IsSupportOrAdmin]

    def get_queryset(self):
        """
        Restrict notifications to those relevant to the logged-in support staff.
        """
        if self.request.user.role == "support":
            return self.queryset.filter(support_staff__user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save()
        return Response({"message": "Notification created successfully."}, status=status.HTTP_201_CREATED)


class TicketAssignmentViewSet(viewsets.ModelViewSet):
    """
    Handles assignment of tickets to support staff.
    """
    queryset = TicketAssignment.objects.all()
    serializer_class = TicketAssignmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    def create(self, request, *args, **kwargs):
        """
        Assign a ticket to support staff.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.validated_data.get("ticket")
        support_staff = serializer.validated_data.get("assigned_to")
        TicketAssignment.assign_ticket(ticket, support_staff)
        return Response({"message": "Ticket assigned successfully."}, status=status.HTTP_201_CREATED)


class DisputeResolutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles retrieval of dispute resolution logs.
    """
    queryset = DisputeResolutionLog.objects.all()
    serializer_class = DisputeResolutionLogSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]