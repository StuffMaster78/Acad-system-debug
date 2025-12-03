# Generated migration for security features

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_add_login_alerts'),
        ('websites', '0006_enhance_file_versioning'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add email_verified field to User
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(
                default=False,
                help_text='Whether the user has verified their email address'
            ),
        ),
    ]

