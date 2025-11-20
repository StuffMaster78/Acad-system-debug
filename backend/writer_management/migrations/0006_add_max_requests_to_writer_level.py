# Manual migration: Add max_requests_per_writer to WriterLevel
# This moves the max_requests_per_writer setting from WriterConfig (global) to WriterLevel (per-level)
# Different writer levels can now have different request limits
# 
# Rationale: Writer configuration (max requests and max takes) should be coupled with writer levels
# so that different levels can have different capacity limits. This is more flexible and logical
# than having a single global setting for all writers regardless of their level.

from django.db import migrations, models


def migrate_max_requests_from_config(apps, schema_editor):
    """
    Migrate max_requests_per_writer values from WriterConfig to WriterLevel.
    For each website, copy the WriterConfig.max_requests_per_writer value to all WriterLevels for that website.
    
    This preserves existing configuration while moving it to the level-based system.
    """
    WriterLevel = apps.get_model('writer_management', 'WriterLevel')
    WriterConfig = apps.get_model('writer_management', 'WriterConfig')
    
    # For each WriterConfig, update all WriterLevels for that website
    for config in WriterConfig.objects.all():
        updated_count = WriterLevel.objects.filter(website=config.website).update(
            max_requests_per_writer=config.max_requests_per_writer
        )
        # If no levels exist for this website, the default value (5) will be used when levels are created


def reverse_migration(apps, schema_editor):
    """
    Reverse migration: Remove the field.
    Note: We cannot restore the old WriterConfig values, but the field will be removed.
    """
    # The field removal is handled by Django automatically when reversing
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0005_merge_20251118_0524'),
    ]

    operations = [
        # Add max_requests_per_writer field to WriterLevel
        migrations.AddField(
            model_name='writerlevel',
            name='max_requests_per_writer',
            field=models.PositiveIntegerField(
                default=5,
                help_text='Maximum number of order requests a writer can have at once.'
            ),
        ),
        # Migrate existing data from WriterConfig to WriterLevel
        migrations.RunPython(
            migrate_max_requests_from_config,
            reverse_migration,
        ),
    ]

