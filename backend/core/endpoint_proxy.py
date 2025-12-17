"""
API Endpoint Proxy
Masks actual API endpoints from writers and clients by routing through a proxy.
This provides security through obscurity and prevents users from discovering
admin/internal endpoints.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpRequest, Http404
from django.urls import resolve, Resolver404, reverse
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


# Role-based endpoint routing
# Maps masked endpoints to actual endpoints
ENDPOINT_ROUTES = {
    'client': {
        '/client/orders/': '/api/v1/orders/orders/',
        '/client/payments/': '/api/v1/order-payments/order-payments/client-payments/',
        '/client/invoices/': '/api/v1/invoices/client-invoices/',
        '/client/referrals/code/': '/api/v1/referrals/referral-codes/my-code/',
        '/client/referrals/stats/': '/api/v1/referrals/referrals/stats/',
        '/client/profile/': '/api/v1/users/users/profile/',
        '/client/support/': '/api/v1/support-management/tickets/',
        '/client/notifications/': '/api/v1/notifications_system/notifications/feed/',
    },
    'writer': {
        '/writer/orders/': '/api/v1/writer-management/writer-orders/',
        '/writer/requests/': '/api/v1/writer-management/writer-order-requests/',
        '/writer/takes/': '/api/v1/writer-management/writer-order-takes/',
        '/writer/payments/': '/api/v1/writer-management/writer-payments/',
        '/writer/wallet/': '/api/v1/writer-wallet/writer-payments/',
        '/writer/performance/': '/api/v1/writer-management/writer-performance/',
        '/writer/dashboard/': '/api/v1/writer-management/writer-dashboard/',
        '/writer/hold-requests/': '/api/v1/writer-management/writer-order-hold-requests/',
        '/writer/extensions/': '/api/v1/writer-management/writer-deadline-extension-requests/',
        '/writer/profile/': '/api/v1/writer-management/writer-profiles/me/',
        '/writer/support/': '/api/v1/support-management/tickets/',
    },
}


def get_user_role(user):
    """Get user role string"""
    if not user or not user.is_authenticated:
        return None
    return getattr(user, 'role', None)


def route_endpoint(masked_path, user_role, method='GET', data=None, params=None):
    """
    Route a masked endpoint to its actual endpoint.
    
    Args:
        masked_path: The masked endpoint path (e.g., '/client/orders/')
        user_role: User's role ('client', 'writer', 'admin', 'superadmin')
        method: HTTP method
        data: Request body data
        params: Query parameters
    
    Returns:
        tuple: (actual_endpoint, allowed) - actual endpoint path and whether access is allowed
    """
    # Admins and superadmins bypass proxy and use actual endpoints
    if user_role in ['admin', 'superadmin']:
        return masked_path, True
    
    # Get routes for this role
    routes = ENDPOINT_ROUTES.get(user_role, {})
    
    # Try to find matching route
    for masked, actual in routes.items():
        if masked_path.startswith(masked):
            remaining = masked_path[len(masked):]
            return actual + remaining, True
    
    # Check if it's a restricted endpoint
    if '/restricted/' in masked_path or '/blocked/' in masked_path:
        return None, False
    
    # If no route found and it's not an admin endpoint, allow passthrough
    # (for endpoints not in mapping, let them through)
    if not any(admin_path in masked_path for admin_path in ['/admin-management/', '/superadmin-management/']):
        return masked_path, True
    
    # Admin endpoints are blocked for non-admins
    return None, False


def make_internal_request(request: HttpRequest, actual_path: str):
    """
    Make an internal request to the actual endpoint using DRF's APIClient.
    This preserves JWT authentication and headers while making the request internally.
    """
    from rest_framework.test import APIClient
    
    # Create an API client (better for JWT authentication)
    client = APIClient()
    
    # Copy authentication headers from original request
    if hasattr(request, 'META'):
        # Copy Authorization header (JWT token)
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            client.credentials(HTTP_AUTHORIZATION=auth_header)
        
        # Copy website header if present
        website_header = request.META.get('HTTP_X_WEBSITE')
        if website_header:
            client.credentials(HTTP_X_WEBSITE=website_header)
    
    # Also set user directly if available (for additional context)
    if hasattr(request, 'user') and request.user.is_authenticated:
        client.force_authenticate(user=request.user)
    
    # Prepare query parameters
    query_params = dict(request.GET)
    
    # Prepare request data
    data = None
    format_type = 'json'  # DRF APIClient uses 'format' parameter
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        if hasattr(request, 'data'):
            data = request.data
        elif hasattr(request, 'body') and request.body:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                # If not JSON, pass as raw data
                data = request.body
                format_type = 'multipart'  # or 'json' depending on content
    
    # Build the full URL path (ensure it starts with /api/v1/)
    if not actual_path.startswith('/'):
        actual_path = '/' + actual_path
    
    # Ensure it has the /api/v1/ prefix if it's an API endpoint
    if not actual_path.startswith('/api/v1/'):
        if actual_path.startswith('/api/'):
            # Already has /api/, just ensure /v1/
            if not actual_path.startswith('/api/v1/'):
                actual_path = '/api/v1' + actual_path[4:]
        else:
            # Add /api/v1/ prefix
            actual_path = '/api/v1' + actual_path
    
    # DRF APIClient needs the path without /api/v1/ prefix for internal routing
    # Extract the path after /api/v1/
    internal_path = actual_path
    if actual_path.startswith('/api/v1/'):
        internal_path = actual_path[8:]  # Remove '/api/v1/' prefix
    
    # Make the internal request using DRF APIClient
    try:
        if request.method == 'GET':
            response = client.get(internal_path, query_params, format=format_type)
        elif request.method == 'POST':
            response = client.post(internal_path, data, format=format_type)
        elif request.method == 'PUT':
            response = client.put(internal_path, data, format=format_type)
        elif request.method == 'PATCH':
            response = client.patch(internal_path, data, format=format_type)
        elif request.method == 'DELETE':
            response = client.delete(internal_path, format=format_type)
        else:
            return Response(
                {'error': f'Method {request.method} not supported'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        
        # Extract response data (DRF responses already have .data)
        response_data = response.data if hasattr(response, 'data') else {}
        
        # If response.data is empty but there's content, try to parse it
        if not response_data and response.content:
            try:
                response_data = json.loads(response.content)
            except (json.JSONDecodeError, AttributeError):
                response_data = {'content': response.content.decode('utf-8') if hasattr(response.content, 'decode') else str(response.content)}
        
        # Return the proxied response
        return Response(
            response_data,
            status=response.status_code
        )
        
    except Resolver404:
        logger.warning(f'Proxy: Resolver404 for path: {internal_path} (original: {actual_path})')
        return Response(
            {'error': f'Endpoint not found: {internal_path}', 'original_path': actual_path},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f'Error proxying request to {internal_path} (original: {actual_path}): {str(e)}', exc_info=True)
        return Response(
            {'error': 'Internal proxy error', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def endpoint_proxy(request, masked_path=''):
    """
    Proxy endpoint that routes masked endpoints to actual endpoints.
    
    Usage:
        GET /api/v1/proxy/client/orders/ -> GET /api/v1/orders/orders/
        POST /api/v1/proxy/writer/orders/ -> POST /api/v1/writer-management/writer-orders/
    """
    user = request.user
    user_role = get_user_role(user)
    
    if not user_role:
        return Response(
            {'error': 'User role not found'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Normalize the masked path
    if not masked_path.startswith('/'):
        masked_path = '/' + masked_path
    
    # Route the endpoint
    actual_path, allowed = route_endpoint(
        masked_path,
        user_role,
        method=request.method,
        data=request.data if hasattr(request, 'data') else None,
        params=request.query_params
    )
    
    logger.debug(f'Proxy: masked_path={masked_path}, user_role={user_role}, actual_path={actual_path}, allowed={allowed}')
    
    if not allowed:
        logger.warning(f'Proxy: Access denied for {user_role} to {masked_path}')
        return Response(
            {'error': 'Access denied. This endpoint is not available for your role.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if not actual_path:
        logger.warning(f'Proxy: No actual path found for masked_path={masked_path}, user_role={user_role}')
        return Response(
            {'error': 'Endpoint not found', 'masked_path': masked_path, 'user_role': user_role},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Make internal request to actual endpoint
    return make_internal_request(request, actual_path)

