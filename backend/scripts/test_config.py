#!/usr/bin/env python
"""
Test script to verify deployment configuration
Run this to check if all settings are properly configured
"""

import os
import sys
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def test_database_config():
    """Test database configuration"""
    print(" Testing database configuration...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print(" Database connection: OK")

                # Check connection pooling
                conn_max_age = settings.DATABASES['default'].get('CONN_MAX_AGE', 0)
                if conn_max_age > 0:
                    print(f" Connection pooling: Enabled (max age: {conn_max_age}s)")
                else:
                    print(" ️ Connection pooling: Not configured")

                # Check query timeout
                options = settings.DATABASES['default'].get('OPTIONS', {})
                if 'options' in options and 'statement_timeout' in options['options']:
                    print(" Query timeout: Configured")
                else:
                    print(" ️ Query timeout: Not configured")

                return True
    except Exception as e:
        print(f" Database connection failed: {e}")
        return False

def test_redis_config():
    """Test Redis configuration"""
    print("\n Testing Redis configuration...")
    try:
        cache.set('test_key', 'test_value', 10)
        value = cache.get('test_key')
        if value == 'test_value':
            print(" Redis connection: OK")

            # Check connection pooling
            cache_options = settings.CACHES['default'].get('OPTIONS', {})
            pool_kwargs = cache_options.get('CONNECTION_POOL_KWARGS', {})
            if pool_kwargs:
                max_conn = pool_kwargs.get('max_connections', 0)
                if max_conn > 0:
                    print(f" Connection pooling: Enabled (max: {max_conn})")
                else:
                    print(" ️ Connection pooling: Not configured")
            else:
                print(" ️ Connection pooling: Not configured")

            cache.delete('test_key')
            return True
    except Exception as e:
        print(f" Redis connection failed: {e}")
        return False

def test_logging_config():
    """Test logging configuration"""
    print("\n Testing logging configuration...")
    try:
        # Check if LOGGING is configured
        if hasattr(settings, 'LOGGING') and settings.LOGGING:
            print(" Logging configuration: Found")

            # Check handlers
            handlers = settings.LOGGING.get('handlers', {})
            if 'file' in handlers or 'error_file' in handlers:
                print(" File logging: Configured")
            else:
                print(" ️ File logging: Not configured")

            if 'console' in handlers:
                print(" Console logging: Configured")

            return True
        else:
            print(" ️ Logging configuration: Not found (using defaults)")
            return False
    except Exception as e:
        print(f" Logging configuration error: {e}")
        return False

def test_environment_validation():
    """Test environment variable validation"""
    print("\n Testing environment variable validation...")
    try:
        # Check if validation function exists
        from writing_system.settings import get_required_env

        # Check critical variables (in production mode)
        if not settings.DEBUG:
            required_vars = ['SECRET_KEY', 'POSTGRES_DB_NAME', 'POSTGRES_USER_NAME', 'POSTGRES_PASSWORD']
            missing = []
            for var in required_vars:
                value = os.getenv(var)
                if not value or value == '':
                    missing.append(var)

            if missing:
                print(f" ️ Missing required variables: {', '.join(missing)}")
                return False
            else:
                print(" Environment variables: All required variables set")
        else:
            print(" ℹ️ Environment validation: Skipped (DEBUG mode)")

        return True
    except Exception as e:
        print(f" Environment validation error: {e}")
        return False

def test_celery_config():
    """Test Celery configuration"""
    print("\n Testing Celery configuration...")
    try:
        # Check Celery settings
        task_time_limit = getattr(settings, 'CELERY_TASK_TIME_LIMIT', None)
        task_soft_time_limit = getattr(settings, 'CELERY_TASK_SOFT_TIME_LIMIT', None)

        if task_time_limit:
            print(f" Task time limit: {task_time_limit}s")
        else:
            print(" ️ Task time limit: Not configured")

        if task_soft_time_limit:
            print(f" Task soft time limit: {task_soft_time_limit}s")
        else:
            print(" ️ Task soft time limit: Not configured")

        return True
    except Exception as e:
        print(f" Celery configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print(" Testing Deployment Configuration")
    print("=" * 60)
    print()

    results = []

    # Run tests
    results.append(("Database", test_database_config()))
    results.append(("Redis", test_redis_config()))
    results.append(("Logging", test_logging_config()))
    results.append(("Environment", test_environment_validation()))
    results.append(("Celery", test_celery_config()))

    # Summary
    print("\n" + "=" * 60)
    print(" Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = " PASS" if result else " FAIL"
        print(f" {status}: {name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n All configuration tests passed!")
        return 0
    else:
        print("\n️ Some configuration tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

