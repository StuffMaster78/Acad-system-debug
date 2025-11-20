# Generated manually for Invoice model updates
# Generated on 2025-11-16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_payments_management', '0007_add_invoice_fields'),
        ('websites', '0001_initial'),
        ('orders', '0001_initial'),
        ('special_orders', '0001_initial'),
        ('class_management', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Make client nullable (was required, now optional)
        migrations.AlterField(
            model_name='invoice',
            name='client',
            field=models.ForeignKey(
                blank=True,
                help_text='Client user (if exists in system)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='invoices',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        
        # Add recipient_email (required field)
        migrations.AddField(
            model_name='invoice',
            name='recipient_email',
            field=models.EmailField(
                help_text='Email address to send invoice to (required if client is null)',
                null=True  # Temporary null=True, will be made required after data migration
            ),
        ),
        
        # Add recipient_name
        migrations.AddField(
            model_name='invoice',
            name='recipient_name',
            field=models.CharField(
                blank=True,
                help_text='Name of recipient (for email personalization)',
                max_length=255
            ),
        ),
        
        # Add website (required)
        migrations.AddField(
            model_name='invoice',
            name='website',
            field=models.ForeignKey(
                help_text='Website context for the invoice',
                null=True,  # Temporary null=True, will be made required after data migration
                on_delete=django.db.models.deletion.CASCADE,
                related_name='invoices',
                to='websites.website'
            ),
        ),
        
        # Update title max_length from 100 to 200
        migrations.AlterField(
            model_name='invoice',
            name='title',
            field=models.CharField(
                help_text='Invoice title/purpose',
                max_length=200
            ),
        ),
        
        # Add purpose field
        migrations.AddField(
            model_name='invoice',
            name='purpose',
            field=models.CharField(
                blank=True,
                help_text="Purpose of invoice (e.g., 'Order Payment', 'Class Purchase')",
                max_length=100
            ),
        ),
        
        # Add order_number field
        migrations.AddField(
            model_name='invoice',
            name='order_number',
            field=models.CharField(
                blank=True,
                help_text='Optional order/reference number for display',
                max_length=100
            ),
        ),
        
        # Update payment field to reference OrderPayment instead of PaymentRecord
        migrations.AlterField(
            model_name='invoice',
            name='payment',
            field=models.OneToOneField(
                blank=True,
                help_text='Linked payment record when paid',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='invoice',
                to='order_payments_management.orderpayment'
            ),
        ),
        
        # Add payment_token
        migrations.AddField(
            model_name='invoice',
            name='payment_token',
            field=models.CharField(
                blank=True,
                help_text='Secure token for payment link',
                max_length=128,
                null=True,
                unique=True
            ),
        ),
        
        # Add token_expires_at
        migrations.AddField(
            model_name='invoice',
            name='token_expires_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When payment token expires',
                null=True
            ),
        ),
        
        # Add email_sent
        migrations.AddField(
            model_name='invoice',
            name='email_sent',
            field=models.BooleanField(default=False),
        ),
        
        # Add email_sent_at
        migrations.AddField(
            model_name='invoice',
            name='email_sent_at',
            field=models.DateTimeField(
                blank=True,
                null=True
            ),
        ),
        
        # Add email_sent_count
        migrations.AddField(
            model_name='invoice',
            name='email_sent_count',
            field=models.IntegerField(default=0),
        ),
        
        # Add order reference (optional)
        migrations.AddField(
            model_name='invoice',
            name='order',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional reference to order',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='invoices',
                to='orders.order'
            ),
        ),
        
        # Add special_order reference (optional)
        migrations.AddField(
            model_name='invoice',
            name='special_order',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional reference to special order',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='invoices',
                to='special_orders.specialorder'
            ),
        ),
        
        # Add class_purchase reference (optional)
        migrations.AddField(
            model_name='invoice',
            name='class_purchase',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional reference to class purchase',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='invoices',
                to='class_management.classpurchase'
            ),
        ),
        
        # Add updated_at
        migrations.AddField(
            model_name='invoice',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['reference_id'], name='order_payme_referen_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['payment_token'], name='order_payme_payment_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['is_paid', 'due_date'], name='order_payme_is_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['website', 'is_paid'], name='order_payme_website_idx'),
        ),
        
        # Data migration: Populate recipient_email and website for existing invoices
        migrations.RunPython(
            code=migrations.RunPython.noop,  # No data migration needed if no existing invoices
            reverse_code=migrations.RunPython.noop,
        ),
        
        # Make recipient_email and website required (after data migration)
        migrations.AlterField(
            model_name='invoice',
            name='recipient_email',
            field=models.EmailField(
                help_text='Email address to send invoice to (required if client is null)'
            ),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='website',
            field=models.ForeignKey(
                help_text='Website context for the invoice',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='invoices',
                to='websites.website'
            ),
        ),
    ]

