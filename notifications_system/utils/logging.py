"""
Enhanced logging utilities with correlation IDs and structured logging.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional
from django.conf import settings

# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class CorrelationIDFilter(logging.Filter):
    """Logging filter to add correlation ID to log records."""
    
    def filter(self, record):
        correlation_id = correlation_id_var.get()
        if correlation_id:
            record.correlation_id = correlation_id
        else:
            record.correlation_id = 'no-correlation-id'
        return True


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""
    
    def format(self, record):
        log_entry = {
            'timestamp': time.time(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', 'no-correlation-id'),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'correlation_id']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class NotificationLogger:
    """Specialized logger for notification system."""
    
    def __init__(self, name: str = 'notifications'):
        self.logger = logging.getLogger(name)
        self.logger.addFilter(CorrelationIDFilter())
    
    def log_notification_sent(
        self,
        notification_id: int,
        user_id: int,
        event_key: str,
        channels: list,
        duration: float,
        **kwargs
    ):
        """Log notification sent event."""
        self.logger.info(
            "Notification sent",
            extra={
                'notification_id': notification_id,
                'user_id': user_id,
                'event_key': event_key,
                'channels': channels,
                'duration_ms': duration * 1000,
                'event_type': 'notification_sent',
                **kwargs
            }
        )
    
    def log_notification_failed(
        self,
        notification_id: int,
        user_id: int,
        event_key: str,
        error: str,
        **kwargs
    ):
        """Log notification failure."""
        self.logger.error(
            "Notification failed",
            extra={
                'notification_id': notification_id,
                'user_id': user_id,
                'event_key': event_key,
                'error': error,
                'event_type': 'notification_failed',
                **kwargs
            }
        )
    
    def log_template_rendered(
        self,
        event_key: str,
        template_type: str,
        duration: float,
        **kwargs
    ):
        """Log template rendering."""
        self.logger.debug(
            "Template rendered",
            extra={
                'event_key': event_key,
                'template_type': template_type,
                'duration_ms': duration * 1000,
                'event_type': 'template_rendered',
                **kwargs
            }
        )
    
    def log_sse_connection(
        self,
        user_id: int,
        connection_id: str,
        action: str,
        **kwargs
    ):
        """Log SSE connection events."""
        self.logger.info(
            f"SSE connection {action}",
            extra={
                'user_id': user_id,
                'connection_id': connection_id,
                'action': action,
                'event_type': 'sse_connection',
                **kwargs
            }
        )
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'ms',
        **kwargs
    ):
        """Log performance metrics."""
        self.logger.info(
            "Performance metric",
            extra={
                'metric_name': metric_name,
                'value': value,
                'unit': unit,
                'event_type': 'performance_metric',
                **kwargs
            }
        )


def get_correlation_id() -> str:
    """Get current correlation ID."""
    correlation_id = correlation_id_var.get()
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
    return correlation_id


def set_correlation_id(correlation_id: str):
    """Set correlation ID for current context."""
    correlation_id_var.set(correlation_id)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def with_correlation_id(correlation_id: str):
    """Context manager to set correlation ID."""
    class CorrelationIDContext:
        def __init__(self, cid: str):
            self.correlation_id = cid
            self.old_correlation_id = None
        
        def __enter__(self):
            self.old_correlation_id = correlation_id_var.get()
            correlation_id_var.set(self.correlation_id)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.old_correlation_id:
                correlation_id_var.set(self.old_correlation_id)
            else:
                correlation_id_var.set(None)
    
    return CorrelationIDContext(correlation_id)


def log_notification_flow(
    step: str,
    notification_id: Optional[int] = None,
    user_id: Optional[int] = None,
    event_key: Optional[str] = None,
    **kwargs
):
    """Log notification flow steps."""
    logger = NotificationLogger()
    correlation_id = get_correlation_id()
    
    logger.logger.info(
        f"Notification flow: {step}",
        extra={
            'correlation_id': correlation_id,
            'step': step,
            'notification_id': notification_id,
            'user_id': user_id,
            'event_key': event_key,
            'event_type': 'notification_flow',
            **kwargs
        }
    )


def setup_notification_logging():
    """Setup notification system logging configuration."""
    # Create notification logger
    notification_logger = logging.getLogger('notifications')
    notification_logger.setLevel(logging.INFO)
    
    # Add correlation ID filter
    notification_logger.addFilter(CorrelationIDFilter())
    
    # Create console handler with structured formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    notification_logger.addHandler(console_handler)
    
    # Create file handler if configured
    log_file = getattr(settings, 'NOTIFICATION_LOG_FILE', None)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter())
        notification_logger.addHandler(file_handler)
    
    return notification_logger


# Global notification logger instance
notification_logger = NotificationLogger()
