# Generated migration for adding pen_name field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0002_add_tip_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='writerprofile',
            name='pen_name',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text="Pen name visible to clients (instead of real name)"
            ),
        ),
    ]

