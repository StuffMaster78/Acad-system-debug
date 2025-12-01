from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0012_add_writer_availability_fields'),
        ('websites', '0001_initial'),
        ('orders', '0001_initial'),
        ('writer_wallet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WriterAdvancePaymentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_amount', models.DecimalField(decimal_places=2, help_text='Amount requested by writer', max_digits=12)),
                ('approved_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Amount approved by admin (may be less than requested - counteroffer)', max_digits=12, null=True)),
                ('disbursed_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Amount actually disbursed', max_digits=12)),
                ('expected_earnings', models.DecimalField(decimal_places=2, help_text='Expected earnings calculated at request time', max_digits=12)),
                ('max_advance_percentage', models.DecimalField(decimal_places=2, default=Decimal('50.00'), help_text='Maximum advance percentage allowed (e.g., 50%)', max_digits=5)),
                ('max_advance_amount', models.DecimalField(decimal_places=2, help_text='Maximum advance amount based on expected earnings', max_digits=12)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('disbursed', 'Disbursed'), ('repaid', 'Repaid'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('reason', models.TextField(blank=True, help_text="Writer's reason for advance request", null=True)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('review_notes', models.TextField(blank=True, help_text='Admin review notes (rejection reason or counteroffer explanation)', null=True)),
                ('disbursed_at', models.DateTimeField(blank=True, null=True)),
                ('repaid_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Amount repaid so far', max_digits=12)),
                ('fully_repaid_at', models.DateTimeField(blank=True, null=True)),
                ('disbursed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disbursed_advances', to='users.user')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_advances', to='users.user')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='websites.website')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advance_requests', to='writer_management.writerprofile')),
            ],
            options={
                'ordering': ['-requested_at'],
            },
        ),
        migrations.CreateModel(
            name='AdvanceDeduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_deducted', models.DecimalField(decimal_places=2, help_text='Amount deducted from payment', max_digits=12)),
                ('deducted_at', models.DateTimeField(auto_now_add=True)),
                ('advance_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='writer_management.writeradvancepaymentrequest')),
                ('order', models.ForeignKey(blank=True, help_text='Order payment from which advance was deducted', null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.order')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='websites.website')),
                ('writer_payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='advance_deductions', to='writer_wallet.writerpayment')),
            ],
            options={
                'ordering': ['-deducted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='writeradvancepaymentrequest',
            index=models.Index(fields=['writer', 'status'], name='writer_mana_writer__idx'),
        ),
        migrations.AddIndex(
            model_name='writeradvancepaymentrequest',
            index=models.Index(fields=['status', 'requested_at'], name='writer_mana_status__idx'),
        ),
    ]

