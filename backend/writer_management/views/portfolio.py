"""
Writer Portfolio ViewSets
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q

from writer_management.models.portfolio import WriterPortfolio, PortfolioSample
from writer_management.serializers.portfolio import (
    WriterPortfolioSerializer,
    WriterPortfolioUpdateSerializer,
    PortfolioSampleSerializer,
    PortfolioSampleCreateSerializer,
)


class WriterPortfolioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer portfolios.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WriterPortfolioSerializer
    
    def get_queryset(self):
        """Get portfolios based on visibility and user role."""
        user = self.request.user
        website = user.website
        
        if user.role == 'writer':
            # Writers see their own portfolio
            return WriterPortfolio.objects.filter(
                writer=user,
                website=website
            )
        elif user.role == 'client':
            # Clients see enabled portfolios they can view
            return WriterPortfolio.objects.filter(
                website=website,
                is_enabled=True,
                visibility__in=['clients_only', 'public']
            )
        else:
            # Admins see all
            return WriterPortfolio.objects.filter(website=website)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return WriterPortfolioUpdateSerializer
        return WriterPortfolioSerializer
    
    def get_permissions(self):
        """Allow public access for retrieve if portfolio is public."""
        if self.action == 'retrieve':
            # Check if portfolio is public
            try:
                portfolio = WriterPortfolio.objects.get(pk=self.kwargs.get('pk'))
                if portfolio.is_enabled and portfolio.visibility == 'public':
                    return [AllowAny()]
            except WriterPortfolio.DoesNotExist:
                pass
        
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Create portfolio for current user."""
        serializer.save(
            writer=self.request.user,
            website=self.request.user.website
        )
    
    @action(detail=False, methods=['get'], url_path='my-portfolio')
    def my_portfolio(self, request):
        """Get current user's portfolio."""
        if request.user.role != 'writer':
            return Response(
                {'error': 'Only writers can have portfolios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            portfolio = WriterPortfolio.objects.get(
                writer=request.user,
                website=request.user.website
            )
            serializer = self.get_serializer(portfolio)
            return Response(serializer.data)
        except WriterPortfolio.DoesNotExist:
            return Response(
                {'message': 'Portfolio not created yet'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], url_path='update-statistics')
    def update_statistics(self, request, pk=None):
        """Manually update portfolio statistics."""
        portfolio = self.get_object()
        
        if portfolio.writer != request.user and request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        portfolio.update_statistics()
        serializer = self.get_serializer(portfolio)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='public-view')
    def public_view(self, request, pk=None):
        """Public view of portfolio (no auth required for public portfolios)."""
        portfolio = self.get_object()
        
        if not portfolio.is_enabled:
            return Response(
                {'error': 'Portfolio is not enabled'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check visibility
        if portfolio.visibility == 'private':
            return Response(
                {'error': 'Portfolio is private'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Return limited data for public view
        serializer = self.get_serializer(portfolio)
        data = serializer.data
        
        # Remove sensitive information
        if not portfolio.show_contact_info:
            data.pop('writer_email', None)
        if not portfolio.show_order_history:
            data.pop('total_orders_completed', None)
        if not portfolio.show_earnings:
            data.pop('average_rating', None)
        
        return Response(data)


class PortfolioSampleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing portfolio samples.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioSampleSerializer
    
    def get_queryset(self):
        """Get portfolio samples."""
        user = self.request.user
        website = user.website
        
        if user.role == 'writer':
            # Writers see their own samples
            return PortfolioSample.objects.filter(
                writer=user,
                website=website
            )
        elif user.role == 'client':
            # Clients see featured samples from enabled portfolios
            return PortfolioSample.objects.filter(
                website=website,
                is_featured=True,
                writer__portfolio__is_enabled=True,
                writer__portfolio__visibility__in=['clients_only', 'public']
            )
        else:
            # Admins see all
            return PortfolioSample.objects.filter(website=website)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PortfolioSampleCreateSerializer
        return PortfolioSampleSerializer
    
    def perform_create(self, serializer):
        """Create sample for current user."""
        serializer.save(
            writer=self.request.user,
            website=self.request.user.website
        )
    
    @action(detail=True, methods=['post'], url_path='toggle-featured')
    def toggle_featured(self, request, pk=None):
        """Toggle featured status of sample."""
        sample = self.get_object()
        
        if sample.writer != request.user and request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        sample.is_featured = not sample.is_featured
        sample.save(update_fields=['is_featured'])
        
        serializer = self.get_serializer(sample)
        return Response(serializer.data)

