# Generated manually to add missing OrderPayment fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order_payments_management', '0004_add_payment_reminder_models'),
        ('special_orders', '0002_initial'),
        ('class_management', '0005_alter_classinstallment_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderpayment',
            name='class_purchase',
            field=models.ForeignKey(
                blank=True,
                help_text='Class bundle purchase payment (for payment_type=\'class_payment\')',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                to='class_management.classpurchase'
            ),
        ),
        migrations.AddField(
            model_name='orderpayment',
            name='related_object_id',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='ID of related object (e.g., InstallmentPayment.id for special order installments)',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='orderpayment',
            name='related_object_type',
            field=models.CharField(
                blank=True,
                help_text='Type of related object (e.g., \'installment_payment\')',
                max_length=50,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='orderpayment',
            name='special_order',
            field=models.ForeignKey(
                blank=True,
                help_text='Special order payment (for payment_type=\'predefined_special\' or \'estimated_special\')',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                to='special_orders.specialorder'
            ),
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='order',
            field=models.ForeignKey(
                blank=True,
                help_text='Standard order payment (for payment_type=\'standard\')',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                to='orders.order'
            ),
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                    ('refunded', 'Refunded'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='payment_type',
            field=models.CharField(
                choices=[
                    ('standard', 'Standard Order Payment'),
                    ('predefined_special', 'Predefined Special Order'),
                    ('estimated_special', 'Estimated Special Order'),
                    ('class_payment', 'Class Bundle Payment'),
                    ('wallet', 'Wallet Transaction'),
                    ('refund', 'Refund')
                ],
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                    ('refunded', 'Refunded'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                help_text='Current payment status',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='payment_type',
            field=models.CharField(
                choices=[
                    ('standard', 'Standard Order Payment'),
                    ('predefined_special', 'Predefined Special Order'),
                    ('estimated_special', 'Estimated Special Order'),
                    ('class_payment', 'Class Bundle Payment'),
                    ('wallet', 'Wallet Transaction'),
                    ('refund', 'Refund')
                ],
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                    ('refunded', 'Refunded'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='refund',
            name='client',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='refunds',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name='refund',
            name='payment',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='refunds',
                to='order_payments_management.orderpayment'
            ),
        ),
        migrations.AlterField(
            model_name='refund',
            name='processed_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='processed_refunds',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name='specialorderpayment',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                    ('refunded', 'Refunded'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                    ('refunded', 'Refunded'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AddIndex(
            model_name='orderpayment',
            index=models.Index(fields=['payment_type', 'order_id'], name='order_payme_payment_8ac386_idx'),
        ),
        migrations.AddIndex(
            model_name='orderpayment',
            index=models.Index(fields=['payment_type', 'special_order_id'], name='order_payme_payment_a1ab38_idx'),
        ),
        migrations.AddIndex(
            model_name='orderpayment',
            index=models.Index(fields=['payment_type', 'class_purchase_id'], name='order_payme_payment_17ee87_idx'),
        ),
        migrations.AddIndex(
            model_name='orderpayment',
            index=models.Index(fields=['client', 'status'], name='order_payme_client__af5023_idx'),
        ),
        migrations.AddIndex(
            model_name='orderpayment',
            index=models.Index(fields=['related_object_type', 'related_object_id'], name='order_payme_related_91610c_idx'),
        ),
    ]

