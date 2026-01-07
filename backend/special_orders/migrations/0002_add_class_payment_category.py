# Generated migration - Add class_payment category to WriterBonus
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('special_orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='writerbonus',
            name='category',
            field=models.CharField(
                choices=[
                    ('performance', 'Outstanding Performance'),
                    ('order_completion', 'Order Completion'),
                    ('client_tip', 'Client Tip'),
                    ('class_payment', 'Class Payment'),
                    ('other', 'Other'),
                ],
                default='client_tip',
                max_length=50
            ),
        ),
    ]

