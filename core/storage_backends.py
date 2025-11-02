"""
Custom storage backends for cloud file storage (DigitalOcean Spaces, AWS S3, Azure, GCS).
Supports multi-tenant file organization and security.
"""
from django.conf import settings
import os


# Storage backend: 'do_spaces', 's3', or 'local'
STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'local')

if STORAGE_BACKEND in ['do_spaces', 's3']:
    try:
        from storages.backends.s3boto3 import S3Boto3Storage
    except ImportError:
        # django-storages not installed, fall back to default
        from django.core.files.storage import FileSystemStorage as S3Boto3Storage

    class MediaStorage(S3Boto3Storage):
        """
        Storage backend for media files (user uploads).
        Organizes files by website/tenant for isolation.
        All files are private and accessed via signed URLs.
        """
        location = 'media'
        default_acl = 'private'
        file_overwrite = False
        
        def get_valid_name(self, name):
            """Add website prefix for multi-tenant isolation."""
            # Try to get website from context
            try:
                from core.tenant_context import get_current_website
                website = get_current_website()
                if website:
                    # Organize by website: media/website-slug/...
                    # Use website slug or ID for folder structure
                    website_identifier = getattr(website, 'slug', None) or f'website-{website.id}'
                    if not name.startswith(f'{website_identifier}/'):
                        name = f'{website_identifier}/{name}'
            except (ImportError, AttributeError, Exception):
                # If tenant context not available, continue without prefix
                pass
            
            return super().get_valid_name(name)
        
        def url(self, name, parameters=None, expire=3600):
            """
            Generate signed URL for private files.
            Default expiry: 1 hour (3600 seconds)
            """
            # Increase expiry for certain file types if needed
            if isinstance(name, str):
                if name.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
                    expire = 3600 * 24  # 24 hours for documents
                elif name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    expire = 3600 * 12  # 12 hours for images
            
            try:
                return super().url(name, parameters=parameters, expire=expire)
            except Exception:
                # Fallback to default if signed URL generation fails
                return super().url(name, parameters=parameters)

    class StaticStorage(S3Boto3Storage):
        """
        Storage backend for static files (CSS, JS, images).
        These can be public for better CDN performance.
        """
        location = 'static'
        default_acl = 'public-read'  # Static files can be public
        file_overwrite = True

    class PublicMediaStorage(S3Boto3Storage):
        """
        For public media files (blog images, public assets).
        Use when you want files accessible without signed URLs.
        """
        location = 'public-media'
        default_acl = 'public-read'
        file_overwrite = False

else:
    # Fallback to default storage if S3 not enabled
    from django.core.files.storage import FileSystemStorage
    
    class MediaStorage(FileSystemStorage):
        """Local filesystem storage for development."""
        pass
    
    class StaticStorage(FileSystemStorage):
        """Local filesystem storage for static files."""
        pass
    
    class PublicMediaStorage(FileSystemStorage):
        """Local filesystem storage for public media."""
        pass

