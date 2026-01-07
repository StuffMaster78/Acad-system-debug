# Generated migration for adding payment_reference_id field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writer_payments_management', '0001_initial'),  # Update with actual last migration
    ]

    operations = [
        migrations.AddField(
            model_name='writerpayment',
            name='payment_reference_id',
            field=models.CharField(
                blank=True,
                help_text='Payment system reference ID (MPESA, PayPal, Stripe, bank transfer, etc.)',
                max_length=255,
                null=True
            ),
        ),
    ]

