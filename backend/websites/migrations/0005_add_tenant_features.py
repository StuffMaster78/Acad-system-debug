# Generated manually
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0004_add_admin_notifications_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantBranding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_subject_prefix', models.CharField(blank=True, help_text="Prefix for email subjects (e.g., '[YourSite]')", max_length=50)),
                ('email_reply_to', models.EmailField(blank=True, help_text='Reply-to address for emails')),
                ('email_from_name', models.CharField(blank=True, help_text="From name for emails (e.g., 'YourSite Support')", max_length=100)),
                ('email_from_address', models.EmailField(blank=True, help_text='From address for emails')),
                ('notification_subject_prefix', models.CharField(blank=True, help_text='Prefix for notification subjects', max_length=50)),
                ('email_logo_url', models.URLField(blank=True, help_text='Logo URL for email templates')),
                ('email_header_color', models.CharField(blank=True, help_text='Header color for emails (HEX)', max_length=7)),
                ('email_footer_text', models.TextField(blank=True, help_text='Footer text for emails')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='branding', to='websites.website')),
            ],
            options={
                'verbose_name': 'Tenant Branding',
                'verbose_name_plural': 'Tenant Branding',
            },
        ),
        migrations.CreateModel(
            name='TenantFeatureToggle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('magic_link_enabled', models.BooleanField(default=True, help_text='Allow magic link authentication')),
                ('two_factor_required', models.BooleanField(default=False, help_text='Require 2FA for all users')),
                ('password_reset_enabled', models.BooleanField(default=True, help_text='Allow password reset')),
                ('messaging_enabled', models.BooleanField(default=True, help_text='Enable messaging system')),
                ('messaging_types_allowed', models.JSONField(blank=True, default=list, help_text="Allowed messaging types: ['order_messages', 'direct_messages', 'group_messages']")),
                ('max_order_size_pages', models.PositiveIntegerField(blank=True, help_text='Maximum pages per order (null = unlimited)', null=True)),
                ('max_order_size_slides', models.PositiveIntegerField(blank=True, help_text='Maximum slides per order (null = unlimited)', null=True)),
                ('allow_order_drafts', models.BooleanField(default=True, help_text='Allow saving order drafts')),
                ('allow_order_presets', models.BooleanField(default=True, help_text='Allow order presets')),
                ('allow_writer_portfolios', models.BooleanField(default=True, help_text='Allow writer portfolios')),
                ('allow_writer_feedback', models.BooleanField(default=True, help_text='Allow feedback system')),
                ('allow_wallet', models.BooleanField(default=True, help_text='Allow wallet payments')),
                ('allow_advance_payments', models.BooleanField(default=True, help_text='Allow advance payments for writers')),
                ('allow_class_orders', models.BooleanField(default=True, help_text='Allow class/bulk orders')),
                ('allow_disputes', models.BooleanField(default=True, help_text='Allow order disputes')),
                ('allow_escalations', models.BooleanField(default=True, help_text='Allow escalation flows')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feature_toggles', to='websites.website')),
            ],
            options={
                'verbose_name': 'Tenant Feature Toggle',
                'verbose_name_plural': 'Tenant Feature Toggles',
            },
        ),
    ]

