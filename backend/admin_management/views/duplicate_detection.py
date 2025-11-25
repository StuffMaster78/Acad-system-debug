"""
API views for duplicate account detection.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from admin_management.permissions import IsAdmin, IsSuperAdmin
from admin_management.services.duplicate_detection import DuplicateAccountDetectionService
from admin_management.serializers import UserSerializer

User = get_user_model()


class DuplicateAccountDetectionViewSet(viewsets.ViewSet):
    """
    ViewSet for detecting and managing suspected duplicate accounts.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'])
    def detect(self, request):
        """
        Detect suspected duplicate accounts.
        
        Query params:
        - role: Filter by 'client' or 'writer'
        - min_confidence: 'low', 'medium', or 'high'
        - limit: Maximum number of results (default: 100)
        """
        role_filter = request.query_params.get('role')
        min_confidence = request.query_params.get('min_confidence', 'low')
        limit = int(request.query_params.get('limit', 100))
        
        try:
            duplicates = DuplicateAccountDetectionService.detect_all(
                role_filter=role_filter,
                min_confidence=min_confidence
            )
            
            # Limit results
            duplicates = duplicates[:limit]
            
            # Serialize results
            results = []
            for dup in duplicates:
                user_data = []
                for user in dup['users']:
                    user_data.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                        'website': {
                            'id': user.website.id if user.website else None,
                            'name': user.website.name if user.website else None,
                        } if user.website else None,
                        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'is_active': user.is_active,
                        'is_suspended': user.is_suspended,
                        'is_blacklisted': user.is_blacklisted,
                    })
                
                # Handle websites - they might be IDs or objects
                website_data = []
                for w in dup.get('websites', []):
                    if w:
                        if isinstance(w, int):
                            from websites.models import Website
                            try:
                                website_obj = Website.objects.get(id=w)
                                website_data.append({'id': website_obj.id, 'name': website_obj.name})
                            except:
                                pass
                        else:
                            website_data.append({'id': w.id, 'name': w.name})
                
                results.append({
                    'user_ids': dup['user_ids'],
                    'users': user_data,
                    'websites': website_data,
                    'signals': dup['signals'],
                    'detection_types': dup['detection_types'],
                    'confidence': dup['confidence'],
                    'match_count': dup['match_count'],
                })
            
            return Response({
                'count': len(results),
                'results': results,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error detecting duplicates: {e}")
            return Response(
                {'error': 'Failed to detect duplicates', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='by-role/(?P<role>[^/.]+)')
    def by_role(self, request, role=None):
        """Get suspected duplicates for a specific role."""
        min_confidence = request.query_params.get('min_confidence', 'low')
        
        try:
            duplicates = DuplicateAccountDetectionService.detect_all(
                role_filter=role,
                min_confidence=min_confidence
            )
            
            # Serialize (same as detect method)
            results = []
            for dup in duplicates:
                user_data = []
                for user in dup['users']:
                    user_data.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'website': {
                            'id': user.website.id if user.website else None,
                            'name': user.website.name if user.website else None,
                        } if user.website else None,
                    })
                
                results.append({
                    'user_ids': dup['user_ids'],
                    'users': user_data,
                    'confidence': dup['confidence'],
                    'signals': dup['signals'],
                })
            
            return Response({
                'role': role,
                'count': len(results),
                'results': results,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to detect duplicates', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='user-duplicates')
    def user_duplicates(self, request, pk=None):
        """Get all suspected duplicates for a specific user."""
        try:
            user = User.objects.get(id=pk)
            duplicates = DuplicateAccountDetectionService.get_user_duplicate_summary(user.id)
            
            results = []
            for dup in duplicates:
                other_users = [u for u in dup['users'] if u.id != user.id]
                results.append({
                    'matched_users': [
                        {
                            'id': u.id,
                            'username': u.username,
                            'email': u.email,
                            'website': u.website.name if u.website else None,
                        }
                        for u in other_users
                    ],
                    'signals': dup['signals'],
                    'confidence': dup['confidence'],
                })
            
            return Response({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'suspected_duplicates': results,
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to get duplicates', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about duplicate detection."""
        try:
            client_duplicates = DuplicateAccountDetectionService.detect_all(role_filter='client')
            writer_duplicates = DuplicateAccountDetectionService.detect_all(role_filter='writer')
            
            # Count unique users involved
            client_user_ids = set()
            for dup in client_duplicates:
                client_user_ids.update(dup['user_ids'])
            
            writer_user_ids = set()
            for dup in writer_duplicates:
                writer_user_ids.update(dup['user_ids'])
            
            return Response({
                'clients': {
                    'suspected_groups': len(client_duplicates),
                    'users_involved': len(client_user_ids),
                },
                'writers': {
                    'suspected_groups': len(writer_duplicates),
                    'users_involved': len(writer_user_ids),
                },
                'total': {
                    'suspected_groups': len(client_duplicates) + len(writer_duplicates),
                    'users_involved': len(client_user_ids | writer_user_ids),
                },
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to get stats', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

