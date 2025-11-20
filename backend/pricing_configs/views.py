from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import (
    PricingConfiguration, AdditionalService, AcademicLevelPricing,
    TypeOfWorkMultiplier, DeadlineMultiplier, PreferredWriterConfig,
    WriterLevelOptionConfig
)
from .serializers import (
    PricingConfigurationSerializer, AdditionalServiceSerializer,
    AcademicLevelPricingSerializer, TypeOfWorkMultiplierSerializer,
    DeadlineMultiplierSerializer, PreferredWriterConfigSerializer,
    PriceEstimationInputSerializer, WriterLevelOptionConfigSerializer
)
from .permissions import IsAdminUserOrReadOnly, IsAdminOfWebsite
from rest_framework.permissions import AllowAny
from pricing_configs.services.price_estimation_service import (
    PricingEstimationService
)
from .mixins import WebsiteScopedViewSetMixin

class PricingConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing PricingConfiguration.
    """
    queryset = PricingConfiguration.objects.all()
    serializer_class = PricingConfigurationSerializer
    permission_classes = [
        IsAdminUser, IsAdminUserOrReadOnly, IsAdminOfWebsite
    ] 

    def perform_create(self, serializer):
        # Automatically associate the website of the logged-in admin user
        serializer.save(website=self.request.user.website)


class AdditionalServiceViewSet(WebsiteScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing AdditionalService.
    """
    queryset = AdditionalService.objects.filter(is_active=True)  # Only return active services by default
    serializer_class = AdditionalServiceSerializer
    permission_classes = [
        IsAdminUser, IsAdminUserOrReadOnly, IsAdminOfWebsite
    ]

    def perform_create(self, serializer):
        # Automatically associate the website of the logged-in admin user
        serializer.save(website=self.request.user.website)


class AcademicLevelPricingViewSet(WebsiteScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = AcademicLevelPricing.objects.all()
    serializer_class = AcademicLevelPricingSerializer

    def perform_create(self, serializer):
        serializer.save(website=self.request.user.website)  # Assign website dynamically


class TypeOfWorkMultiplierViewSet(WebsiteScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing TypeOfWorkMultiplier.
    """
    queryset = TypeOfWorkMultiplier.objects.all()
    serializer_class = TypeOfWorkMultiplierSerializer
    permission_classes = [IsAdminUser, IsAdminUserOrReadOnly, IsAdminOfWebsite]

    def perform_create(self, serializer):
        serializer.save(website=self.request.user.website)  # Assign website dynamically

class DeadlineMultiplierViewSet(WebsiteScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing DeadlineMultiplier.
    """
    queryset = DeadlineMultiplier.objects.all()
    serializer_class = DeadlineMultiplierSerializer
    permission_classes = [IsAdminUser, IsAdminUserOrReadOnly, IsAdminOfWebsite]

    def perform_create(self, serializer):
        serializer.save(website=self.request.user.website)  # Assign website dynamically
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def options(self, request):
        """
        Get available deadline multiplier options for the current website.
        Useful for frontend deadline selection.
        """
        from pricing_configs.services.deadline_multiplier_service import DeadlineMultiplierService
        from .utils import get_website_from_request
        
        website = get_website_from_request(request)
        if not website:
            return Response(
                {"detail": "Website not recognized."},
                status=400
            )
        
        options = DeadlineMultiplierService.get_available_options(website)
        return Response({
            'options': options,
            'website': {
                'id': website.id,
                'name': website.name,
                'domain': website.domain
            }
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recommended(self, request):
        """
        Get recommended default deadline multiplier configurations.
        Useful for initial setup.
        """
        from pricing_configs.services.deadline_multiplier_service import DeadlineMultiplierService
        
        recommended = DeadlineMultiplierService.get_recommended_multipliers()
        return Response({
            'recommended': [
                {
                    'label': r['label'],
                    'hours': r['hours'],
                    'multiplier': float(r['multiplier'])
                }
                for r in recommended
            ]
        })

class PreferredWriterConfigViewSet(WebsiteScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing PreferredWriterConfig.
    """
    queryset = PreferredWriterConfig.objects.all()
    serializer_class = PreferredWriterConfigSerializer
    permission_classes = [IsAdminUser, IsAdminUserOrReadOnly, IsAdminOfWebsite]

    def perform_create(self, serializer):
        serializer.save(website=self.request.user.website)  # Assign website dynamically


class WriterLevelOptionConfigViewSet(WebsiteScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing WriterLevelOptionConfig.
    """
    queryset = WriterLevelOptionConfig.objects.all()
    serializer_class = WriterLevelOptionConfigSerializer
    permission_classes = [IsAdminUser, IsAdminUserOrReadOnly, IsAdminOfWebsite]

    def perform_create(self, serializer):
        serializer.save(website=self.request.user.website)  # Assign website dynamically    

class EstimatePriceView(APIView):
    """
    Public API to estimate pricing based on order inputs.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PriceEstimationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_data = serializer.validated_data

        website = get_website_from_request(request)
        if not website:
            return Response(
                {"detail": "Website not recognized."},
                status=400
            )
        
        input_data["website"] = website

        estimate = PricingEstimationService.calculate(input_data)
        return Response(estimate)