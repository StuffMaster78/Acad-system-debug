from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications_system", "0007_templateperformance_templateusage"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["user", "created_at"], name="notif_user_created_idx"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["user", "is_read"], name="notif_user_read_idx"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["website", "created_at"], name="notif_website_created_idx"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["event"], name="notif_event_idx"),
        ),
    ]
