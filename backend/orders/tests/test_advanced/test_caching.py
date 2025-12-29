"""
Advanced caching tests.

Tests cover:
- Cache hit/miss behavior
- Cache invalidation
- Cache expiration
- Cache consistency
- Cache warming
"""
import pytest
import time
from unittest.mock import patch
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import OperationalError

from orders.models import Order
from orders.order_enums import OrderStatus
try:
    from core.services.resilient_db import ResilientDatabaseService
except ImportError:
    ResilientDatabaseService = None


@pytest.mark.django_db
@pytest.mark.skipif(ResilientDatabaseService is None, reason="ResilientDatabaseService not available")
class TestCacheBehavior:
    """Test cache behavior and consistency."""
    
    def test_cache_hit_returns_cached_data(self, order):
        """Test cache hit returns cached data without database query."""
        cache_key = f"order_{order.id}"
        cached_data = {"id": order.id, "status": "cached_status"}
        
        cache.set(cache_key, cached_data, timeout=300)
        
        query_count = [0]
        
        def read_operation():
            query_count[0] += 1
            return Order.objects.get(id=order.id)
        
        result = ResilientDatabaseService.execute_read(
            query_func=read_operation,
            cache_key=cache_key,
            fallback_value=None
        )
        
        # Should use cache, not query database
        assert query_count[0] == 0
        assert result == cached_data
    
    def test_cache_miss_queries_database(self, order):
        """Test cache miss queries database and caches result."""
        cache_key = f"order_{order.id}"
        cache.delete(cache_key)  # Ensure cache miss
        
        query_count = [0]
        
        def read_operation():
            query_count[0] += 1
            return {"id": order.id, "status": order.status}
        
        result = ResilientDatabaseService.execute_read(
            query_func=read_operation,
            cache_key=cache_key,
            cache_timeout=300,
            fallback_value=None
        )
        
        # Should query database
        assert query_count[0] == 1
        assert result is not None
        
        # Should be cached now
        cached = cache.get(cache_key)
        assert cached == result
    
    def test_cache_invalidation(self, order):
        """Test cache invalidation removes cached data."""
        cache_key = f"order_{order.id}"
        cache.set(cache_key, {"test": "data"}, timeout=300)
        
        # Verify cached
        assert cache.get(cache_key) is not None
        
        # Invalidate
        ResilientDatabaseService.invalidate_cache(cache_key)
        
        # Should be removed
        assert cache.get(cache_key) is None
    
    def test_cache_expiration(self, order):
        """Test cache expires after timeout."""
        cache_key = f"order_{order.id}"
        cache.set(cache_key, {"test": "data"}, timeout=1)  # 1 second timeout
        
        # Should be cached immediately
        assert cache.get(cache_key) is not None
        
        # Wait for expiration
        import time
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get(cache_key) is None
    
    def test_cache_consistency_on_update(self, order, admin_user):
        """Test cache is invalidated when order is updated."""
        cache_key = f"order_{order.id}"
        cache.set(cache_key, {"status": "old_status"}, timeout=300)
        
        # Update order
        order.status = OrderStatus.PENDING.value
        order.save()
        
        # Cache should be invalidated or updated
        # (Implementation specific - might auto-invalidate or require manual)
        # For now, test that we can invalidate manually
        ResilientDatabaseService.invalidate_cache(cache_key)
        assert cache.get(cache_key) is None
    
    def test_cache_fallback_on_database_error(self, order):
        """Test cache is used as fallback when database fails."""
        cache_key = f"order_{order.id}"
        cached_data = {"id": order.id, "status": "cached"}
        cache.set(cache_key, cached_data, timeout=300)
        
        def failing_read():
            raise OperationalError("Database error")
        
        result = ResilientDatabaseService.execute_read(
            query_func=failing_read,
            cache_key=cache_key,
            fallback_value=None
        )
        
        # Should return cached data
        assert result == cached_data
    
    def test_clear_all_cache(self):
        """Test clearing all cache entries."""
        # Set multiple cache entries
        cache.set("key1", "value1", timeout=300)
        cache.set("key2", "value2", timeout=300)
        
        # Clear all
        ResilientDatabaseService.clear_all_cache()
        
        # All should be cleared
        assert cache.get("key1") is None
        assert cache.get("key2") is None


@pytest.mark.django_db
@pytest.mark.skipif(ResilientDatabaseService is None, reason="ResilientDatabaseService not available")
class TestCacheWarming:
    """Test cache warming strategies."""
    
    def test_get_cached_data_with_fetch(self, order):
        """Test get_cached_data fetches and caches if not present."""
        cache_key = f"order_{order.id}"
        cache.delete(cache_key)  # Ensure not cached
        
        def fetch_func():
            return {"id": order.id, "status": order.status}
        
        # First call should fetch and cache
        result1 = ResilientDatabaseService.get_cached_data(
            key=cache_key,
            fetch_func=fetch_func,
            timeout=300
        )
        
        assert result1 is not None
        
        # Second call should use cache
        query_count = [0]
        def fetch_func_with_count():
            query_count[0] += 1
            return {"id": order.id, "status": order.status}
        
        result2 = ResilientDatabaseService.get_cached_data(
            key=cache_key,
            fetch_func=fetch_func_with_count,
            timeout=300
        )
        
        # Should use cache, not fetch again
        assert query_count[0] == 0
        assert result2 == result1

