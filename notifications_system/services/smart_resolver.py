"""
Smart template resolution with fallbacks and performance optimization.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple, Type
from django.core.cache import cache
from notifications_system.templates.base import BaseNotificationTemplate
from notifications_system.registry.template_registry import get_template, _TEMPLATE_CLASSES
from notifications_system.services.templates_registry import resolve_template as resolve_db_template

logger = logging.getLogger(__name__)


class SmartTemplateResolver:
    """
    Smart template resolution with multiple fallback strategies.
    
    Resolution order:
    1. Class-based templates (fastest, type-safe)
    2. Database templates (flexible, user-editable)
    3. Generic fallback templates
    4. Emergency fallback
    """
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
        self.performance_stats = {}
    
    def resolve_template(
        self, 
        event_key: str, 
        context: Dict[str, Any],
        channel: str = "email",
        website_id: Optional[int] = None,
        locale: str = "en"
    ) -> Tuple[str, str, str]:
        """
        Resolve and render template with smart fallbacks.
        
        Args:
            event_key: The notification event key
            context: Template context data
            channel: Notification channel
            website_id: Website/tenant ID
            locale: User locale
            
        Returns:
            (title, text, html) tuple
            
        Raises:
            TemplateNotFoundError: If no template can be resolved
        """
        import time
        start_time = time.time()
        
        try:
            # Try class-based template first (fastest)
            template_result = self._try_class_template(event_key, context)
            if template_result:
                self._record_performance(event_key, "class", time.time() - start_time)
                return template_result
            
            # Try database template (flexible)
            template_result = self._try_database_template(
                event_key, context, channel, website_id, locale
            )
            if template_result:
                self._record_performance(event_key, "database", time.time() - start_time)
                return template_result
            
            # Try generic fallback
            template_result = self._try_generic_template(event_key, context)
            if template_result:
                self._record_performance(event_key, "generic", time.time() - start_time)
                return template_result
            
            # Emergency fallback
            template_result = self._emergency_fallback(event_key, context)
            self._record_performance(event_key, "emergency", time.time() - start_time)
            return template_result
            
        except Exception as e:
            # Use debug level for template resolution failures unless it's critical
            logger.debug(f"Template resolution failed for {event_key}: {e}")
            # Final emergency fallback
            return self._emergency_fallback(event_key, context)
    
    def _try_class_template(self, event_key: str, context: Dict[str, Any]) -> Optional[Tuple[str, str, str]]:
        """Try to resolve using class-based template."""
        try:
            if event_key in _TEMPLATE_CLASSES:
                template = get_template(event_key)
                return template.render(context)
        except Exception as e:
            logger.debug(f"Class template failed for {event_key}: {e}")
        return None
    
    def _try_database_template(
        self, 
        event_key: str, 
        context: Dict[str, Any],
        channel: str,
        website_id: Optional[int],
        locale: str
    ) -> Optional[Tuple[str, str, str]]:
        """Try to resolve using database template."""
        try:
            # Check cache first
            cache_key = f"template:{event_key}:{channel}:{website_id}:{locale}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Resolve database template
            db_template = resolve_db_template(event_key, channel, website_id, locale)
            if db_template:
                # Render the database template
                from notifications_system.services.render import render_template
                rendered = render_template(db_template, context)
                
                # Cache the result
                cache.set(cache_key, rendered, self.cache_timeout)
                return rendered
                
        except Exception as e:
            logger.debug(f"Database template failed for {event_key}: {e}")
        return None
    
    def _try_generic_template(self, event_key: str, context: Dict[str, Any]) -> Optional[Tuple[str, str, str]]:
        """Try to resolve using generic template."""
        try:
            # Try to find a generic template for the event category
            category = event_key.split('.')[0]
            generic_key = f"{category}.generic"
            
            if generic_key in _TEMPLATE_CLASSES:
                template = get_template(generic_key)
                return template.render(context)
                
        except Exception as e:
            logger.debug(f"Generic template failed for {event_key}: {e}")
        return None
    
    def _emergency_fallback(self, event_key: str, context: Dict[str, Any]) -> Tuple[str, str, str]:
        """Emergency fallback when all other methods fail."""
        # Use debug level instead of warning for emergency fallbacks
        # These are expected when templates aren't configured yet
        logger.debug(f"Using emergency fallback for {event_key}")
        
        # Extract basic info from context
        user = context.get('user', {})
        username = user.get('username', 'User') if isinstance(user, dict) else str(user)
        
        title = f"Notification: {event_key.replace('_', ' ').title()}"
        text = f"Hello {username},\n\nYou have received a notification: {event_key}\n\nThis is an automated message."
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Notification</h2>
            <p>Hello {username},</p>
            <p>You have received a notification: <strong>{event_key}</strong></p>
            <p>This is an automated message.</p>
        </div>
        """
        
        return title, text, html
    
    def _record_performance(self, event_key: str, method: str, duration: float):
        """Record performance metrics for optimization."""
        if event_key not in self.performance_stats:
            self.performance_stats[event_key] = {}
        
        if method not in self.performance_stats[event_key]:
            self.performance_stats[event_key][method] = []
        
        self.performance_stats[event_key][method].append(duration)
        
        # Keep only last 100 measurements
        if len(self.performance_stats[event_key][method]) > 100:
            self.performance_stats[event_key][method] = self.performance_stats[event_key][method][-100:]
    
    def get_performance_stats(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Get performance statistics for all templates."""
        stats = {}
        
        for event_key, methods in self.performance_stats.items():
            stats[event_key] = {}
            for method, durations in methods.items():
                if durations:
                    stats[event_key][method] = {
                        'avg_duration': sum(durations) / len(durations),
                        'min_duration': min(durations),
                        'max_duration': max(durations),
                        'count': len(durations)
                    }
        
        return stats


# Global resolver instance
_smart_resolver = None

def get_smart_resolver() -> SmartTemplateResolver:
    """Get the global smart resolver instance."""
    global _smart_resolver
    if _smart_resolver is None:
        _smart_resolver = SmartTemplateResolver()
    return _smart_resolver


def resolve_smart_template(
    event_key: str,
    context: Dict[str, Any],
    channel: str = "email",
    website_id: Optional[int] = None,
    locale: str = "en"
) -> Tuple[str, str, str]:
    """
    Convenience function to resolve templates using smart resolver.
    
    Args:
        event_key: The notification event key
        context: Template context data
        channel: Notification channel
        website_id: Website/tenant ID
        locale: User locale
        
    Returns:
        (title, text, html) tuple
    """
    resolver = get_smart_resolver()
    return resolver.resolve_template(event_key, context, channel, website_id, locale)
