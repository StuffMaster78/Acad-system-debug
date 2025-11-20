# Generated manually for DiscountUsage proxy and field alterations
# Generated on 2024-12-19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import order_payments_management.models


class Migration(migrations.Migration):

    dependencies = [
        ('order_payments_management', '0009_add_invoice_indexes'),
        ('discounts', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create proxy model DiscountUsage
        migrations.CreateModel(
            name='DiscountUsage',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Discount Usage',
                'verbose_name_plural': 'Discount Usages',
            },
            bases=('discounts.discountusage',),
        ),
        # Change Meta options on invoice (indexes are already there, just renaming)
        migrations.AlterModelOptions(
            name='invoice',
            options={'ordering': ['-created_at']},
        ),
        # Rename indexes to match Django's auto-generated naming convention
        migrations.AlterIndexTogether(
            name='invoice',
            index_together=set(),
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_referen_idx',
            new_name='order_payme_referen_6f66b6_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_payment_idx',
            new_name='order_payme_payment_5c71e3_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_is_paid_single_idx',
            new_name='order_payme_is_paid_b11a1c_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_created_at_idx',
            new_name='order_payme_created_8e7618_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_client_idx',
            new_name='order_payme_client__9c1de2_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_website_single_idx',
            new_name='order_payme_website_e82b2f_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_due_date_idx',
            new_name='order_payme_due_dat_01efb0_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_is_paid_idx',
            new_name='order_payme_is_paid_fabe64_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_website_idx',
            new_name='order_payme_website_0682d6_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_client_paid_idx',
            new_name='order_payme_client__78b6d9_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_website_created_idx',
            new_name='order_payme_website_a6d4c3_idx',
        ),
        migrations.RenameIndex(
            model_name='invoice',
            old_name='order_payme_paid_created_idx',
            new_name='order_payme_is_paid_7e8e7e_idx',
        ),
        # Rename indexes on paymentremindersent
        migrations.RenameIndex(
            model_name='paymentremindersent',
            old_name='order_paym_order_i_123456_idx',
            new_name='order_payme_order_i_22971a_idx',
        ),
        migrations.RenameIndex(
            model_name='paymentremindersent',
            old_name='order_paym_payment_123456_idx',
            new_name='order_payme_payment_10bb1d_idx',
        ),
        migrations.RenameIndex(
            model_name='paymentremindersent',
            old_name='order_paym_client_123456_idx',
            new_name='order_payme_client__3b30e3_idx',
        ),
        # Alter fields on invoice
        migrations.AlterField(
            model_name='invoice',
            name='description',
            field=models.TextField(blank=True, help_text='Detailed description'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='issued_by',
            field=models.ForeignKey(blank=True, help_text='Admin/superadmin who created the invoice', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issued_invoices', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='reference_id',
            field=models.CharField(default=order_payments_management.models.generate_reference_id, help_text='Unique invoice reference number', max_length=64, unique=True),
        ),
        # Alter fields on orderpayment
        migrations.AlterField(
            model_name='orderpayment',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('unpaid', 'Unpaid'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('partially_refunded', 'Partially Refunded'), ('fully_refunded', 'Fully Refunded'), ('disputed', 'Disputed'), ('under_review', 'Under Review')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='payment_type',
            field=models.CharField(choices=[('standard', 'Standard Order'), ('predefined_special', 'Predefined Special Order'), ('estimated_special', 'Estimated Special Order'), ('class_payment', 'Class Payment'), ('wallet_payment', 'Wallet Payment'), ('invoice', 'Invoice')], max_length=20),
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('unpaid', 'Unpaid'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('partially_refunded', 'Partially Refunded'), ('fully_refunded', 'Fully Refunded'), ('disputed', 'Disputed'), ('under_review', 'Under Review')], default='pending', help_text='Current payment status', max_length=20),
        ),
        # Alter fields on paymentrecord
        migrations.AlterField(
            model_name='paymentrecord',
            name='payment_type',
            field=models.CharField(choices=[('standard', 'Standard Order'), ('predefined_special', 'Predefined Special Order'), ('estimated_special', 'Estimated Special Order'), ('class_payment', 'Class Payment'), ('wallet_payment', 'Wallet Payment'), ('invoice', 'Invoice')], max_length=20),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('unpaid', 'Unpaid'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('partially_refunded', 'Partially Refunded'), ('fully_refunded', 'Fully Refunded'), ('disputed', 'Disputed'), ('under_review', 'Under Review')], default='pending', max_length=20),
        ),
        # Alter fields on refund
        migrations.AlterField(
            model_name='refund',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='refund',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='order_payments_management.orderpayment'),
        ),
        migrations.AlterField(
            model_name='refund',
            name='processed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_refunds', to=settings.AUTH_USER_MODEL),
        ),
        # Alter fields on specialorderpayment
        migrations.AlterField(
            model_name='specialorderpayment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('unpaid', 'Unpaid'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('partially_refunded', 'Partially Refunded'), ('fully_refunded', 'Fully Refunded'), ('disputed', 'Disputed'), ('under_review', 'Under Review')], default='pending', max_length=20),
        ),
        # Alter fields on wallettransaction
        migrations.AlterField(
            model_name='wallettransaction',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('unpaid', 'Unpaid'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('partially_refunded', 'Partially Refunded'), ('fully_refunded', 'Fully Refunded'), ('disputed', 'Disputed'), ('under_review', 'Under Review')], default='pending', max_length=20),
        ),
    ]

