# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


# No-op functions - we'll use RunSQL directly


class Migration(migrations.Migration):

    dependencies = [
        ('class_management', '0004_add_express_class_fields'),
        ('order_payments_management', '0004_add_payment_reminder_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='classinstallment',
            options={'ordering': ['installment_number', 'due_date']},
        ),
        migrations.AddField(
            model_name='classinstallment',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='classinstallment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='classinstallment',
            name='due_date',
            field=models.DateField(blank=True, help_text='Date when this installment is due', null=True),
        ),
        migrations.AddField(
            model_name='classinstallment',
            name='installment_number',
            field=models.PositiveIntegerField(blank=True, help_text='Sequence number of this installment (1, 2, 3, ...)', null=True),
        ),
        migrations.AddField(
            model_name='classinstallment',
            name='is_paid',
            field=models.BooleanField(default=False, help_text='Whether this installment has been paid'),
        ),
        migrations.AddField(
            model_name='classinstallment',
            name='payment_record',
            field=models.ForeignKey(blank=True, help_text='The actual payment transaction record for this installment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_installments', to='order_payments_management.orderpayment'),
        ),
        migrations.AlterField(
            model_name='classinstallment',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Amount due for this installment', max_digits=10),
        ),
        migrations.AlterField(
            model_name='classinstallment',
            name='paid_at',
            field=models.DateTimeField(blank=True, help_text='When this installment was paid', null=True),
        ),
        migrations.AlterField(
            model_name='classinstallment',
            name='paid_by',
            field=models.ForeignKey(blank=True, help_text='User who made the payment', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ClassBundleFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(help_text='Name of the file', max_length=255)),
                ('file_size', models.PositiveIntegerField(help_text='Size of the file in bytes')),
                ('description', models.TextField(blank=True, help_text='Description of the file')),
                ('is_visible_to_client', models.BooleanField(default=True, help_text='Whether client can see this file')),
                ('is_visible_to_writer', models.BooleanField(default=True, help_text='Whether writer can see this file')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to='class_bundle_files/')),
                ('class_bundle', models.ForeignKey(help_text='Class bundle this file belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='files', to='class_management.classbundle')),
                ('uploaded_by', models.ForeignKey(help_text='User who uploaded the file', on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_class_bundle_files', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='class_management_classbundle' AND column_name='balance_remaining') THEN
                            ALTER TABLE class_management_classbundle ADD COLUMN balance_remaining NUMERIC(10, 2);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='class_management_classbundle' AND column_name='deposit_paid') THEN
                            ALTER TABLE class_management_classbundle ADD COLUMN deposit_paid NUMERIC(10, 2) DEFAULT 0.0;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='class_management_classbundle' AND column_name='deposit_required') THEN
                            ALTER TABLE class_management_classbundle ADD COLUMN deposit_required NUMERIC(10, 2) DEFAULT 0.0;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='class_management_classbundle' AND column_name='installment_count') THEN
                            ALTER TABLE class_management_classbundle ADD COLUMN installment_count INTEGER DEFAULT 0;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='class_management_classbundle' AND column_name='installments_enabled') THEN
                            ALTER TABLE class_management_classbundle ADD COLUMN installments_enabled BOOLEAN DEFAULT FALSE;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='class_management_classpurchase' AND column_name='payment_record_id') THEN
                            ALTER TABLE class_management_classpurchase 
                            ADD COLUMN payment_record_id BIGINT REFERENCES order_payments_management_orderpayment(id) ON DELETE SET NULL;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='class_management_classpurchase' AND column_name='payment_type') THEN
                            ALTER TABLE class_management_classpurchase ADD COLUMN payment_type VARCHAR(20);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='class_management_classpurchase' AND column_name='website_id') THEN
                            ALTER TABLE class_management_classpurchase 
                            ADD COLUMN website_id BIGINT REFERENCES websites_website(id) ON DELETE CASCADE;
                        END IF;
                    END $$;
                """, reverse_sql=migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='classbundle',
                    name='balance_remaining',
                    field=models.DecimalField(blank=True, decimal_places=2, help_text='Remaining balance to be paid', max_digits=10, null=True),
                ),
                migrations.AddField(
                    model_name='classbundle',
                    name='deposit_paid',
                    field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='Amount of deposit already paid', max_digits=10, null=True),
                ),
                migrations.AddField(
                    model_name='classbundle',
                    name='deposit_required',
                    field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='Deposit amount required', max_digits=10, null=True),
                ),
                migrations.AddField(
                    model_name='classbundle',
                    name='installment_count',
                    field=models.PositiveIntegerField(blank=True, default=0, help_text='Number of installments', null=True),
                ),
                migrations.AddField(
                    model_name='classbundle',
                    name='installments_enabled',
                    field=models.BooleanField(blank=True, default=False, help_text='Whether installments are enabled for this bundle', null=True),
                ),
                migrations.AddField(
                    model_name='classpurchase',
                    name='payment_record',
                    field=models.ForeignKey(blank=True, help_text='Payment record for this purchase', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_purchases', to='order_payments_management.orderpayment'),
                ),
                migrations.AddField(
                    model_name='classpurchase',
                    name='payment_type',
                    field=models.CharField(blank=True, choices=[('full', 'Full Payment'), ('deposit', 'Deposit Only'), ('installment', 'Installment')], help_text='Type of payment for this purchase', max_length=20, null=True),
                ),
                migrations.AddField(
                    model_name='classpurchase',
                    name='website',
                    field=models.ForeignKey(blank=True, help_text='Website this purchase is for', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='class_purchases', to='websites.website'),
                ),
            ],
        ),
    ]

