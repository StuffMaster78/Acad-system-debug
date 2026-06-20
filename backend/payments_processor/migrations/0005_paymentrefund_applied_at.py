from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments_processor', '0004_paymentintent_client_disclosure_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrefund',
            name='applied_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text=(
                    'Set when the refund has been applied internally '
                    '(wallet credited / ledger reversed). '
                    'Replaces the metadata.internally_applied flag for '
                    'DB-level idempotency.'
                ),
            ),
        ),
        migrations.AddIndex(
            model_name='paymentrefund',
            index=models.Index(
                fields=['payment_intent', 'applied_at'],
                name='ppr_payment_intent_applied_at_idx',
            ),
        ),
    ]
