from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("websites", "0003_merge_20251201_0817"),
    ]

    operations = [
        migrations.AddField(
            model_name="website",
            name="admin_notifications_email",
            field=models.EmailField(
                max_length=254,
                null=True,
                blank=True,
                help_text="Email where critical order & payment notifications are forwarded for this website (e.g., a Gmail inbox for admins).",
            ),
        ),
    ]


