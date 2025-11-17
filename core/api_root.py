"""
API Root View - Provides information about available endpoints.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint providing information about available endpoints.
    """
    return Response({
        'message': 'Writing System API v1',
        'version': '1.0.0',
        'documentation': {
            'swagger': '/api/v1/docs/swagger/',
            'redoc': '/api/v1/docs/redoc/',
            'schema': '/api/v1/schema/',
        },
        'authentication': {
            'login': '/api/v1/auth/login/',
            'token_refresh': '/api/v1/auth/refresh-token/',
            'method': 'JWT Bearer Token',
        },
        'endpoints': {
            'auth': '/api/v1/auth/',
            'users': '/api/v1/users/',
            'orders': '/api/v1/orders/',
            'websites': '/api/v1/websites/',
            'discounts': '/api/v1/discounts/',
            'client_management': '/api/v1/client-management/',
            'writer_management': '/api/v1/writer-management/',
            'support_management': '/api/v1/support-management/',
            'editor_management': '/api/v1/editor-management/',
            'admin_management': '/api/v1/admin-management/',
            'superadmin_management': '/api/v1/superadmin-management/',
            'notifications': '/api/v1/notifications/',
            'communications': '/api/v1/order-communications/',
            'tickets': '/api/v1/tickets/',
            'wallet': '/api/v1/wallet/',
            'fines': '/api/v1/fines/',
            'blog_pages': '/api/v1/blog_pages_management/',
            'service_pages': '/api/v1/service-pages/',
            'dropdown_options': '/api/v1/dropdown-options/',
        },
        'status': 'operational'
    })

