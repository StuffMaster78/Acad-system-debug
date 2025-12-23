"""
Signals to automatically track configuration changes.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from core.models.config_versioning import ConfigVersion
from core.services.config_versioning_service import ConfigVersioningService

# List of config models to track
CONFIG_MODELS = [
    'pricingconfiguration',
    'writerconfig',
    'discountconfig',
    'writerlevelconfig',
    'preferredwriterconfig',
    'revisionpolicyconfig',
    'editingrequirementconfig',
    'writerdeadlineconfig',
    'finetypeconfig',
    'referralbonusconfig',
    'paymentreminderconfig',
    'orderfilesconfig',
    'classbundleconfig',
    'predefinedspecialorderconfig',
]


def should_track_version(sender):
    """Check if a model should have versioning tracked."""
    model_name = sender._meta.model_name.lower()
    return model_name in CONFIG_MODELS


@receiver(post_save)
def track_config_save(sender, instance, created, **kwargs):
    """
    Automatically create a version when a config is saved.
    """
    if not should_track_version(sender):
        return
    
    # Skip if this is a migration or fixture load
    if kwargs.get('raw', False):
        return
    
    try:
        # Determine change type
        change_type = 'created' if created else 'updated'
        
        # Get previous version if updating
        previous_version = None
        if not created:
            content_type = ContentType.objects.get_for_model(sender)
            previous_version = ConfigVersion.get_current_version(
                content_type, instance.pk
            )
        
        # Get user from thread local or request (if available)
        # This is a simplified version - in production, you'd use middleware
        changed_by = getattr(instance, '_versioning_user', None)
        
        # Create version
        ConfigVersioningService.create_version(
            instance,
            change_type=change_type,
            changed_by=changed_by,
            previous_version=previous_version
        )
    except Exception as e:
        # Log error but don't break the save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating config version: {e}", exc_info=True)


@receiver(pre_delete)
def track_config_delete(sender, instance, **kwargs):
    """
    Create a version when a config is deleted (before deletion).
    """
    if not should_track_version(sender):
        return
    
    try:
        # Get current version before deletion
        content_type = ContentType.objects.get_for_model(sender)
        previous_version = ConfigVersion.get_current_version(
            content_type, instance.pk
        )
        
        # Get user from thread local (set by middleware) or instance attribute
        from core.middleware.config_versioning import get_current_user
        changed_by = getattr(instance, '_versioning_user', None) or get_current_user()
        
        # Create deletion version
        ConfigVersioningService.create_version(
            instance,
            change_type='deleted',
            changed_by=changed_by,
            previous_version=previous_version,
            change_summary="Configuration deleted"
        )
    except Exception as e:
        # Log error but don't break the delete
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating deletion version: {e}", exc_info=True)

