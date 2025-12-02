# Generated manually
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('websites', '0001_initial'),
        ('users', '0006_merge_20251201_0817'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAlertPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify_new_login', models.BooleanField(default=True, help_text='Notify when a new login occurs')),
                ('notify_new_device', models.BooleanField(default=True, help_text='Notify when login from a new device')),
                ('notify_new_location', models.BooleanField(default=True, help_text='Notify when login from a new location')),
                ('email_enabled', models.BooleanField(default=True, help_text='Receive alerts via email')),
                ('push_enabled', models.BooleanField(default=False, help_text='Receive alerts via push notifications')),
                ('in_app_enabled', models.BooleanField(default=True, help_text='Receive alerts in-app')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='login_alert_preferences', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='login_alert_preferences', to='websites.website')),
            ],
            options={
                'verbose_name': 'Login Alert Preference',
                'verbose_name_plural': 'Login Alert Preferences',
                'unique_together': {('user', 'website')},
            },
        ),
        migrations.AddIndex(
            model_name='loginalertpreference',
            index=models.Index(fields=['user', 'website'], name='users_logina_user_id_idx'),
        ),
    ]

