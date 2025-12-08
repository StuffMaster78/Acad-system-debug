"""
Enhanced response compression middleware.
Provides optimized GZip compression for API responses with better control.
"""

import gzip
import logging
from io import BytesIO
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)

# Cache key prefix for compression monitoring
COMPRESSION_MONITOR_PREFIX = 'compression_monitor:'

# Compression settings
COMPRESS_MIN_LENGTH = getattr(settings, 'COMPRESS_MIN_LENGTH', 200)  # Minimum size to compress (bytes)
COMPRESS_LEVEL = getattr(settings, 'COMPRESS_LEVEL', 6)  # Compression level (1-9, 6 is good balance)
COMPRESS_MIMETYPES = getattr(settings, 'COMPRESS_MIMETYPES', [
    'text/html',
    'text/css',
    'text/xml',
    'text/javascript',
    'application/javascript',
    'application/json',
    'application/xml',
    'application/xml+rss',
    'application/rss+xml',
    'application/atom+xml',
    'application/vnd.api+json',  # JSON API
    'text/plain',
    'text/csv',
    'application/vnd.ms-excel',
])

# Content types that should NOT be compressed
COMPRESS_EXCLUDE_TYPES = getattr(settings, 'COMPRESS_EXCLUDE_TYPES', [
    'image/',
    'video/',
    'audio/',
    'application/pdf',
    'application/zip',
    'application/gzip',
    'application/x-gzip',
    'application/x-tar',
    'application/octet-stream',
])


class EnhancedCompressionMiddleware(MiddlewareMixin):
    """
    Enhanced compression middleware with better control and optimization.
    
    Features:
    - Configurable compression level
    - Minimum size threshold
    - Content-type filtering
    - Compression ratio tracking
    - Better header handling
    """
    
    def process_response(self, request, response):
        """
        Compress response if appropriate.
        """
        # Skip compression for certain conditions
        if not self._should_compress(request, response):
            return response
        
        # Check if client accepts gzip
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in accept_encoding.lower():
            return response
        
        # Don't compress if already compressed
        if response.get('Content-Encoding', '').lower() == 'gzip':
            return response
        
        # Get response content
        content = response.content
        if not content:
            return response
        
        # Check minimum length
        if len(content) < COMPRESS_MIN_LENGTH:
            return response
        
        # Compress content
        try:
            compressed_content = self._compress_content(content)
            
            # Only use compressed version if it's actually smaller
            if len(compressed_content) < len(content):
                response.content = compressed_content
                response['Content-Encoding'] = 'gzip'
                response['Content-Length'] = str(len(compressed_content))
                response['Vary'] = 'Accept-Encoding'
                
                # Add compression info header (for monitoring)
                compression_ratio = (1 - len(compressed_content) / len(content)) * 100
                response['X-Compression-Ratio'] = f"{compression_ratio:.1f}%"
                response['X-Original-Size'] = str(len(content))
                response['X-Compressed-Size'] = str(len(compressed_content))
            else:
                # Compression didn't help, use original
                logger.debug(f"Compression not beneficial for {request.path}")
        except Exception as e:
            logger.warning(f"Compression failed for {request.path}: {e}")
            # Return original response on error
            return response
        
        return response
    
    def _should_compress(self, request, response):
        """
        Determine if response should be compressed.
        """
        # Skip compression for streaming responses
        if hasattr(response, 'streaming') and response.streaming:
            return False
        
        # Skip compression for certain status codes
        if response.status_code not in [200, 201, 202, 203, 204, 206]:
            return False
        
        # Check content type
        content_type = response.get('Content-Type', '').lower()
        if not content_type:
            return False
        
        # Exclude certain content types
        for exclude_type in COMPRESS_EXCLUDE_TYPES:
            if exclude_type in content_type:
                return False
        
        # Include only specified MIME types
        for mime_type in COMPRESS_MIMETYPES:
            if mime_type in content_type:
                return True
        
        return False
    
    def _compress_content(self, content):
        """
        Compress content using gzip.
        """
        buffer = BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=COMPRESS_LEVEL) as gz_file:
            gz_file.write(content)
        return buffer.getvalue()
    
    def _log_compression(self, request, original_size, compressed_size):
        """
        Log compression statistics for monitoring.
        """
        try:
            from django.core.cache import cache
            from django.conf import settings
            
            cache_key = f"{COMPRESSION_MONITOR_PREFIX}recent"
            compression_data = cache.get(cache_key, [])
            
            compression_data.append({
                'endpoint': request.path,
                'method': request.method,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'saved': original_size - compressed_size,
                'ratio': ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0,
            })
            
            # Keep only last 10000 compressions
            if len(compression_data) > 10000:
                compression_data = compression_data[-10000:]
            
            # Store in cache (24 hour TTL)
            cache.set(cache_key, compression_data, timeout=86400)
        except Exception as e:
            # Don't fail if logging fails
            logger.debug(f"Failed to log compression: {e}")


class APICompressionMiddleware(MiddlewareMixin):
    """
    Specialized compression middleware for API endpoints.
    More aggressive compression for JSON responses.
    """
    
    def process_response(self, request, response):
        """
        Compress API responses with optimized settings.
        """
        # Only process API endpoints
        if not request.path.startswith('/api/'):
            return response
        
        # Use enhanced compression for API
        middleware = EnhancedCompressionMiddleware()
        return middleware.process_response(request, response)

