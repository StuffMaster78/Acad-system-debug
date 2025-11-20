from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from writer_management.models.levels import WriterLevel
from writer_management.serializers import WriterLevelSerializer


class WriterLevelViewSet(viewsets.ModelViewSet):
    """
    Manage WriterLevel definitions (templates/configurations).
    Admin-only endpoint for managing level configurations.
    """
    queryset = WriterLevel.objects.select_related("website").prefetch_related("writers")
    serializer_class = WriterLevelSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['website', 'is_active', 'earning_mode']
    search_fields = ['name', 'description']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                qs = qs.filter(website=website)
        return qs
    
    def create(self, request, *args, **kwargs):
        """
        Create a new writer level.
        Automatically sets website if not provided (for non-superadmin users).
        """
        # Make a mutable copy of request.data
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # If website is not provided and user is not superadmin, set it from user's website
        if 'website' not in data and request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                data['website'] = website.id
            else:
                return Response(
                    {"detail": "Website is required. Please select a website."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate that website is provided
        if 'website' not in data:
            return Response(
                {"detail": "Website field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new request with modified data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as e:
            # Handle unique constraint violation (website + name)
            if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                return Response(
                    {
                        "detail": "A writer level with this name already exists for the selected website.",
                        "error": "A level with the same name already exists for this website. Please choose a different name."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"detail": f"Database error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import traceback
            return Response(
                {
                    "detail": f"Error creating writer level: {str(e)}",
                    "error_details": traceback.format_exc() if hasattr(e, '__traceback__') else None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def calculate_sample_earnings(self, request, pk=None):
        """
        Calculate sample earnings for a level with example order.
        Helps admins understand earnings before saving.
        """
        from writer_management.services.earnings_calculator import WriterEarningsCalculator
        from decimal import Decimal
        
        level = self.get_object()
        pages = int(request.data.get('pages', 10))
        slides = int(request.data.get('slides', 0))
        order_total = request.data.get('order_total')
        order_cost = request.data.get('order_cost')
        is_urgent = request.data.get('is_urgent', False)
        is_technical = request.data.get('is_technical', False)
        
        order_total_decimal = Decimal(str(order_total)) if order_total else None
        order_cost_decimal = Decimal(str(order_cost)) if order_cost else None
        
        breakdown = WriterEarningsCalculator.calculate_estimated_earnings(
            level,
            pages=pages,
            slides=slides,
            order_total=order_total_decimal,
            order_cost=order_cost_decimal,
            is_urgent=is_urgent,
            is_technical=is_technical
        )
        
        return Response({
            'earnings': breakdown,
            'level_name': level.name,
            'earning_mode': level.earning_mode,
        })
    
    @action(detail=True, methods=['get'])
    def progression_stats(self, request, pk=None):
        """
        Get statistics on how many writers are eligible for this level.
        """
        from writer_management.services.level_progression import WriterLevelProgressionService
        from writer_management.models.profile import WriterProfile
        
        level = self.get_object()
        
        # Get all writers for this website
        writers = WriterProfile.objects.filter(website=level.website)
        
        eligible_count = 0
        ineligible_count = 0
        sample_failures = []
        
        for writer in writers[:100]:  # Limit to first 100 for performance
            is_eligible, failed = WriterLevelProgressionService.check_level_eligibility(writer, level)
            if is_eligible:
                eligible_count += 1
            else:
                ineligible_count += 1
                if len(sample_failures) < 5:  # Store first 5 failure examples
                    sample_failures.append({
                        'writer_id': writer.id,
                        'writer_username': writer.user.username,
                        'failed_requirements': failed[:3],  # First 3 failures
                    })
        
        return Response({
            'level': {
                'id': level.id,
                'name': level.name,
            },
            'statistics': {
                'eligible_writers': eligible_count,
                'ineligible_writers': ineligible_count,
                'total_checked': eligible_count + ineligible_count,
            },
            'sample_failures': sample_failures,
        })

