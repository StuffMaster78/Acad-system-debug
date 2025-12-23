"""
Service for managing configuration versioning.
Automatically creates versions when configs are created, updated, or deleted.
"""
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone
from core.models.config_versioning import ConfigVersion
import json


class ConfigVersioningService:
    """
    Service to handle configuration versioning.
    """
    
    @staticmethod
    def serialize_config(config_instance):
        """
        Serialize a config instance to JSON.
        Handles various field types including ForeignKeys, ManyToMany, etc.
        """
        from django.core.serializers import serialize
        
        # Get all fields from the model
        fields = {}
        for field in config_instance._meta.get_fields():
            field_name = field.name
            
            # Skip reverse relations and auto fields
            if field.auto_created or field_name in ['id', 'pk']:
                continue
            
            try:
                value = getattr(config_instance, field_name, None)
                
                # Handle different field types
                if hasattr(field, 'related_model'):  # ForeignKey, OneToOne
                    if value is not None:
                        fields[field_name] = {
                            'id': value.id,
                            'model': field.related_model.__name__,
                            'str': str(value)
                        }
                    else:
                        fields[field_name] = None
                elif hasattr(field, 'remote_field'):  # ManyToMany
                    if value is not None:
                        fields[field_name] = [item.id for item in value.all()]
                    else:
                        fields[field_name] = []
                elif isinstance(value, (str, int, float, bool, type(None))):
                    fields[field_name] = value
                elif isinstance(value, (list, dict)):
                    fields[field_name] = value
                else:
                    # Convert to string for other types
                    fields[field_name] = str(value) if value is not None else None
            except Exception:
                # Skip fields that can't be accessed
                continue
        
        return fields
    
    @staticmethod
    def get_changed_fields(old_data, new_data):
        """Compare two config data dictionaries and return changed fields."""
        changed = []
        
        # Get all unique keys
        all_keys = set(old_data.keys()) | set(new_data.keys())
        
        for key in all_keys:
            old_value = old_data.get(key)
            new_value = new_data.get(key)
            
            # Compare values (handle dict/list comparisons)
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                if old_value != new_value:
                    changed.append(key)
            elif isinstance(old_value, list) and isinstance(new_value, list):
                if old_value != new_value:
                    changed.append(key)
            elif old_value != new_value:
                changed.append(key)
        
        return changed
    
    @staticmethod
    @transaction.atomic
    def create_version(
        config_instance,
        change_type='updated',
        changed_by=None,
        change_summary=None,
        notes=None,
        previous_version=None
    ):
        """
        Create a new version of a configuration.
        
        Args:
            config_instance: The config model instance
            change_type: 'created', 'updated', 'deleted', or 'restored'
            changed_by: User who made the change
            change_summary: Summary of changes
            notes: Additional notes
            previous_version: Previous ConfigVersion instance (optional)
        """
        content_type = ContentType.objects.get_for_model(config_instance.__class__)
        object_id = config_instance.pk
        
        # Mark previous versions as not current
        ConfigVersion.objects.filter(
            content_type=content_type,
            object_id=object_id,
            is_current=True
        ).update(is_current=False)
        
        # Get next version number
        if previous_version:
            version_number = previous_version.version_number + 1
        else:
            version_number = ConfigVersion.get_next_version_number(
                content_type, object_id
            )
        
        # Serialize current config state
        config_data = ConfigVersioningService.serialize_config(config_instance)
        
        # Get changed fields if previous version exists
        changed_fields = []
        if previous_version:
            changed_fields = ConfigVersioningService.get_changed_fields(
                previous_version.config_data,
                config_data
            )
        
        # Get user from thread local (set by middleware) or instance attribute if not provided
        if changed_by is None:
            from core.middleware.config_versioning import get_current_user
            changed_by = getattr(instance, '_versioning_user', None) or get_current_user()
        
        # Create version
        version = ConfigVersion.objects.create(
            content_type=content_type,
            object_id=object_id,
            version_number=version_number,
            created_by=changed_by,
            config_data=config_data,
            change_type=change_type,
            change_summary=change_summary or f"{change_type.title()} configuration",
            changed_fields=changed_fields,
            previous_version=previous_version,
            notes=notes,
            is_current=True
        )
        
        return version
    
    @staticmethod
    def restore_version(version, restored_by=None, notes=None):
        """
        Restore a configuration to a previous version.
        
        Args:
            version: ConfigVersion instance to restore
            restored_by: User restoring the version
            notes: Notes about the restoration
        """
        if not version.config_object:
            raise ValueError("Cannot restore: config object no longer exists")
        
        config_instance = version.config_object
        
        # Restore fields from version data
        for field_name, field_value in version.config_data.items():
            if hasattr(config_instance, field_name):
                field = config_instance._meta.get_field(field_name)
                
                # Handle ForeignKey fields
                if hasattr(field, 'related_model') and isinstance(field_value, dict):
                    related_model = field.related_model
                    related_id = field_value.get('id')
                    if related_id:
                        try:
                            related_obj = related_model.objects.get(id=related_id)
                            setattr(config_instance, field_name, related_obj)
                        except related_model.DoesNotExist:
                            pass
                # Handle ManyToMany fields (set after save)
                elif hasattr(field, 'remote_field') and isinstance(field_value, list):
                    # Will be handled after save
                    pass
                # Handle regular fields
                else:
                    try:
                        setattr(config_instance, field_name, field_value)
                    except Exception:
                        pass
        
        # Save the instance
        config_instance.save()
        
        # Handle ManyToMany fields
        for field_name, field_value in version.config_data.items():
            if isinstance(field_value, list):
                field = config_instance._meta.get_field(field_name)
                if hasattr(field, 'remote_field'):  # ManyToMany
                    try:
                        related_model = field.remote_field.model
                        related_objects = related_model.objects.filter(id__in=field_value)
                        getattr(config_instance, field_name).set(related_objects)
                    except Exception:
                        pass
        
        # Create a new version for the restoration
        return ConfigVersioningService.create_version(
            config_instance,
            change_type='restored',
            changed_by=restored_by,
            change_summary=f"Restored to version {version.version_number}",
            notes=notes or f"Restored from version {version.version_number}",
            previous_version=ConfigVersion.get_current_version(
                ContentType.objects.get_for_model(config_instance.__class__),
                config_instance.pk
            )
        )

