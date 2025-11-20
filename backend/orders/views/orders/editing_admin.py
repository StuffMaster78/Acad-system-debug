"""
Admin endpoints for managing order editing requirements.
"""

from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from orders.models import Order
from orders.permissions import CanExecuteOrderAction
from authentication.permissions import IsAdminOrSuperAdmin
from audit_logging.services.audit_log_service import AuditLogService


class OrderEditingAdminView(views.APIView):
    """
    Admin-only endpoints for managing order editing requirements.
    """
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    
    def patch(self, request, pk: int):
        """
        Set editing requirement for a specific order.
        
        Request body:
        {
            "requires_editing": true,  // true = force editing, false = skip editing, null = use config
            "reason": "Optional reason for the override"
        }
        """
        order = get_object_or_404(Order, pk=pk)
        
        requires_editing = request.data.get('requires_editing')
        if requires_editing is None:
            # Remove override - use config rules
            old_value = order.requires_editing
            order.requires_editing = None
            order.editing_skip_reason = None
            order.save(update_fields=['requires_editing', 'editing_skip_reason'])
            
            AuditLogService.log_auto(
                actor=request.user,
                action="Removed editing override",
                target=order,
                changes={
                    "requires_editing": {"old": old_value, "new": None}
                }
            )
            
            return Response({
                "status": "success",
                "message": "Editing override removed - will use configuration rules",
                "order_id": order.id,
                "requires_editing": None
            })
        
        if not isinstance(requires_editing, bool):
            return Response(
                {"detail": "requires_editing must be true, false, or null"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_value = order.requires_editing
        order.requires_editing = requires_editing
        
        if requires_editing:
            order.editing_skip_reason = None
        else:
            reason = request.data.get('reason', 'Admin disabled editing')
            order.editing_skip_reason = reason
        
        order.save(update_fields=['requires_editing', 'editing_skip_reason'])
        
        AuditLogService.log_auto(
            actor=request.user,
            action=f"{'Force' if requires_editing else 'Skip'} editing",
            target=order,
            changes={
                "requires_editing": {"old": old_value, "new": requires_editing},
                "editing_skip_reason": order.editing_skip_reason
            }
        )
        
        return Response({
            "status": "success",
            "message": f"Editing {'required' if requires_editing else 'disabled'} for order",
            "order_id": order.id,
            "requires_editing": requires_editing,
            "editing_skip_reason": order.editing_skip_reason
        })

