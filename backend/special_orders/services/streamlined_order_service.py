"""
Streamlined Special Order Service
Unified service for placing, negotiating, pricing, and completing special orders.
"""
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from special_orders.models import SpecialOrder, InstallmentPayment, EstimatedSpecialOrderSettings
from special_orders.services.installment_payment_service import InstallmentPaymentService
from special_orders.services.writer_assignment import assign_writer as assign_special_order_writer
from notifications_system.services.core import NotificationService

logger = logging.getLogger(__name__)


class StreamlinedSpecialOrderService:
    """
    Streamlined service for managing special order lifecycle:
    1. Place order (client)
    2. Set/negotiate price (admin)
    3. Approve order (admin)
    4. Assign writer (admin)
    5. Complete order (writer/admin)
    """
    
    @staticmethod
    @transaction.atomic
    def place_order(data, client):
        """
        Place a new special order (streamlined creation).
        
        Args:
            data: Order data dict with:
                - order_type: 'predefined' or 'estimated'
                - predefined_type_id: (if predefined)
                - duration_days: int
                - inquiry_details: str
                - website_id: int
                - price_per_day: Decimal (optional, for estimated)
            client: User instance (client)
        
        Returns:
            SpecialOrder: Created order
        """
        from websites.models import Website
        
        order_type = data.get('order_type', 'estimated')
        website_id = data.get('website_id') or data.get('website')
        
        if not website_id:
            raise ValidationError("website_id is required")
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            raise ValidationError("Website not found")
        
        # Create order
        order_data = {
            'client': client,
            'website': website,
            'order_type': order_type,
            'duration_days': data.get('duration_days'),
            'inquiry_details': data.get('inquiry_details', ''),
            'status': 'inquiry',
        }
        
        # Handle predefined orders
        if order_type == 'predefined':
            predefined_type_id = data.get('predefined_type_id') or data.get('predefined_type')
            if not predefined_type_id:
                raise ValidationError("predefined_type_id is required for predefined orders")
            
            from special_orders.models import PredefinedSpecialOrderConfig
            try:
                predefined_type = PredefinedSpecialOrderConfig.objects.get(id=predefined_type_id)
            except PredefinedSpecialOrderConfig.DoesNotExist:
                raise ValidationError("Predefined type not found")
            
            order_data['predefined_type'] = predefined_type
            
            # Get price from duration
            duration_days = data.get('duration_days')
            if not duration_days:
                raise ValidationError("duration_days is required")
            
            duration_price = predefined_type.durations.filter(
                duration_days=duration_days
            ).first()
            
            if not duration_price:
                raise ValidationError(f"No pricing found for {duration_days} days")
            
            order_data['total_cost'] = duration_price.price
            order_data['deposit_required'] = duration_price.price  # Full payment for predefined
        
        # Handle estimated orders
        elif order_type == 'estimated':
            price_per_day = data.get('price_per_day')
            duration_days = data.get('duration_days', 1)
            
            if price_per_day:
                order_data['price_per_day'] = Decimal(str(price_per_day))
                order_data['total_cost'] = Decimal(str(price_per_day)) * duration_days
            else:
                order_data['total_cost'] = None
                order_data['price_per_day'] = None
            
            # Deposit will be calculated when price is set
            order_data['deposit_required'] = None
        
        # Create order
        order = SpecialOrder.objects.create(**order_data)
        
        # Generate installments if total_cost is set
        if order.total_cost:
            InstallmentPaymentService.generate_installments(order)
        
        # Notify admins (notification would need to be sent individually to each admin)
        # For now, we'll skip admin notifications or implement separately
        # TODO: Implement admin notification broadcast
        logger.info(f"New special order {order.id} created - admin notification needed")
        
        logger.info(f"Special order {order.id} placed by client {client.username}")
        return order
    
    @staticmethod
    @transaction.atomic
    def set_price(order, admin_user, total_cost=None, price_per_day=None, admin_notes=None):
        """
        Set or negotiate price for an estimated order (admin action).
        Can be called multiple times for negotiation.
        
        Args:
            order: SpecialOrder instance
            admin_user: User instance (admin)
            total_cost: Decimal (optional, total cost)
            price_per_day: Decimal (optional, price per day)
            admin_notes: str (optional, negotiation notes)
        
        Returns:
            SpecialOrder: Updated order
        """
        if order.order_type != 'estimated':
            raise ValidationError("Price setting is only for estimated orders")
        
        if order.status not in ['inquiry', 'awaiting_approval']:
            raise ValidationError(f"Cannot set price for order in status '{order.status}'")
        
        # Calculate total_cost if price_per_day provided
        if price_per_day and not total_cost:
            total_cost = Decimal(str(price_per_day)) * order.duration_days
            order.price_per_day = Decimal(str(price_per_day))
        elif total_cost:
            total_cost = Decimal(str(total_cost))
            if order.duration_days:
                order.price_per_day = total_cost / order.duration_days
        
        if not total_cost:
            raise ValidationError("Either total_cost or price_per_day must be provided")
        
        # Update order
        old_cost = order.total_cost
        order.total_cost = total_cost
        order.admin_approved_cost = total_cost
        
        # Calculate deposit
        config = getattr(order.website, 'estimated_order_settings', None)
        deposit_percent = config.default_deposit_percentage if config else 50.0
        order.deposit_required = round(total_cost * (deposit_percent / 100), 2)
        
        # Update admin notes
        if admin_notes:
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            note = f"[{timestamp}] {admin_user.username}: {admin_notes}"
            order.admin_notes = (order.admin_notes or '') + '\n' + note if order.admin_notes else note
        
        # Regenerate installments if cost changed
        if old_cost != total_cost:
            # Delete old installments
            order.installments.all().delete()
            # Generate new installments
            InstallmentPaymentService.generate_installments(order)
        
        # Update status
        if order.status == 'inquiry':
            order.status = 'awaiting_approval'
        
        order.save()
        
        # Notify client
        try:
            NotificationService.send_notification(
                user=order.client,
                event="special_order.price_set",
                payload={
                    "order_id": order.id,
                    "total_cost": float(total_cost),
                    "deposit_required": float(order.deposit_required),
                    "admin_notes": admin_notes,
                },
                website=order.website
            )
        except Exception as e:
            logger.warning(f"Failed to send price notification for order {order.id}: {e}")
        
        logger.info(f"Price set for order {order.id} by {admin_user.username}: ${total_cost}")
        return order
    
    @staticmethod
    @transaction.atomic
    def approve_and_assign(order, admin_user, writer_id=None, writer_payment_amount=None, 
                          writer_payment_percentage=None, auto_assign=False):
        """
        Streamlined approval and optional writer assignment in one action.
        
        Args:
            order: SpecialOrder instance
            admin_user: User instance (admin)
            writer_id: int (optional, writer to assign)
            writer_payment_amount: Decimal (optional, fixed payment)
            writer_payment_percentage: Decimal (optional, percentage payment)
            auto_assign: bool (if True, auto-assigns best writer)
        
        Returns:
            dict: Updated order data
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Validate order can be approved
        if order.status not in ['inquiry', 'awaiting_approval']:
            raise ValidationError(f"Order cannot be approved from status '{order.status}'")
        
        if not order.total_cost:
            raise ValidationError("Order must have a price set before approval")
        
        # Approve order
        order.is_approved = True
        
        # Check if deposit is paid
        deposit_paid = (
            order.admin_marked_paid or
            (order.deposit_required and 
             order.installments.filter(is_paid=True).exists())
        )
        
        # Assign writer if provided
        writer = None
        if writer_id:
            try:
                writer = User.objects.get(id=writer_id, role='writer', is_active=True)
            except User.DoesNotExist:
                raise ValidationError("Writer not found or not active")
            
            assign_special_order_writer(
                order,
                writer,
                payment_amount=writer_payment_amount,
                payment_percentage=writer_payment_percentage
            )
        
        # Auto-assign if requested (simplified - would need smart matching service)
        elif auto_assign:
            # TODO: Implement smart writer matching
            logger.warning("Auto-assign not yet implemented")
        
        # Update status
        if deposit_paid and writer:
            order.status = 'in_progress'
        elif deposit_paid:
            order.status = 'awaiting_approval'  # Approved but no writer yet
        else:
            order.status = 'awaiting_approval'  # Approved but waiting for payment
        
        order.save()
        
        # Notify client and writer
        try:
            NotificationService.send_notification(
                user=order.client,
                event="special_order.approved",
                payload={
                    "order_id": order.id,
                    "status": order.status,
                    "writer_assigned": writer is not None,
                },
                website=order.website
            )
            
            if writer:
                NotificationService.send_notification(
                    user=writer,
                    event="special_order.assigned",
                    payload={
                        "order_id": order.id,
                        "client_username": order.client.username,
                    },
                    website=order.website
                )
        except Exception as e:
            logger.warning(f"Failed to send approval notifications for order {order.id}: {e}")
        
        logger.info(f"Order {order.id} approved by {admin_user.username}, writer: {writer.username if writer else 'None'}")
        
        return {
            'order': order,
            'writer_assigned': writer is not None,
            'status': order.status,
        }
    
    @staticmethod
    @transaction.atomic
    def complete_order(order, completed_by, files_uploaded=True, completion_notes=None):
        """
        Streamlined order completion process.
        
        Args:
            order: SpecialOrder instance
            completed_by: User instance (writer or admin)
            files_uploaded: bool (whether files were uploaded)
            completion_notes: str (optional completion notes)
        
        Returns:
            SpecialOrder: Completed order
        """
        # Validate completion
        if order.status != 'in_progress':
            raise ValidationError(f"Order must be in_progress to complete. Current status: {order.status}")
        
        # Check if writer is completing their own order
        if completed_by.role == 'writer' and order.writer != completed_by:
            raise ValidationError("Writers can only complete their assigned orders")
        
        # Update order
        order.status = 'completed'
        order.writer_completed_no_files = not files_uploaded
        
        if completion_notes:
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            note = f"[{timestamp}] Completion: {completion_notes}"
            order.admin_notes = (order.admin_notes or '') + '\n' + note if order.admin_notes else note
        
        order.save()
        
        # Notify client
        try:
            NotificationService.send_notification(
                user=order.client,
                event="special_order.completed",
                payload={
                    "order_id": order.id,
                    "completed_by": completed_by.username,
                    "files_uploaded": files_uploaded,
                },
                website=order.website
            )
        except Exception as e:
            logger.warning(f"Failed to send completion notification for order {order.id}: {e}")
        
        logger.info(f"Order {order.id} completed by {completed_by.username}")
        return order
    
    @staticmethod
    def get_order_workflow_status(order, user=None):
        """
        Get current workflow status and next available actions.
        
        Args:
            order: SpecialOrder instance
            user: User instance (optional, for role-based actions)
        
        Returns:
            dict: Workflow status with available actions
        """
        deposit_paid = order.admin_marked_paid or (
            order.deposit_required and 
            order.installments.filter(is_paid=True).exists()
        )
        
        status_info = {
            'current_status': order.status,
            'is_approved': order.is_approved,
            'has_price': order.total_cost is not None and order.total_cost > 0,
            'has_writer': order.writer is not None,
            'deposit_paid': deposit_paid,
            'all_payments_paid': all(
                inst.is_paid for inst in order.installments.all()
            ) if order.installments.exists() else False,
            'available_actions': {
                'client': [],
                'admin': [],
                'writer': [],
            },
        }
        
        user_role = getattr(user, 'role', None) if user else None
        
        # Determine available actions based on status and role
        if order.status == 'inquiry':
            if user_role in ['admin', 'superadmin', 'support']:
                if not status_info['has_price']:
                    status_info['available_actions']['admin'].append('set_price')
                else:
                    status_info['available_actions']['admin'].extend(['approve', 'set_price', 'approve_and_assign'])
        
        elif order.status == 'awaiting_approval':
            if user_role in ['admin', 'superadmin', 'support']:
                if not status_info['has_writer']:
                    status_info['available_actions']['admin'].extend(['assign_writer', 'approve_and_assign'])
                if not deposit_paid:
                    status_info['available_actions']['admin'].append('mark_payment_paid')
                if deposit_paid and status_info['has_writer']:
                    status_info['available_actions']['admin'].append('start_work')
            
            if user_role == 'client':
                status_info['available_actions']['client'].append('pay_deposit')
        
        elif order.status == 'in_progress':
            if user_role == 'writer' and order.writer == user:
                status_info['available_actions']['writer'].append('complete')
            if user_role in ['admin', 'superadmin', 'support']:
                status_info['available_actions']['admin'].extend(['complete', 'unlock_files', 'mark_paid'])
        
        elif order.status == 'completed':
            status_info['available_actions']['client'].append('view_completion')
            status_info['available_actions']['admin'].append('view_completion')
        
        return status_info

