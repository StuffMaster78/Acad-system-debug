# Generated migration for ClassBundle missing fields
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('class_management', '0002_initial'),
        ('websites', '0001_initial'),
        ('discounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='classbundle',
            name='website',
            field=models.ForeignKey(
                help_text='Website this class bundle belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='class_bundles',
                to='websites.website',
                null=True,  # Allow null temporarily for existing records
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='assigned_writer',
            field=models.ForeignKey(
                blank=True,
                help_text='Writer assigned to this class bundle',
                limit_choices_to={'role': 'writer'},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_class_bundles',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='pricing_source',
            field=models.CharField(
                choices=[('config', 'From Bundle Config'), ('manual', 'Admin Manual Entry')],
                default='config',
                help_text='Source of pricing for this bundle',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='start_date',
            field=models.DateField(
                blank=True,
                help_text='When the class bundle starts',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='end_date',
            field=models.DateField(
                blank=True,
                help_text='When the class bundle ends',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='deposit_required',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Deposit amount required',
                max_digits=10,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='deposit_paid',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Amount of deposit already paid',
                max_digits=10,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='installments_enabled',
            field=models.BooleanField(
                default=False,
                help_text='Whether installments are enabled for this bundle'
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='installment_count',
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text='Number of installments (set by admin)',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='original_price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Original price before discount (if discount applied)',
                max_digits=10,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='discount',
            field=models.ForeignKey(
                blank=True,
                help_text='Applied discount (set by admin)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='class_bundles',
                to='discounts.discount'
            ),
        ),
        migrations.AddField(
            model_name='classbundle',
            name='created_by_admin',
            field=models.ForeignKey(
                blank=True,
                help_text='Admin who created this bundle (if manual)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_class_bundles',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

