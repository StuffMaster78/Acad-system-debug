from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import PricingConfiguration, AdditionalService, WriterQuality
from .serializers import PricingConfigurationSerializer, AdditionalServiceSerializer, WriterQualitySerializer
from .permissions import IsAdminUserOrReadOnly, IsAdminOfWebsite

class PricingConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing PricingConfiguration.
    """
    queryset = PricingConfiguration.objects.all()
    serializer_class = PricingConfigurationSerializer
    permission_classes = [IsAdminUser, IsAdminUserOrReadOnly, IsAdminOfWebsite]  # Only admins can manage pricing configurations

    def perform_create(self, serializer):
        # Automatically associate the website of the logged-in admin user
        serializer.save(website=self.request.user.website)


class AdditionalServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AdditionalService.
    """
    queryset = AdditionalService.objects.filter(is_active=True)  # Only return active services by default
    serializer_class = AdditionalServiceSerializer
    permission_classes = [IsAdminUser, IsAdminUserOrReadOnly, IsAdminOfWebsite]

    def perform_create(self, serializer):
        # Automatically associate the website of the logged-in admin user
        serializer.save(website=self.request.user.website)


class WriterQualityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing WriterQuality.
    """
    queryset = WriterQuality.objects.all()
    serializer_class = WriterQualitySerializer
    permission_classes = [IsAdminUserOrReadOnly, IsAdminOfWebsite]

    def perform_create(self, serializer):
        serializer.save(website=self.request.user.website)