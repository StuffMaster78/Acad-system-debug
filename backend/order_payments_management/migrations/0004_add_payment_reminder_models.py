# Generated manually for payment reminder models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0001_initial'),
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order_payments_management', '0003_alter_paymentrecord_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentReminderConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Name/description for this reminder (e.g., 'First Reminder', 'Final Warning')", max_length=255)),
                ('deadline_percentage', models.DecimalField(decimal_places=2, help_text='Percentage of deadline elapsed when to send (e.g., 30.00 for 30%)', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('message', models.TextField(help_text='Message to send in notification/email')),
                ('send_as_notification', models.BooleanField(default=True, help_text='Send as in-app notification')),
                ('send_as_email', models.BooleanField(default=True, help_text='Send as email')),
                ('email_subject', models.CharField(blank=True, help_text='Email subject (if blank, uses default)', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this reminder is active')),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Order for displaying reminders (lower = earlier)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='Admin who created this reminder', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_payment_reminders', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website this reminder config applies to', on_delete=django.db.models.deletion.CASCADE, related_name='payment_reminder_configs', to='websites.website')),
            ],
            options={
                'verbose_name': 'Payment Reminder Configuration',
                'verbose_name_plural': 'Payment Reminder Configurations',
                'ordering': ['display_order', 'deadline_percentage'],
                'unique_together': {('website', 'deadline_percentage')},
            },
        ),
        migrations.CreateModel(
            name='PaymentReminderDeletionMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='Message to send when order is deleted after deadline')),
                ('send_as_notification', models.BooleanField(default=True, help_text='Send as in-app notification')),
                ('send_as_email', models.BooleanField(default=True, help_text='Send as email')),
                ('email_subject', models.CharField(blank=True, help_text='Email subject (if blank, uses default)', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this deletion message is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='Admin who created this message', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_deletion_messages', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website this message applies to', on_delete=django.db.models.deletion.CASCADE, related_name='payment_deletion_messages', to='websites.website')),
            ],
            options={
                'verbose_name': 'Payment Deletion Message',
                'verbose_name_plural': 'Payment Deletion Messages',
            },
        ),
        migrations.CreateModel(
            name='PaymentReminderSent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('sent_as_notification', models.BooleanField(default=False)),
                ('sent_as_email', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_reminders_received', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_reminders_sent', to='orders.order')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reminders_sent', to='order_payments_management.orderpayment')),
                ('reminder_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_reminders', to='order_payments_management.paymentreminderconfig')),
            ],
            options={
                'unique_together': {('reminder_config', 'order', 'payment')},
            },
        ),
        migrations.AddIndex(
            model_name='paymentremindersent',
            index=models.Index(fields=['order', 'reminder_config'], name='order_paym_order_i_123456_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentremindersent',
            index=models.Index(fields=['payment', 'reminder_config'], name='order_paym_payment_123456_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentremindersent',
            index=models.Index(fields=['client', 'sent_at'], name='order_paym_client_123456_idx'),
        ),
    ]

