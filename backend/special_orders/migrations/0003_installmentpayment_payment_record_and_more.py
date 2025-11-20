# Generated manually for installment payment and writer bonus changes
# Generated on 2024-12-19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('special_orders', '0002_initial'),
        ('order_payments_management', '0002_initial'),
    ]

    operations = [
        # Add payment_record field to InstallmentPayment
        migrations.AddField(
            model_name='installmentpayment',
            name='payment_record',
            field=models.ForeignKey(blank=True, help_text='The actual payment transaction record for this installment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='installment_payments', to='order_payments_management.orderpayment'),
        ),
        # Alter field special_order on WriterBonus
        migrations.AlterField(
            model_name='writerbonus',
            name='special_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='special_order_bonuses', to='special_orders.specialorder'),
        ),
    ]

