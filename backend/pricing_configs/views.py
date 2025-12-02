from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .models import (
    PricingConfiguration, AdditionalService, AcademicLevelPricing,
    TypeOfWorkMultiplier, DeadlineMultiplier, PreferredWriterConfig,
    WriterLevelOptionConfig,
)
from .serializers import (
    PricingConfigurationSerializer, AdditionalServiceSerializer,
    AcademicLevelPricingSerializer, TypeOfWorkMultiplierSerializer,
    DeadlineMultiplierSerializer, PreferredWriterConfigSerializer,
    PriceEstimationInputSerializer, WriterLevelOptionConfigSerializer,
    PricingCalculatorSessionSerializer,
)
from .permissions import IsAdminUserOrReadOnly, IsAdminOfWebsite
from pricing_configs.services.price_estimation_service import (
    PricingEstimationService
)
from .mixins import WebsiteScopedViewSetMixin
from pricing.models.calculator_session import PricingCalculatorSession

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


class PricingCalculatorSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing pricing calculator sessions.
    Allows anonymous users to save pricing calculations.
    """
    serializer_class = PricingCalculatorSessionSerializer
    permission_classes = [AllowAny]  # Allow anonymous users
    
    def get_queryset(self):
        """Filter queryset based on user authentication."""
        user = self.request.user
        
        if user.is_authenticated:
            # Authenticated users can see their own sessions
            return PricingCalculatorSession.objects.filter(user=user)
        else:
            # Anonymous users can only see sessions with their session key
            session_key = self.request.session.session_key
            if session_key:
                return PricingCalculatorSession.objects.filter(session_key=session_key)
            return PricingCalculatorSession.objects.none()
    
    def get_permissions(self):
        """Override permissions for specific actions."""
        if self.action in ['create', 'calculate', 'save_session']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate(self, request):
        """
        Calculate pricing and optionally save the session.
        """
        from orders.services.pricing_calculator import PricingCalculatorService
        
        order_data = request.data.get('order_data', {})
        discount_code = request.data.get('discount_code', '')
        save_session = request.data.get('save_session', False)
        
        try:
            # Calculate pricing
            calculator = PricingCalculatorService()
            pricing_result = calculator.calculate_price(
                order_data=order_data,
                discount_code=discount_code if discount_code else None
            )
            
            # Save session if requested
            session = None
            if save_session:
                session_key = request.session.session_key or request.data.get('session_key', '')
                user = request.user if request.user.is_authenticated else None
                
                session = PricingCalculatorSession.create_session(
                    session_key=session_key,
                    order_data=order_data,
                    pricing_result=pricing_result,
                    user=user,
                    discount_code=discount_code
                )
            
            response_data = {
                'pricing': pricing_result,
                'session_id': session.id if session else None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='save-session')
    def save_session(self, request):
        """Save a pricing calculation session."""
        order_data = request.data.get('order_data', {})
        pricing_result = request.data.get('pricing_result', {})
        discount_code = request.data.get('discount_code', '')
        
        session_key = request.session.session_key or request.data.get('session_key', '')
        user = request.user if request.user.is_authenticated else None
        
        try:
            session = PricingCalculatorSession.create_session(
                session_key=session_key,
                order_data=order_data,
                pricing_result=pricing_result,
                user=user,
                discount_code=discount_code
            )
            
            serializer = self.get_serializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='active-session')
    def active_session(self, request):
        """Get the active (non-expired, non-converted) session for the current user/session."""
        session_key = request.session.session_key or request.GET.get('session_key', '')
        user = request.user if request.user.is_authenticated else None
        
        session = PricingCalculatorSession.get_active_session(session_key, user)
        
        if session:
            serializer = self.get_serializer(session)
            return Response(serializer.data)
        else:
            return Response({'detail': 'No active session found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='convert-to-order')
    def convert_to_order(self, request, pk=None):
        """Convert a pricing session to an actual order."""
        session = self.get_object()
        
        if session.converted_to_order:
            return Response(
                {'error': 'Session already converted to order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order from session data
        # This would integrate with your order creation logic
        order_data = session.order_data
        
        # For now, just mark as converted
        # In production, you'd create the actual order here
        order_id = request.data.get('order_id')  # Assuming order is created elsewhere
        
        if order_id:
            session.mark_as_converted(order_id)
            serializer = self.get_serializer(session)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'order_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )


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