# Generated manually for refund field alterations
# Generated on 2024-12-19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('refunds', '0001_initial'),
        ('order_payments_management', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='refund',
            name='order_payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refund_app_refunds', to='order_payments_management.orderpayment'),
        ),
        migrations.AlterField(
            model_name='refund',
            name='processed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_refund_app_refunds', to=settings.AUTH_USER_MODEL),
        ),
    ]

