# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0001_initial'),
        ('websites', '0001_initial'),
        ('orders', '0004_add_external_contact_and_unpaid_override'),
        ('order_payments_management', '0004_add_payment_reminder_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tip_type', models.CharField(choices=[('direct', 'Direct Tip'), ('order', 'Order-Based Tip'), ('class', 'Class/Task-Based Tip')], default='direct', help_text='Type of tip: direct, order-based, or class/task-based', max_length=20)),
                ('related_entity_type', models.CharField(blank=True, help_text='Type of related entity (e.g., \'class_bundle\', \'express_class\')', max_length=50, null=True)),
                ('related_entity_id', models.PositiveIntegerField(blank=True, help_text='ID of related entity (class bundle, express class, etc.)', null=True)),
                ('tip_amount', models.DecimalField(decimal_places=2, help_text='Full tip amount paid by client', max_digits=10)),
                ('tip_reason', models.TextField(blank=True, help_text='Reason for the tip')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('writer_percentage', models.DecimalField(decimal_places=2, help_text='Percentage of tip that goes to writer (based on their level)', max_digits=5)),
                ('writer_earning', models.DecimalField(decimal_places=2, help_text='Amount writer receives (their share only)', max_digits=10)),
                ('platform_profit', models.DecimalField(decimal_places=2, help_text='Amount platform retains (not visible to writer)', max_digits=10)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', help_text='Payment status for this tip', max_length=20)),
                ('origin', models.CharField(default='client', help_text='Origin of tip (e.g., \'client\', \'admin\', \'system\')', max_length=50)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tips_sent', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, help_text='Order this tip is for (if order-based)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tips', to='orders.order')),
                ('payment', models.ForeignKey(blank=True, help_text='Payment record for this tip', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tips', to='order_payments_management.orderpayment')),
                ('website', models.ForeignKey(help_text='Multitenancy support: this tip is for a specific website.', on_delete=django.db.models.deletion.CASCADE, to='websites.website')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tips_received', to=settings.AUTH_USER_MODEL)),
                ('writer_level', models.ForeignKey(blank=True, help_text='Writer level at time of tip (for percentage calculation)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tips', to='writer_management.writerlevel')),
            ],
            options={
                'ordering': ['-sent_at'],
            },
        ),
        migrations.AddIndex(
            model_name='tip',
            index=models.Index(fields=['client', 'website'], name='writer_mana_client__idx'),
        ),
        migrations.AddIndex(
            model_name='tip',
            index=models.Index(fields=['writer', 'website'], name='writer_mana_writer__idx'),
        ),
        migrations.AddIndex(
            model_name='tip',
            index=models.Index(fields=['tip_type', 'related_entity_type', 'related_entity_id'], name='writer_mana_tip_typ_idx'),
        ),
    ]
