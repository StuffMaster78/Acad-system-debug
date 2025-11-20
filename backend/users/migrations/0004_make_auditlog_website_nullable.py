# Generated manually to make website nullable in UserAuditLog

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_user'),
        ('websites', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userauditlog',
            name='website',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='audit_logs',
                to='websites.website'
            ),
        ),
    ]

