# Generated migration for adding GenericForeignKey fields to CommunicationThread
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('communications', '0004_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='communicationthread',
            name='content_type',
            field=models.ForeignKey(
                blank=True,
                help_text='Content type for generic relation (e.g., ClassBundle)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='contenttypes.contenttype'
            ),
        ),
        migrations.AddField(
            model_name='communicationthread',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]

