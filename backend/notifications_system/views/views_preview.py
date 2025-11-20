# notifications_system/api/views_preview.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from notifications_system.registry.template_registry import get_template
from ..serializers import PreviewRequestSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class NotificationTemplatePreviewView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        ser = PreviewRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        event = ser.validated_data["event"]
        payload = ser.validated_data["payload"] or {}

        tmpl = get_template(event)
        if not tmpl:
            return Response(
                {"detail": f"No template registered for '{event}'"},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            title, text_msg, html_msg = tmpl.render(payload)
            return Response(
                {
                    "event": event,
                    "title": title,
                    "text": text_msg,
                    "html": html_msg,
                },
                status=200
            )
        except Exception as exc:
            return Response(
                {"detail": f"Render failed: {exc}"},
                status=status.HTTP_400_BAD_REQUEST
            )