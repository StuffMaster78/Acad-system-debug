"""
Circuit Breaker pattern implementation for resilient service calls.
Prevents cascading failures by stopping requests to failing services.
"""
import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascading failures.
    
    Usage:
        breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=ConnectionError
        )
        
        @breaker
        def call_external_service():
            # Your service call
            pass
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception,
        cache_key_prefix: str = "circuit_breaker"
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Unique name for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting half-open
            expected_exception: Exception type that indicates failure
            cache_key_prefix: Prefix for cache keys
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.cache_key_prefix = cache_key_prefix
        self.state_key = f"{cache_key_prefix}:{name}:state"
        self.failure_count_key = f"{cache_key_prefix}:{name}:failures"
        self.last_failure_key = f"{cache_key_prefix}:{name}:last_failure"
    
    def _get_state(self) -> CircuitState:
        """Get current circuit state."""
        state_str = cache.get(self.state_key, CircuitState.CLOSED.value)
        return CircuitState(state_str)
    
    def _set_state(self, state: CircuitState):
        """Set circuit state."""
        cache.set(self.state_key, state.value, timeout=self.timeout * 2)
    
    def _get_failure_count(self) -> int:
        """Get current failure count."""
        return cache.get(self.failure_count_key, 0)
    
    def _increment_failure(self):
        """Increment failure count."""
        count = self._get_failure_count() + 1
        cache.set(self.failure_count_key, count, timeout=self.timeout * 2)
        cache.set(self.last_failure_key, time.time(), timeout=self.timeout * 2)
        
        if count >= self.failure_threshold:
            self._set_state(CircuitState.OPEN)
            logger.warning(
                f"Circuit breaker '{self.name}' opened after {count} failures"
            )
    
    def _reset_failures(self):
        """Reset failure count."""
        cache.delete(self.failure_count_key)
        cache.delete(self.last_failure_key)
    
    def _should_attempt_half_open(self) -> bool:
        """Check if we should attempt half-open state."""
        last_failure = cache.get(self.last_failure_key)
        if not last_failure:
            return True
        
        return (time.time() - last_failure) >= self.timeout
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap function with circuit breaker."""
        def wrapper(*args, **kwargs) -> Any:
            state = self._get_state()
            
            # Circuit is open - reject request
            if state == CircuitState.OPEN:
                if self._should_attempt_half_open():
                    # Try half-open
                    self._set_state(CircuitState.HALF_OPEN)
                    logger.info(f"Circuit breaker '{self.name}' attempting half-open")
                else:
                    # Still in timeout period
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is open. Service unavailable."
                    )
            
            # Try the function
            try:
                result = func(*args, **kwargs)
                
                # Success - reset failures and close circuit
                if state == CircuitState.HALF_OPEN:
                    self._set_state(CircuitState.CLOSED)
                    self._reset_failures()
                    logger.info(f"Circuit breaker '{self.name}' closed after successful call")
                elif state == CircuitState.CLOSED:
                    self._reset_failures()
                
                return result
                
            except self.expected_exception as e:
                # Expected failure - increment counter
                self._increment_failure()
                logger.warning(
                    f"Circuit breaker '{self.name}' recorded failure: {e}"
                )
                raise
            except Exception as e:
                # Unexpected exception - log but don't count as circuit breaker failure
                logger.error(
                    f"Circuit breaker '{self.name}' unexpected error: {e}"
                )
                raise
        
        return wrapper


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


# Pre-configured circuit breakers for common services
database_breaker = CircuitBreaker(
    name="database",
    failure_threshold=5,
    timeout=30,
    expected_exception=Exception
)

cache_breaker = CircuitBreaker(
    name="cache",
    failure_threshold=10,
    timeout=30,
    expected_exception=Exception
)

email_breaker = CircuitBreaker(
    name="email",
    failure_threshold=5,
    timeout=60,
    expected_exception=Exception
)

