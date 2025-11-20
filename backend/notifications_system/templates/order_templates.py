"""
Order-related notification templates.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple
from notifications_system.templates.base import OrderNotificationTemplate
from notifications_system.registry.template_registry import register_template_class


@register_template_class("order.created")
class OrderCreatedTemplate(OrderNotificationTemplate):
    """Template for when a new order is created."""
    
    event_name = "order.created"
    priority = 7
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render order created notification."""
        order_ctx = self._get_order_context(context)
        user_ctx = self._get_user_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        
        title = f"New Order Created: {order_ctx['order_title']}"
        
        text = f"""Hello {user_ctx['username']},

A new order has been created in the system.

Order Details:
- Order ID: #{order_ctx['order_id']}
- Title: {order_ctx['order_title']}
- Amount: {order_ctx['order_currency']} {order_ctx['order_amount']}
- Status: {order_ctx['order_status']}

You can view the order at: {frontend_url}/orders/{order_ctx['order_id']}

Best regards,
The Writing System Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">New Order Created</h2>
            <p>Hello {user_ctx['username']},</p>
            <p>A new order has been created in the system.</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #495057;">Order Details</h3>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Order ID:</strong> #{order_ctx['order_id']}</li>
                    <li><strong>Title:</strong> {order_ctx['order_title']}</li>
                    <li><strong>Amount:</strong> {order_ctx['order_currency']} {order_ctx['order_amount']}</li>
                    <li><strong>Status:</strong> {order_ctx['order_status']}</li>
                </ul>
            </div>
            
            <p>
                <a href="{frontend_url}/orders/{order_ctx['order_id']}" 
                   style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Order
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                Best regards,<br>
                The Writing System Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("order.assigned")
class OrderAssignedTemplate(OrderNotificationTemplate):
    """Template for when an order is assigned to a writer."""
    
    event_name = "order.assigned"
    priority = 8
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render order assigned notification."""
        order_ctx = self._get_order_context(context)
        user_ctx = self._get_user_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        writer = context.get("writer", {})
        writer_name = writer.get("username", "Writer")
        
        title = f"Order Assigned: {order_ctx['order_title']}"
        
        text = f"""Hello {user_ctx['username']},

You have been assigned a new order.

Order Details:
- Order ID: #{order_ctx['order_id']}
- Title: {order_ctx['order_title']}
- Amount: {order_ctx['order_currency']} {order_ctx['order_amount']}
- Status: {order_ctx['order_status']}

Please review the order requirements and begin work as soon as possible.

View Order: {frontend_url}/orders/{order_ctx['order_id']}

Best regards,
The Writing System Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">Order Assigned</h2>
            <p>Hello {user_ctx['username']},</p>
            <p>You have been assigned a new order.</p>
            
            <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="margin-top: 0; color: #155724;">Order Details</h3>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Order ID:</strong> #{order_ctx['order_id']}</li>
                    <li><strong>Title:</strong> {order_ctx['order_title']}</li>
                    <li><strong>Amount:</strong> {order_ctx['order_currency']} {order_ctx['order_amount']}</li>
                    <li><strong>Status:</strong> {order_ctx['order_status']}</li>
                </ul>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p style="margin: 0; color: #856404;">
                    <strong>Action Required:</strong> Please review the order requirements and begin work as soon as possible.
                </p>
            </div>
            
            <p>
                <a href="{frontend_url}/orders/{order_ctx['order_id']}" 
                   style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Order
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                Best regards,<br>
                The Writing System Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("order.completed")
class OrderCompletedTemplate(OrderNotificationTemplate):
    """Template for when an order is completed."""
    
    event_name = "order.completed"
    priority = 8
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render order completed notification."""
        order_ctx = self._get_order_context(context)
        user_ctx = self._get_user_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        
        title = f"Order Completed: {order_ctx['order_title']}"
        
        text = f"""Hello {user_ctx['username']},

Great news! Your order has been completed.

Order Details:
- Order ID: #{order_ctx['order_id']}
- Title: {order_ctx['order_title']}
- Amount: {order_ctx['order_currency']} {order_ctx['order_amount']}
- Status: Completed

You can now download your completed work and provide feedback.

View Order: {frontend_url}/orders/{order_ctx['order_id']}

Thank you for using our service!

Best regards,
The Writing System Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">Order Completed! 🎉</h2>
            <p>Hello {user_ctx['username']},</p>
            <p>Great news! Your order has been completed.</p>
            
            <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="margin-top: 0; color: #155724;">Order Details</h3>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Order ID:</strong> #{order_ctx['order_id']}</li>
                    <li><strong>Title:</strong> {order_ctx['order_title']}</li>
                    <li><strong>Amount:</strong> {order_ctx['order_currency']} {order_ctx['order_amount']}</li>
                    <li><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">Completed</span></li>
                </ul>
            </div>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <p style="margin: 0; color: #004085;">
                    <strong>Next Steps:</strong> You can now download your completed work and provide feedback.
                </p>
            </div>
            
            <p>
                <a href="{frontend_url}/orders/{order_ctx['order_id']}" 
                   style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Order
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                Thank you for using our service!<br>
                Best regards,<br>
                The Writing System Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("order.paid")
class OrderPaidTemplate(OrderNotificationTemplate):
    """Template for when an order payment is received."""
    
    event_name = "order.paid"
    priority = 7
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render order paid notification."""
        order_ctx = self._get_order_context(context)
        user_ctx = self._get_user_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        payment = context.get("payment", {})
        
        title = f"Payment Received: {order_ctx['order_title']}"
        
        text = f"""Hello {user_ctx['username']},

Payment has been received for your order.

Order Details:
- Order ID: #{order_ctx['order_id']}
- Title: {order_ctx['order_title']}
- Amount: {order_ctx['order_currency']} {order_ctx['order_amount']}
- Payment ID: {payment.get('id', 'N/A')}

Your order is now confirmed and will be processed.

View Order: {frontend_url}/orders/{order_ctx['order_id']}

Thank you for your payment!

Best regards,
The Writing System Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">Payment Received ✅</h2>
            <p>Hello {user_ctx['username']},</p>
            <p>Payment has been received for your order.</p>
            
            <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="margin-top: 0; color: #155724;">Order Details</h3>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Order ID:</strong> #{order_ctx['order_id']}</li>
                    <li><strong>Title:</strong> {order_ctx['order_title']}</li>
                    <li><strong>Amount:</strong> {order_ctx['order_currency']} {order_ctx['order_amount']}</li>
                    <li><strong>Payment ID:</strong> {payment.get('id', 'N/A')}</li>
                </ul>
            </div>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <p style="margin: 0; color: #004085;">
                    <strong>Status:</strong> Your order is now confirmed and will be processed.
                </p>
            </div>
            
            <p>
                <a href="{frontend_url}/orders/{order_ctx['order_id']}" 
                   style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Order
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                Thank you for your payment!<br>
                Best regards,<br>
                The Writing System Team
            </p>
        </div>
        """
        
        return title, text, html
