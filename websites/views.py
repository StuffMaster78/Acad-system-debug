from rest_framework import viewsets
from .models import Website
from .serializers import WebsiteSerializer
from rest_framework.permissions import IsAuthenticated

class WebsiteViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing websites.
    """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter websites by the current user's association.
        """
        user = self.request.user
        if user.is_staff:  # Admin or superuser can view all websites
            return Website.objects.all()
        return Website.objects.filter(is_active=True)