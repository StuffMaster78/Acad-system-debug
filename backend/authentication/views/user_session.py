from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authentication.models import UserSession
from authentication.serializers import UserSessionSerializer
from websites.models import Website  # or your actual path
from django.utils.timezone import now
from rest_framework.decorators import action

class UserSessionViewSet(mixins.ListModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    Allows users to list and terminate their active sessions.
    """

    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        website = self.request.user.website  # assumes user is tied to website
        # Add ordering to prevent UnorderedObjectListWarning
        return UserSession.objects.filter(
            user=self.request.user,
            website=website,
            is_active=True
        ).order_by('-last_activity')

    def destroy(self, request, *args, **kwargs):
        """
        Terminates the session explicitly.
        """
        instance = self.get_object()
        instance.terminate()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'], url_path='terminate-others')
    def terminate_other_sessions(self, request):
        """
        Terminates all active sessions for the user except the current one.
        """
        current_session_key = request.session.session_key
        sessions = self.get_queryset().filter(is_active=True).exclude(session_key=current_session_key)

        for session in sessions:
            session.terminate()

        return Response({
            "detail": "Other sessions terminated successfully."
        }, status=status.HTTP_200_OK)