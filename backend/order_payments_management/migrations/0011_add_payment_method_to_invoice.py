# Generated migration for adding payment_method to Invoice model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_payments_management', '0010_discountusage_alter_invoice_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='payment_method',
            field=models.CharField(
                blank=True,
                help_text='Preferred payment method: wallet, stripe, paypal, bank_transfer, etc.',
                max_length=50,
                null=True
            ),
        ),
    ]

