from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("writer_management", "0003_add_badge_and_writerbadge"),
    ]

    operations = [
        migrations.AddField(
            model_name="writerlevelsettings",
            name="max_warnings",
            field=models.PositiveIntegerField(
                default=3,
                help_text="Maximum active warnings before a writer at this tier is eligible for demotion.",
            ),
        ),
    ]
