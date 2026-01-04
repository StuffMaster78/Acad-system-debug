"""
Structured Logging Configuration for Writing System

This module provides structured logging configuration with:
- Log rotation to prevent disk space issues
- Separate handlers for different log levels
- JSON formatting for production (optional)
- Console output for development
"""

import os
import logging
from pathlib import Path

# Base directory for log files
# Try system log directory first, fallback to project directory if no permission
LOG_DIR_DEFAULT = '/var/log/writing-system'
LOG_DIR_ENV = os.getenv('LOG_DIR', LOG_DIR_DEFAULT)
LOG_DIR = Path(LOG_DIR_ENV)

# Try to create log directory, fallback to project logs if permission denied
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR_CREATED = False

try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR_CREATED = True
except (PermissionError, OSError):
    # Fallback 1: Try /app/logs (Docker container app directory)
    try:
        LOG_DIR = Path('/app/logs')
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR_CREATED = True
    except (PermissionError, OSError):
        # Fallback 2: Try project-relative logs directory
        try:
            LOG_DIR = BASE_DIR / 'logs'
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            LOG_DIR_CREATED = True
        except (PermissionError, OSError):
            # Fallback 3: Use /tmp (usually writable in containers)
            try:
                LOG_DIR = Path('/tmp/writing-system-logs')
                LOG_DIR.mkdir(parents=True, exist_ok=True)
                LOG_DIR_CREATED = True
            except (PermissionError, OSError):
                # Last resort: Disable file logging, use console only
                LOG_DIR = None
                LOG_DIR_CREATED = False
                import warnings
                if os.getenv('DEBUG', 'False') == 'True':
                    warnings.warn(
                        f"Could not create log directory. File logging disabled. "
                        f"Logs will only go to console.",
                        RuntimeWarning
                    )

# Determine log level from environment
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
DEBUG = os.getenv('DEBUG', 'False') == 'True'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # Reduce database query logging noise
            'propagate': False,
        },
        'writing_system': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery.task': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Only add file handlers if log directory was successfully created
if LOG_DIR_CREATED and LOG_DIR is not None:
    LOGGING['handlers'].update({
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'app.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 10,  # Keep 10 backup files
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'error.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'django_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    })
    
    # Update root and logger handlers to include file handlers
    LOGGING['root']['handlers'] = ['console', 'file', 'error_file']
    LOGGING['loggers']['django']['handlers'] = ['console', 'django_file', 'error_file']
    LOGGING['loggers']['writing_system']['handlers'] = ['console', 'file', 'error_file']
    LOGGING['loggers']['celery']['handlers'] = ['console', 'file', 'error_file']
    LOGGING['loggers']['celery.task']['handlers'] = ['console', 'file', 'error_file']
else:
    # If file logging is disabled, only use console
    LOGGING['root']['handlers'] = ['console']
    LOGGING['loggers']['django']['handlers'] = ['console']
    LOGGING['loggers']['django.request']['handlers'] = ['console']
    LOGGING['loggers']['django.server']['handlers'] = ['console']
    LOGGING['loggers']['writing_system']['handlers'] = ['console']
    LOGGING['loggers']['celery']['handlers'] = ['console']
    LOGGING['loggers']['celery.task']['handlers'] = ['console']

