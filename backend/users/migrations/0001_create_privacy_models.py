# Generated migration for privacy settings and data access log
# Run: python manage.py makemigrations users

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),  # Update with your latest migration
        ('websites', '0001_initial'),  # Update with your latest migration
    ]

    operations = [
        migrations.CreateModel(
            name='PrivacySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_visibility_to_writers', models.CharField(choices=[('public', 'Public'), ('limited', 'Limited'), ('private', 'Private'), ('hidden', 'Hidden')], default='limited', help_text='Profile visibility to writers', max_length=20)),
                ('profile_visibility_to_admins', models.CharField(choices=[('public', 'Public'), ('limited', 'Limited'), ('private', 'Private'), ('hidden', 'Hidden')], default='public', help_text='Profile visibility to administrators', max_length=20)),
                ('profile_visibility_to_support', models.CharField(choices=[('public', 'Public'), ('limited', 'Limited'), ('private', 'Private'), ('hidden', 'Hidden')], default='public', help_text='Profile visibility to support staff', max_length=20)),
                ('allow_analytics', models.BooleanField(default=True, help_text='Allow usage analytics')),
                ('allow_marketing', models.BooleanField(default=False, help_text='Allow marketing communications')),
                ('allow_third_party_sharing', models.BooleanField(default=False, help_text='Allow sharing data with third parties')),
                ('notify_on_login', models.BooleanField(default=True, help_text='Notify on new login')),
                ('notify_on_login_method', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')], default='email', help_text='Method for login notifications', max_length=10)),
                ('notify_on_suspicious_activity', models.BooleanField(default=True, help_text='Notify on suspicious activity')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(help_text='User these privacy settings belong to', on_delete=django.db.models.deletion.CASCADE, related_name='privacy_settings', to='users.user')),
            ],
            options={
                'verbose_name': 'Privacy Settings',
                'verbose_name_plural': 'Privacy Settings',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='DataAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_type', models.CharField(choices=[('profile_view', 'Profile View'), ('order_access', 'Order Access'), ('payment_access', 'Payment Access'), ('message_access', 'Message Access'), ('data_export', 'Data Export')], help_text='Type of data access', max_length=20)),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address of the access', null=True)),
                ('user_agent', models.TextField(blank=True, help_text='User agent of the access', null=True)),
                ('accessed_at', models.DateTimeField(auto_now_add=True, help_text='When the data was accessed')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional metadata about the access')),
                ('accessed_by', models.ForeignKey(blank=True, help_text='User who accessed the data', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_access_actions', to='users.user')),
                ('user', models.ForeignKey(help_text='User whose data was accessed', on_delete=django.db.models.deletion.CASCADE, related_name='data_access_logs', to='users.user')),
            ],
            options={
                'verbose_name': 'Data Access Log',
                'verbose_name_plural': 'Data Access Logs',
                'ordering': ['-accessed_at'],
            },
        ),
        migrations.AddIndex(
            model_name='dataaccesslog',
            index=models.Index(fields=['user', '-accessed_at'], name='users_dataa_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='dataaccesslog',
            index=models.Index(fields=['accessed_by', '-accessed_at'], name='users_dataa_access_idx'),
        ),
    ]

