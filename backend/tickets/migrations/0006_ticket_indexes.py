from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0005_rename_tickets_tick_ticket__idx_tickets_tic_ticket__02f237_idx_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="ticket",
            index=models.Index(fields=["status"], name="ticket_status_idx"),
        ),
        migrations.AddIndex(
            model_name="ticket",
            index=models.Index(fields=["created_at"], name="ticket_created_idx"),
        ),
        migrations.AddIndex(
            model_name="ticket",
            index=models.Index(fields=["assigned_to"], name="ticket_assigned_idx"),
        ),
        migrations.AddIndex(
            model_name="ticket",
            index=models.Index(fields=["created_by"], name="ticket_created_by_idx"),
        ),
        migrations.AddIndex(
            model_name="ticket",
            index=models.Index(fields=["website"], name="ticket_website_idx"),
        ),
        migrations.AddIndex(
            model_name="ticket",
            index=models.Index(fields=["status", "assigned_to"], name="ticket_status_assigned_idx"),
        ),
        migrations.AddIndex(
            model_name="ticket",
            index=models.Index(fields=["status", "created_at"], name="ticket_status_created_idx"),
        ),
    ]
