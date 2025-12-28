# Generated migration for adding communication widget fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0008_set_guest_checkout_safe_defaults'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='enable_live_chat',
            field=models.BooleanField(default=False, help_text='Enable live chat widget on the website'),
        ),
        migrations.AddField(
            model_name='website',
            name='tawkto_widget_id',
            field=models.CharField(blank=True, help_text='Tawk.to widget ID (found in Tawk.to dashboard under Administration > Property Settings)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='website',
            name='tawkto_property_id',
            field=models.CharField(blank=True, help_text='Tawk.to property ID (optional, for multi-property setups)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='website',
            name='communication_widget_type',
            field=models.CharField(blank=True, choices=[('tawkto', 'Tawk.to'), ('intercom', 'Intercom'), ('zendesk', 'Zendesk Chat'), ('custom', 'Custom Widget')], help_text='Type of communication widget to use', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='website',
            name='communication_widget_config',
            field=models.JSONField(blank=True, default=dict, help_text='Additional configuration for communication widgets (JSON format)'),
        ),
    ]

