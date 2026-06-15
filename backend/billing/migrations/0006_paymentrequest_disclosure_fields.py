from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0005_disclosure_accepted_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentrequest",
            name="processor_display_name",
            field=models.CharField(
                blank=True,
                max_length=120,
                help_text="Human-readable payment processor name shown to the client.",
            ),
        ),
        migrations.AddField(
            model_name="paymentrequest",
            name="statement_descriptor_snapshot",
            field=models.CharField(
                blank=True,
                max_length=22,
                help_text="Exact card/bank statement descriptor shown to the client.",
            ),
        ),
        migrations.AddField(
            model_name="paymentrequest",
            name="client_disclosure_text",
            field=models.TextField(
                blank=True,
                help_text="Full disclosure text presented to the client before payment.",
            ),
        ),
        migrations.AddField(
            model_name="paymentrequest",
            name="disclosure_shown_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text="Timestamp when the disclosure was first presented.",
            ),
        ),
        migrations.AddField(
            model_name="paymentrequest",
            name="disclosure_accepted_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text="Timestamp when the client explicitly acknowledged the disclosure.",
            ),
        ),
    ]
