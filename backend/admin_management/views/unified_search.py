"""
Unified search view for searching across multiple entity types.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from admin_management.services.unified_search_service import UnifiedSearchService


class UnifiedSearchViewSet(viewsets.ViewSet):
    """
    Unified search endpoint for searching across orders, users, payments, and messages.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search across multiple entity types.
        
        Query parameters:
        - q: Search query (required, min 2 characters)
        - types: Comma-separated list of entity types to search (orders, users, payments, messages)
                 If not provided, searches all types
        - limit: Maximum results per entity type (default: 10)
        
        Example:
        GET /api/v1/admin-management/unified-search/search/?q=john&types=users,orders&limit=5
        """
        query = request.query_params.get('q', '').strip()
        
        if not query or len(query) < 2:
            return Response({
                'orders': [],
                'users': [],
                'payments': [],
                'messages': [],
                'total_results': 0,
                'query': query
            })
        
        # Parse entity types
        types_param = request.query_params.get('types', '')
        entity_types = None
        if types_param:
            entity_types = [t.strip() for t in types_param.split(',') if t.strip()]
            # Validate entity types
            valid_types = {'orders', 'users', 'payments', 'messages'}
            entity_types = [t for t in entity_types if t in valid_types]
            if not entity_types:
                entity_types = None
        
        # Parse limit
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = max(1, min(limit, 50))  # Clamp between 1 and 50
        except ValueError:
            limit = 10
        
        # Perform search
        results = UnifiedSearchService.search(
            query=query,
            user=request.user,
            entity_types=entity_types,
            limit_per_type=limit
        )
        
        results['query'] = query
        
        return Response(results)

