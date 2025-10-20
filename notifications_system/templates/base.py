"""
Enhanced base template classes for the notification system.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
from django.utils.html import escape
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


class BaseNotificationTemplate(ABC):
    """
    Enhanced base class for notification templates.
    
    Provides common functionality for all notification templates including:
    - Type-safe context handling
    - Template validation
    - Error handling
    - Performance monitoring
    """
    
    # Template metadata
    event_name: str = "generic"
    priority: int = 5
    channels: List[str] = ["email", "in_app"]
    version: str = "1.0"
    
    # Template configuration
    requires_context: List[str] = []
    optional_context: List[str] = []
    max_retries: int = 3
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """Initialize template with context."""
        self.context = context or {}
        self._render_count = 0
        self._last_render_time = None
        
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that required context is present.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Check required context
        for field in self.requires_context:
            if field not in context:
                errors.append(f"Missing required context field: {field}")
        
        # Check for None values in required fields
        for field in self.requires_context:
            if field in context and context[field] is None:
                errors.append(f"Required context field '{field}' is None")
        
        return len(errors) == 0, errors
    
    def get_safe_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get context with safe HTML escaping applied.
        
        Returns:
            Context with HTML-escaped string values
        """
        safe_context = {}
        for key, value in context.items():
            if isinstance(value, str):
                safe_context[key] = escape(value)
            elif isinstance(value, dict):
                safe_context[key] = self.get_safe_context(value)
            elif isinstance(value, list):
                safe_context[key] = [
                    escape(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                safe_context[key] = value
        return safe_context
    
    def render(self, context: Optional[Dict[str, Any]] = None) -> Tuple[str, str, str]:
        """
        Render the notification template.
        
        Args:
            context: Additional context to merge with template context
            
        Returns:
            (title, text, html) tuple
            
        Raises:
            ValueError: If required context is missing
            RuntimeError: If template rendering fails
        """
        # Merge contexts
        full_context = {**self.context, **(context or {})}
        
        # Validate context
        is_valid, errors = self.validate_context(full_context)
        if not is_valid:
            error_msg = f"Template validation failed for {self.event_name}: {', '.join(errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Track rendering
        self._render_count += 1
        self._last_render_time = datetime.now()
        
        try:
            # Get safe context for HTML rendering
            safe_context = self.get_safe_context(full_context)
            
            # Render template
            title, text, html = self._render_template(full_context, safe_context)
            
            # Log successful render
            logger.debug(
                f"Template {self.event_name} rendered successfully "
                f"(render #{self._render_count})"
            )
            
            return title, text, html
            
        except Exception as e:
            logger.exception(
                f"Template rendering failed for {self.event_name}: {e}"
            )
            raise RuntimeError(f"Template rendering failed: {e}") from e
    
    @abstractmethod
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        Render the actual template content.
        
        Args:
            context: Full context (may contain unsafe HTML)
            safe_context: Context with HTML escaping applied
            
        Returns:
            (title, text, html) tuple
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get template metadata for debugging/monitoring."""
        return {
            "event_name": self.event_name,
            "priority": self.priority,
            "channels": self.channels,
            "version": self.version,
            "render_count": self._render_count,
            "last_render": self._last_render_time,
            "requires_context": self.requires_context,
            "optional_context": self.optional_context,
        }


class OrderNotificationTemplate(BaseNotificationTemplate):
    """Base template for order-related notifications."""
    
    requires_context = ["order", "user"]
    optional_context = ["website", "actor", "frontend_url"]
    
    def _get_order_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract order-specific context."""
        order = context.get("order", {})
        return {
            "order_id": order.get("id", "N/A"),
            "order_title": order.get("title", "Untitled Order"),
            "order_status": order.get("status", "unknown"),
            "order_amount": order.get("amount", 0),
            "order_currency": order.get("currency", "USD"),
        }
    
    def _get_user_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user-specific context."""
        user = context.get("user", {})
        return {
            "username": user.get("username", "User"),
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "email": user.get("email", ""),
        }


class UserNotificationTemplate(BaseNotificationTemplate):
    """Base template for user-related notifications."""
    
    requires_context = ["user"]
    optional_context = ["website", "frontend_url"]
    
    def _get_user_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user-specific context."""
        user = context.get("user", {})
        return {
            "username": user.get("username", "User"),
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "email": user.get("email", ""),
            "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        }


class SystemNotificationTemplate(BaseNotificationTemplate):
    """Base template for system-related notifications."""
    
    requires_context = []
    optional_context = ["website", "admin_user", "system_info"]
    
    def _get_system_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract system-specific context."""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_name": context.get("system_name", "Writing System"),
            "admin_email": context.get("admin_email", "admin@example.com"),
        }


class WalletNotificationTemplate(BaseNotificationTemplate):
    """Base template for wallet-related notifications."""
    
    requires_context = ["user", "wallet"]
    optional_context = ["transaction", "website", "frontend_url"]
    
    def _get_wallet_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract wallet-specific context."""
        wallet = context.get("wallet", {})
        transaction = context.get("transaction", {})
        
        return {
            "balance": wallet.get("balance", 0),
            "currency": wallet.get("currency", "USD"),
            "transaction_id": transaction.get("id", "N/A"),
            "transaction_amount": transaction.get("amount", 0),
            "transaction_type": transaction.get("type", "unknown"),
        }
