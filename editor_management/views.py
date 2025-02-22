from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (
    EditorProfile,
    EditorTaskAssignment,
    EditorPerformance,
    EditorNotification,
)
from .serializers import (
    EditorProfileSerializer,
    EditorTaskAssignmentSerializer,
    EditorPerformanceSerializer,
    EditorNotificationSerializer,
)
from .permissions import IsEditor


class EditorProfileDetailView(generics.RetrieveAPIView):
    """
    View for retrieving editor profile details.
    """
    queryset = EditorProfile.objects.all()
    serializer_class = EditorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]


class EditorTaskListView(generics.ListAPIView):
    """
    List tasks assigned to an editor.
    """
    serializer_class = EditorTaskAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def get_queryset(self):
        return EditorTaskAssignment.objects.filter(
            assigned_editor=self.request.user.editor_profile
        )


class EditorPerformanceView(generics.RetrieveAPIView):
    """
    View for retrieving editor performance details.
    """
    queryset = EditorPerformance.objects.all()
    serializer_class = EditorPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def get_object(self):
        return self.request.user.editor_profile.performance


class EditorNotificationsView(generics.ListAPIView):
    """
    List notifications for the editor.
    """
    serializer_class = EditorNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def get_queryset(self):
        return EditorNotification.objects.filter(editor=self.request.user.editor_profile)