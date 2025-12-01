# Generated migration for security events
# Run: python manage.py makemigrations authentication

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),  # Update with your latest migration
        ('users', '0001_initial'),  # Update with your latest migration
        ('websites', '0001_initial'),  # Update with your latest migration
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('login', 'Login'), ('login_failed', 'Failed Login'), ('logout', 'Logout'), ('password_change', 'Password Changed'), ('password_reset', 'Password Reset'), ('2fa_enabled', '2FA Enabled'), ('2fa_disabled', '2FA Disabled'), ('2fa_verified', '2FA Verified'), ('magic_link_used', 'Magic Link Used'), ('device_trusted', 'Device Trusted'), ('device_revoked', 'Device Revoked'), ('session_created', 'Session Created'), ('session_revoked', 'Session Revoked'), ('suspicious_activity', 'Suspicious Activity'), ('account_locked', 'Account Locked'), ('account_unlocked', 'Account Unlocked'), ('profile_updated', 'Profile Updated'), ('privacy_settings_changed', 'Privacy Settings Changed')], help_text='Type of security event', max_length=30)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='low', help_text='Severity of the event', max_length=10)),
                ('is_suspicious', models.BooleanField(default=False, help_text='Whether this event is suspicious')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address of the event', null=True)),
                ('location', models.CharField(blank=True, help_text='Geographic location (city, country)', max_length=255, null=True)),
                ('device', models.CharField(blank=True, help_text='Device information', max_length=255, null=True)),
                ('user_agent', models.TextField(blank=True, help_text='User agent string', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the event occurred')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional event metadata')),
                ('user', models.ForeignKey(help_text='User this event belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='security_events', to='users.user')),
                ('website', models.ForeignKey(help_text='Website this event occurred on', on_delete=django.db.models.deletion.CASCADE, related_name='security_events', to='websites.website')),
            ],
            options={
                'verbose_name': 'Security Event',
                'verbose_name_plural': 'Security Events',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='securityevent',
            index=models.Index(fields=['user', '-created_at'], name='authenticat_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='securityevent',
            index=models.Index(fields=['event_type', '-created_at'], name='authenticat_event_t_idx'),
        ),
        migrations.AddIndex(
            model_name='securityevent',
            index=models.Index(fields=['is_suspicious', '-created_at'], name='authenticat_is_susp_idx'),
        ),
    ]

