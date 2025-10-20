"""
User-related notification templates.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple
from notifications_system.templates.base import UserNotificationTemplate
from notifications_system.registry.template_registry import register_template_class


@register_template_class("user.welcome")
class UserWelcomeTemplate(UserNotificationTemplate):
    """Template for user welcome notifications."""
    
    event_name = "user.welcome"
    priority = 6
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render user welcome notification."""
        user_ctx = self._get_user_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        website = context.get("website", {})
        site_name = website.get("name", "Writing System")
        
        title = f"Welcome to {site_name}!"
        
        text = f"""Hello {user_ctx['full_name'] or user_ctx['username']},

Welcome to {site_name}! We're excited to have you on board.

Your account has been successfully created and you can now:

• Browse available writing services
• Place orders for custom content
• Track your order progress
• Manage your account settings

Get started by exploring our services or placing your first order.

Visit Dashboard: {frontend_url}/dashboard

If you have any questions, feel free to contact our support team.

Best regards,
The {site_name} Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Welcome to {site_name}! 🎉</h2>
            <p>Hello {user_ctx['full_name'] or user_ctx['username']},</p>
            <p>Welcome to {site_name}! We're excited to have you on board.</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #495057;">Your account has been successfully created and you can now:</h3>
                <ul style="color: #495057;">
                    <li>Browse available writing services</li>
                    <li>Place orders for custom content</li>
                    <li>Track your order progress</li>
                    <li>Manage your account settings</li>
                </ul>
            </div>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <p style="margin: 0; color: #004085;">
                    <strong>Get Started:</strong> Explore our services or place your first order.
                </p>
            </div>
            
            <p>
                <a href="{frontend_url}/dashboard" 
                   style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Visit Dashboard
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                If you have any questions, feel free to contact our support team.<br>
                Best regards,<br>
                The {site_name} Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("user.registration")
class UserRegistrationTemplate(UserNotificationTemplate):
    """Template for user registration notifications (admin notification)."""
    
    event_name = "user.registration"
    priority = 5
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render user registration notification for admins."""
        user_ctx = self._get_user_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        website = context.get("website", {})
        site_name = website.get("name", "Writing System")
        
        title = f"New User Registration: {user_ctx['username']}"
        
        text = f"""New User Registration

A new user has registered on {site_name}.

User Details:
- Username: {user_ctx['username']}
- Name: {user_ctx['full_name'] or 'Not provided'}
- Email: {user_ctx['email']}

You can view the user profile in the admin panel.

View User: {frontend_url}/admin/users/{user_ctx['username']}

System Notification"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc3545;">New User Registration</h2>
            <p>A new user has registered on {site_name}.</p>
            
            <div style="background: #f8d7da; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <h3 style="margin-top: 0; color: #721c24;">User Details</h3>
                <ul style="list-style: none; padding: 0; color: #721c24;">
                    <li><strong>Username:</strong> {user_ctx['username']}</li>
                    <li><strong>Name:</strong> {user_ctx['full_name'] or 'Not provided'}</li>
                    <li><strong>Email:</strong> {user_ctx['email']}</li>
                </ul>
            </div>
            
            <p>
                <a href="{frontend_url}/admin/users/{user_ctx['username']}" 
                   style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View User
                </a>
            </p>
            
            <p style="color: #6c757d; font-size: 14px;">
                System Notification
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("user.password_reset")
class UserPasswordResetTemplate(UserNotificationTemplate):
    """Template for password reset notifications."""
    
    event_name = "user.password_reset"
    priority = 8
    channels = ["email"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render password reset notification."""
        user_ctx = self._get_user_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        reset_token = context.get("reset_token", "")
        website = context.get("website", {})
        site_name = website.get("name", "Writing System")
        
        title = f"Password Reset Request - {site_name}"
        
        text = f"""Hello {user_ctx['full_name'] or user_ctx['username']},

You have requested to reset your password for your {site_name} account.

To reset your password, click the link below:
{frontend_url}/reset-password?token={reset_token}

This link will expire in 24 hours for security reasons.

If you did not request this password reset, please ignore this email and your password will remain unchanged.

For security reasons, do not share this link with anyone.

Best regards,
The {site_name} Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc3545;">Password Reset Request</h2>
            <p>Hello {user_ctx['full_name'] or user_ctx['username']},</p>
            <p>You have requested to reset your password for your {site_name} account.</p>
            
            <div style="background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p style="margin: 0; color: #856404;">
                    <strong>To reset your password, click the button below:</strong>
                </p>
            </div>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{frontend_url}/reset-password?token={reset_token}" 
                   style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Reset Password
                </a>
            </p>
            
            <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #17a2b8;">
                <p style="margin: 0; color: #0c5460;">
                    <strong>Security Notice:</strong> This link will expire in 24 hours for security reasons.
                </p>
            </div>
            
            <div style="background: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <p style="margin: 0; color: #721c24;">
                    <strong>Important:</strong> If you did not request this password reset, please ignore this email and your password will remain unchanged.
                </p>
            </div>
            
            <p style="color: #6c757d; font-size: 14px;">
                For security reasons, do not share this link with anyone.<br>
                Best regards,<br>
                The {site_name} Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("user.profile_updated")
class UserProfileUpdatedTemplate(UserNotificationTemplate):
    """Template for user profile update notifications."""
    
    event_name = "user.profile_updated"
    priority = 4
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render profile update notification."""
        user_ctx = self._get_user_context(context)
        frontend_url = context.get("frontend_url", "https://example.com")
        changes = context.get("changes", [])
        website = context.get("website", {})
        site_name = website.get("name", "Writing System")
        
        title = f"Profile Updated - {site_name}"
        
        changes_text = "\n".join([f"• {change}" for change in changes]) if changes else "• Various profile information"
        
        text = f"""Hello {user_ctx['full_name'] or user_ctx['username']},

Your profile has been successfully updated.

Changes made:
{changes_text}

You can view your updated profile at any time.

View Profile: {frontend_url}/profile

If you did not make these changes, please contact our support team immediately.

Best regards,
The {site_name} Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">Profile Updated ✅</h2>
            <p>Hello {user_ctx['full_name'] or user_ctx['username']},</p>
            <p>Your profile has been successfully updated.</p>
            
            <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="margin-top: 0; color: #155724;">Changes made:</h3>
                <ul style="color: #155724;">
                    {''.join([f'<li>{change}</li>' for change in changes]) if changes else '<li>Various profile information</li>'}
                </ul>
            </div>
            
            <p>
                <a href="{frontend_url}/profile" 
                   style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Profile
                </a>
            </p>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p style="margin: 0; color: #856404;">
                    <strong>Security Notice:</strong> If you did not make these changes, please contact our support team immediately.
                </p>
            </div>
            
            <p style="color: #6c757d; font-size: 14px;">
                Best regards,<br>
                The {site_name} Team
            </p>
        </div>
        """
        
        return title, text, html
