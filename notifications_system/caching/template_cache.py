"""
Advanced template caching system with Redis.
"""
from __future__ import annotations

import hashlib
import json
import logging
import pickle
from typing import Any, Dict, List, Optional, Tuple, Union
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class TemplateCache:
    """
    Advanced template caching system with multiple cache layers.
    
    Features:
    - Multi-level caching (L1: Memory, L2: Redis)
    - Cache invalidation strategies
    - Performance metrics
    - Cache warming
    - Template versioning support
    """
    
    def __init__(self):
        self.l1_cache = {}  # In-memory cache
        self.l1_max_size = 1000
        self.l1_ttl = 300  # 5 minutes
        self.redis_ttl = 3600  # 1 hour
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'warmups': 0
        }
    
    def get_template(
        self, 
        cache_key: str, 
        version: Optional[str] = None
    ) -> Optional[Tuple[str, str, str]]:
        """
        Get cached template with multi-level lookup.
        
        Args:
            cache_key: Unique cache key for template
            version: Optional template version
            
        Returns:
            (title, text, html) tuple or None if not found
        """
        full_key = self._build_cache_key(cache_key, version)
        
        # L1 Cache (Memory)
        if full_key in self.l1_cache:
            entry = self.l1_cache[full_key]
            if not self._is_expired(entry):
                self.cache_stats['hits'] += 1
                return entry['content']
            else:
                del self.l1_cache[full_key]
        
        # L2 Cache (Redis)
        try:
            cached_content = cache.get(full_key)
            if cached_content:
                # Promote to L1 cache
                self._set_l1_cache(full_key, cached_content)
                self.cache_stats['hits'] += 1
                return cached_content
        except Exception as e:
            logger.warning(f"Redis cache error: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    def set_template(
        self, 
        cache_key: str, 
        content: Tuple[str, str, str],
        ttl: Optional[int] = None,
        version: Optional[str] = None
    ):
        """
        Cache template with multi-level storage.
        
        Args:
            cache_key: Unique cache key
            content: (title, text, html) tuple
            ttl: Time to live in seconds
            version: Optional template version
        """
        full_key = self._build_cache_key(cache_key, version)
        ttl = ttl or self.redis_ttl
        
        # L1 Cache (Memory)
        self._set_l1_cache(full_key, content, ttl)
        
        # L2 Cache (Redis)
        try:
            cache.set(full_key, content, ttl)
        except Exception as e:
            logger.warning(f"Redis cache set error: {e}")
    
    def _build_cache_key(self, base_key: str, version: Optional[str] = None) -> str:
        """Build full cache key with version."""
        if version:
            return f"template:{base_key}:v{version}"
        return f"template:{base_key}"
    
    def _set_l1_cache(self, key: str, content: Tuple[str, str, str], ttl: int = None):
        """Set L1 cache entry."""
        ttl = ttl or self.l1_ttl
        
        # Evict if cache is full
        if len(self.l1_cache) >= self.l1_max_size:
            self._evict_l1_cache()
        
        self.l1_cache[key] = {
            'content': content,
            'expires_at': timezone.now().timestamp() + ttl,
            'created_at': timezone.now().timestamp()
        }
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return timezone.now().timestamp() > entry['expires_at']
    
    def _evict_l1_cache(self):
        """Evict oldest entries from L1 cache."""
        if not self.l1_cache:
            return
        
        # Remove oldest entries (LRU)
        sorted_entries = sorted(
            self.l1_cache.items(),
            key=lambda x: x[1]['created_at']
        )
        
        # Remove 20% of entries
        evict_count = max(1, len(sorted_entries) // 5)
        for key, _ in sorted_entries[:evict_count]:
            del self.l1_cache[key]
            self.cache_stats['evictions'] += 1
    
    def invalidate_template(self, cache_key: str, version: Optional[str] = None):
        """Invalidate cached template."""
        full_key = self._build_cache_key(cache_key, version)
        
        # Remove from L1 cache
        if full_key in self.l1_cache:
            del self.l1_cache[full_key]
        
        # Remove from Redis
        try:
            cache.delete(full_key)
        except Exception as e:
            logger.warning(f"Redis cache delete error: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all templates matching pattern."""
        # This would require Redis SCAN in production
        # For now, we'll invalidate L1 cache only
        keys_to_remove = [key for key in self.l1_cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self.l1_cache[key]
    
    def warm_cache(self, templates: List[Dict[str, Any]]):
        """Warm cache with frequently used templates."""
        for template_data in templates:
            try:
                cache_key = template_data['cache_key']
                content = template_data['content']
                version = template_data.get('version')
                
                self.set_template(cache_key, content, version=version)
                self.cache_stats['warmups'] += 1
                
            except Exception as e:
                logger.warning(f"Cache warming error: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': hit_rate,
            'evictions': self.cache_stats['evictions'],
            'warmups': self.cache_stats['warmups'],
            'l1_size': len(self.l1_cache),
            'l1_max_size': self.l1_max_size
        }
    
    def clear_cache(self):
        """Clear all cached templates."""
        self.l1_cache.clear()
        try:
            # Clear Redis cache (this would need proper implementation)
            cache.clear()
        except Exception as e:
            logger.warning(f"Redis cache clear error: {e}")


class TemplateCacheManager:
    """Manager for template caching operations."""
    
    def __init__(self):
        self.cache = TemplateCache()
        self.cache_key_generator = CacheKeyGenerator()
    
    def get_cached_template(
        self,
        event_key: str,
        context: Dict[str, Any],
        channel: str = "email",
        website_id: Optional[int] = None,
        locale: str = "en",
        version: Optional[str] = None
    ) -> Optional[Tuple[str, str, str]]:
        """Get cached template if available."""
        cache_key = self.cache_key_generator.generate_key(
            event_key, context, channel, website_id, locale
        )
        
        return self.cache.get_template(cache_key, version)
    
    def cache_template(
        self,
        event_key: str,
        context: Dict[str, Any],
        content: Tuple[str, str, str],
        channel: str = "email",
        website_id: Optional[int] = None,
        locale: str = "en",
        version: Optional[str] = None,
        ttl: Optional[int] = None
    ):
        """Cache rendered template."""
        cache_key = self.cache_key_generator.generate_key(
            event_key, context, channel, website_id, locale
        )
        
        self.cache.set_template(cache_key, content, ttl, version)
    
    def invalidate_event_templates(self, event_key: str):
        """Invalidate all templates for an event."""
        pattern = f"template:{event_key}:*"
        self.cache.invalidate_pattern(pattern)
    
    def invalidate_user_templates(self, user_id: int):
        """Invalidate all templates for a user."""
        pattern = f"template:*:user_{user_id}:*"
        self.cache.invalidate_pattern(pattern)
    
    def warm_frequent_templates(self):
        """Warm cache with frequently used templates."""
        # This would typically query the database for popular templates
        frequent_templates = [
            {
                'cache_key': 'order.assigned:default',
                'content': ('Order Assigned', 'Your order has been assigned', '<h1>Order Assigned</h1>'),
                'version': 'v1.0'
            },
            {
                'cache_key': 'user.welcome:default',
                'content': ('Welcome!', 'Welcome to our platform', '<h1>Welcome!</h1>'),
                'version': 'v1.0'
            }
        ]
        
        self.cache.warm_cache(frequent_templates)


class CacheKeyGenerator:
    """Generate consistent cache keys for templates."""
    
    def generate_key(
        self,
        event_key: str,
        context: Dict[str, Any],
        channel: str = "email",
        website_id: Optional[int] = None,
        locale: str = "en"
    ) -> str:
        """Generate cache key for template."""
        # Create deterministic hash from context
        context_hash = self._hash_context(context)
        
        parts = [
            event_key,
            channel,
            f"website_{website_id}" if website_id else "global",
            f"locale_{locale}",
            context_hash
        ]
        
        return ":".join(parts)
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Create hash from context for cache key."""
        # Sort keys for consistent hashing
        sorted_context = {k: v for k, v in sorted(context.items())}
        
        # Create hash
        context_str = json.dumps(sorted_context, sort_keys=True, default=str)
        return hashlib.md5(context_str.encode()).hexdigest()[:8]


class TemplateCacheMiddleware:
    """Middleware for template cache management."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_manager = TemplateCacheManager()
    
    def __call__(self, request):
        # Pre-request cache warming
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._warm_user_cache(request.user.id)
        
        response = self.get_response(request)
        
        # Post-request cache cleanup
        self._cleanup_expired_cache()
        
        return response
    
    def _warm_user_cache(self, user_id: int):
        """Warm cache for user's frequent templates."""
        # This would typically query user's notification history
        pass
    
    def _cleanup_expired_cache(self):
        """Clean up expired cache entries."""
        # This would typically run periodically
        pass


# Global cache manager
_cache_manager = TemplateCacheManager()

def get_cache_manager() -> TemplateCacheManager:
    """Get the global template cache manager."""
    return _cache_manager


def get_cached_template(
    event_key: str,
    context: Dict[str, Any],
    channel: str = "email",
    website_id: Optional[int] = None,
    locale: str = "en",
    version: Optional[str] = None
) -> Optional[Tuple[str, str, str]]:
    """Get cached template if available."""
    manager = get_cache_manager()
    return manager.get_cached_template(
        event_key, context, channel, website_id, locale, version
    )


def cache_template(
    event_key: str,
    context: Dict[str, Any],
    content: Tuple[str, str, str],
    channel: str = "email",
    website_id: Optional[int] = None,
    locale: str = "en",
    version: Optional[str] = None,
    ttl: Optional[int] = None
):
    """Cache rendered template."""
    manager = get_cache_manager()
    manager.cache_template(
        event_key, context, content, channel, website_id, locale, version, ttl
    )
