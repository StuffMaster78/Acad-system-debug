# Generated migration for adding editing-related fields to Order model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='requires_editing',
            field=models.BooleanField(
                blank=True,
                default=None,
                help_text='Admin-controlled: Whether this order must undergo editing. None = use default/config rules, True = force editing, False = skip editing',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='editing_skip_reason',
            field=models.CharField(
                blank=True,
                help_text="Reason why editing was skipped (e.g., 'Urgent order', 'Admin disabled')",
                max_length=255,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='submitted_at',
            field=models.DateTimeField(
                blank=True,
                help_text="Date and time when the writer submitted/uploaded the order.",
                null=True
            ),
        ),
        # Note: is_urgent already exists in 0001_initial.py, so it's not included here
    ]

