# Generated migration for EditorProfile missing fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor_management', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='editorprofile',
            name='can_self_assign',
            field=models.BooleanField(default=True, help_text='Whether editor can claim orders themselves.'),
        ),
        migrations.AddField(
            model_name='editorprofile',
            name='max_concurrent_tasks',
            field=models.PositiveIntegerField(default=5, help_text='Maximum number of concurrent editing tasks.'),
        ),
    ]

