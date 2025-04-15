from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from authentication.models.sessions import UserSession
from authentication.serializers import UserSessionSerializer

class ActiveSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve active sessions for the authenticated user."""
        sessions = UserSession.objects.filter(user=request.user)
        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        """Log out a specific session by session_id."""
        session = get_object_or_404(UserSession, id=session_id, user=request.user)

        if session.session_key == request.session.session_key:
            return Response(
                {"error": "You can't log out of your current session."},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.delete()
        return Response({"message": "Session logged out successfully."}, status=status.HTTP_200_OK)


class LogoutAllSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Log out all sessions except the current one."""
        UserSession.objects.filter(user=request.user).exclude(
            session_key=request.session.session_key
        ).delete()
        return Response({"message": "All other sessions have been logged out."}, status=status.HTTP_200_OK)