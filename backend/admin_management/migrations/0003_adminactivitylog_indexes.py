from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_management", "0002_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="adminactivitylog",
            index=models.Index(fields=["timestamp"], name="adminlog_timestamp_idx"),
        ),
        migrations.AddIndex(
            model_name="adminactivitylog",
            index=models.Index(fields=["admin", "timestamp"], name="adminlog_admin_timestamp_idx"),
        ),
    ]
