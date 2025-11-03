# Generated migration for EditingRequirementConfig model
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_configs', '0002_initial'),
        ('websites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EditingRequirementConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enable_editing_by_default', models.BooleanField(default=True, help_text='Enable editing for orders by default (unless urgent or explicitly disabled)')),
                ('skip_editing_for_urgent', models.BooleanField(default=True, help_text='Skip editing for urgent orders (deadline < 24 hours or is_urgent=True)')),
                ('allow_editing_for_early_submissions', models.BooleanField(default=True, help_text='Allow editing for orders submitted before deadline')),
                ('early_submission_hours_threshold', models.PositiveIntegerField(default=24, help_text="Hours before deadline to consider submission 'early' (for editing eligibility)")),
                ('editing_required_for_first_orders', models.BooleanField(default=True, help_text="Require editing for client's first order")),
                ('editing_required_for_high_value', models.BooleanField(default=True, help_text='Require editing for high-value orders')),
                ('high_value_threshold', models.DecimalField(decimal_places=2, default=300.0, help_text="Order value threshold (USD) to consider 'high value'", max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='Admin who created this configuration', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_editing_configs', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website this configuration applies to', on_delete=django.db.models.deletion.CASCADE, related_name='editing_requirements', to='websites.website')),
            ],
            options={
                'verbose_name': 'Editing Requirement Config',
                'verbose_name_plural': 'Editing Requirement Configs',
                'unique_together': {('website',)},
            },
        ),
    ]

