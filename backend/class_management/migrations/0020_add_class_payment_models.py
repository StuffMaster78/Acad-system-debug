# Generated migration - Add streamlined class payment models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('class_management', '0006_alter_classbundlefile_options_and_more'),
        ('websites', '0001_initial'),
        ('order_payments_management', '0001_initial'),
        ('special_orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.DecimalField(decimal_places=2, help_text='Total amount due from client', max_digits=10)),
                ('deposit_amount', models.DecimalField(decimal_places=2, default=0, help_text='Deposit amount required', max_digits=10)),
                ('deposit_paid', models.DecimalField(decimal_places=2, default=0, help_text='Deposit amount paid', max_digits=10)),
                ('balance_remaining', models.DecimalField(decimal_places=2, default=0, help_text='Remaining balance after all payments', max_digits=10)),
                ('client_payment_status', models.CharField(choices=[('pending', 'Pending'), ('partial', 'Partially Paid'), ('paid', 'Fully Paid'), ('cancelled', 'Cancelled')], default='pending', help_text='Status of client payments', max_length=20)),
                ('writer_compensation_amount', models.DecimalField(decimal_places=2, default=0, help_text='Total compensation amount for writer', max_digits=10)),
                ('writer_paid_amount', models.DecimalField(decimal_places=2, default=0, help_text='Amount already paid to writer', max_digits=10)),
                ('writer_payment_status', models.CharField(choices=[('pending', 'Pending Writer Payment'), ('scheduled', 'Scheduled'), ('paid', 'Writer Paid'), ('cancelled', 'Cancelled')], default='pending', help_text='Status of writer payment', max_length=20)),
                ('uses_installments', models.BooleanField(default=False, help_text='Whether this payment uses installments')),
                ('total_installments', models.PositiveIntegerField(default=0, help_text='Total number of installments')),
                ('paid_installments', models.PositiveIntegerField(default=0, help_text='Number of installments paid')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('writer_paid_at', models.DateTimeField(blank=True, help_text='When writer was fully paid', null=True)),
                ('assigned_writer', models.ForeignKey(blank=True, limit_choices_to={'role': 'writer'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_payments', to=settings.AUTH_USER_MODEL)),
                ('class_bundle', models.ForeignKey(help_text='The class bundle this payment is for', on_delete=django.db.models.deletion.CASCADE, related_name='class_payments', to='class_management.classbundle')),
                ('website', models.ForeignKey(help_text='Website this payment belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='class_payments', to='websites.website')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ClassPaymentInstallment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('installment_number', models.PositiveIntegerField(help_text='Installment sequence number')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Installment amount', max_digits=10)),
                ('is_paid', models.BooleanField(default=False, help_text='Whether this installment is paid')),
                ('paid_at', models.DateTimeField(blank=True, help_text='When this installment was paid', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('class_installment', models.OneToOneField(help_text='The actual installment record', on_delete=django.db.models.deletion.CASCADE, related_name='payment_link', to='class_management.classinstallment')),
                ('class_payment', models.ForeignKey(help_text='The class payment this installment belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='payment_installments', to='class_management.classpayment')),
                ('payment_record', models.ForeignKey(blank=True, help_text='The payment transaction record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_payment_installments', to='order_payments_management.orderpayment')),
            ],
            options={
                'ordering': ['installment_number'],
            },
        ),
        migrations.CreateModel(
            name='ClassWriterPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Payment amount to writer', max_digits=10)),
                ('payment_type', models.CharField(choices=[('full', 'Full Payment'), ('installment', 'Installment-Based Payment'), ('partial', 'Partial Payment')], default='full', help_text='Type of payment', max_length=20)),
                ('installment_number', models.PositiveIntegerField(blank=True, help_text='If installment-based, which installment this payment is for', null=True)),
                ('is_paid', models.BooleanField(default=False, help_text='Whether writer has been paid')),
                ('paid_at', models.DateTimeField(blank=True, help_text='When writer was paid', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('class_payment', models.ForeignKey(help_text='The class payment this writer payment is for', on_delete=django.db.models.deletion.CASCADE, related_name='writer_payments', to='class_management.classpayment')),
                ('writer_bonus', models.ForeignKey(blank=True, help_text='The WriterBonus record (if created)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_writer_payments', to='special_orders.writerbonus')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='classpayment',
            index=models.Index(fields=['class_bundle', 'client_payment_status'], name='class_manage_class_b_client_p_idx'),
        ),
        migrations.AddIndex(
            model_name='classpayment',
            index=models.Index(fields=['assigned_writer', 'writer_payment_status'], name='class_manage_assigned_writer_p_idx'),
        ),
        migrations.AddIndex(
            model_name='classpayment',
            index=models.Index(fields=['website', 'client_payment_status'], name='class_manage_website_client_p_idx'),
        ),
        migrations.AddIndex(
            model_name='classpayment',
            index=models.Index(fields=['assigned_writer', 'website'], name='class_manage_assigned_writer_w_idx'),
        ),
        migrations.AddIndex(
            model_name='classpaymentinstallment',
            index=models.Index(fields=['class_payment', 'is_paid'], name='class_manage_class_p_is_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='classpaymentinstallment',
            index=models.Index(fields=['class_payment', 'installment_number'], name='class_manage_class_p_installment_idx'),
        ),
        migrations.AddIndex(
            model_name='classwriterpayment',
            index=models.Index(fields=['class_payment', 'is_paid'], name='class_manage_class_p_is_paid_w_idx'),
        ),
        migrations.AddIndex(
            model_name='classwriterpayment',
            index=models.Index(fields=['class_payment', 'payment_type'], name='class_manage_class_p_payment_t_idx'),
        ),
    ]

