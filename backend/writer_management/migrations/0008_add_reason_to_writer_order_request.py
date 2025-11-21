# Generated migration - Add reason field to WriterOrderRequest
from django.db import migrations, models


def set_default_reason(apps, schema_editor):
    """Set a default reason for existing records"""
    WriterOrderRequest = apps.get_model('writer_management', 'WriterOrderRequest')
    WriterOrderRequest.objects.filter(reason__isnull=True).update(
        reason='Requested by writer (reason not provided)'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0007_orderdispute_writerautoranking_writermessage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='writerorderrequest',
            name='reason',
            field=models.TextField(
                help_text="Writer's reason for requesting this order (e.g., expertise, availability, interest).",
                null=True,  # Allow null initially for existing records
                blank=True,
            ),
        ),
        migrations.RunPython(set_default_reason, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='writerorderrequest',
            name='reason',
            field=models.TextField(
                help_text="Writer's reason for requesting this order (e.g., expertise, availability, interest).",
                null=False,
                blank=False,
            ),
        ),
    ]

