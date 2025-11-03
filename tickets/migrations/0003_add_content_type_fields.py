# Generated migration for Ticket GenericForeignKey fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('tickets', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]

