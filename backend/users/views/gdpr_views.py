"""
GDPR Views - API endpoints for GDPR compliance.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.services.gdpr_service import GDPRService
from websites.utils import get_current_website
from authentication.utils.ip import get_client_ip


class GDPRViewSet(viewsets.ViewSet):
    """
    ViewSet for GDPR compliance endpoints.
    Implements all GDPR rights.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='export-data')
    def export_data(self, request):
        """
        Article 15: Right of Access - Export all user data.
        
        Query params:
        - format: Export format (json, csv, xml) - default: json
        """
        user = request.user
        website = get_current_website(request)
        format_type = request.query_params.get('format', 'json')
        
        service = GDPRService(user=user, website=website)
        export_data = service.export_all_data(format=format_type)
        
        return Response(export_data)
    
    @action(detail=False, methods=['post'], url_path='request-correction')
    def request_correction(self, request):
        """
        Article 16: Right to Rectification - Request data correction.
        
        Request body:
        {
            "corrections": {
                "email": "new@email.com",
                "first_name": "New Name"
            }
        }
        """
        user = request.user
        website = get_current_website(request)
        
        corrections = request.data.get('corrections', {})
        if not corrections:
            return Response(
                {"error": "No corrections provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GDPRService(user=user, website=website)
        result = service.request_data_correction(corrections)
        
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='request-deletion')
    def request_deletion(self, request):
        """
        Article 17: Right to Erasure - Request account deletion.
        
        Request body:
        {
            "reason": "Optional reason for deletion"
        }
        """
        user = request.user
        website = get_current_website(request)
        
        reason = request.data.get('reason')
        
        service = GDPRService(user=user, website=website)
        result = service.request_account_deletion(reason=reason)
        
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='restrict-processing')
    def restrict_processing(self, request):
        """
        Article 18: Right to Restriction of Processing.
        
        Request body:
        {
            "reason": "Optional reason for restriction"
        }
        """
        user = request.user
        website = get_current_website(request)
        
        reason = request.data.get('reason')
        
        service = GDPRService(user=user, website=website)
        result = service.restrict_processing(reason=reason)
        
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='lift-restriction')
    def lift_restriction(self, request):
        """Lift processing restriction."""
        user = request.user
        website = get_current_website(request)
        
        service = GDPRService(user=user, website=website)
        result = service.lift_processing_restriction()
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='export-portable')
    def export_portable(self, request):
        """
        Article 20: Right to Data Portability.
        
        Query params:
        - format: Export format (json) - default: json
        """
        user = request.user
        website = get_current_website(request)
        format_type = request.query_params.get('format', 'json')
        
        service = GDPRService(user=user, website=website)
        export_data = service.export_portable_data(format=format_type)
        
        return Response(export_data)
    
    @action(detail=False, methods=['post'], url_path='object-processing')
    def object_processing(self, request):
        """
        Article 21: Right to Object.
        
        Request body:
        {
            "processing_type": "marketing|analytics|profiling|all",
            "reason": "Optional reason"
        }
        """
        user = request.user
        website = get_current_website(request)
        
        processing_type = request.data.get('processing_type')
        if not processing_type:
            return Response(
                {"error": "processing_type is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason')
        
        service = GDPRService(user=user, website=website)
        result = service.object_to_processing(processing_type, reason=reason)
        
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='record-consent')
    def record_consent(self, request):
        """
        Article 7: Record Consent.
        
        Request body:
        {
            "consent_type": "analytics|marketing|third_party",
            "consented": true,
            "purpose": "Optional purpose"
        }
        """
        user = request.user
        website = get_current_website(request)
        
        consent_type = request.data.get('consent_type')
        consented = request.data.get('consented', False)
        purpose = request.data.get('purpose')
        
        if not consent_type:
            return Response(
                {"error": "consent_type is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GDPRService(user=user, website=website)
        result = service.record_consent(consent_type, consented, purpose)
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='consent-status')
    def consent_status(self, request):
        """Get current consent status."""
        user = request.user
        website = get_current_website(request)
        
        service = GDPRService(user=user, website=website)
        status_data = service.get_consent_status()
        
        return Response(status_data)
    
    @action(detail=False, methods=['get'], url_path='summary')
    def gdpr_summary(self, request):
        """Get GDPR summary for user."""
        user = request.user
        website = get_current_website(request)
        
        service = GDPRService(user=user, website=website)
        summary = service.get_gdpr_summary()
        
        return Response(summary)

