from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("files_management", "0006_add_dispute_writer_response_support_management_and_orders"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FileDownloadReceipt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_downloaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "attachment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="download_receipts",
                        to="files_management.fileattachment",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="file_download_receipts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "files_management_download_receipt",
            },
        ),
        migrations.AddIndex(
            model_name="filedownloadreceipt",
            index=models.Index(fields=["attachment", "user"], name="fm_receipt_attach_user_idx"),
        ),
        migrations.AddIndex(
            model_name="filedownloadreceipt",
            index=models.Index(fields=["user"], name="fm_receipt_user_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="filedownloadreceipt",
            unique_together={("attachment", "user")},
        ),
    ]
