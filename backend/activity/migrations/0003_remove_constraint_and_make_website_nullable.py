# Generated manually to remove constraint and make website nullable

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0002_initial'),
        ('websites', '0001_initial'),
    ]

    operations = [
        # Remove the unique constraint first (if it exists)
        migrations.RemoveConstraint(
            model_name='activitylog',
            name='unique_activity_log_per_user_website_action',
        ),
        # Then make website nullable
        migrations.AlterField(
            model_name='activitylog',
            name='website',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='activity_logs',
                to='websites.website'
            ),
        ),
    ]

