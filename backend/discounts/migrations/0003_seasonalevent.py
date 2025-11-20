# Generated manually for SeasonalEvent proxy model
# Generated on 2024-12-19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discounts', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeasonalEvent',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Seasonal Event',
                'verbose_name_plural': 'Seasonal Events',
            },
            bases=('discounts.promotionalcampaign',),
        ),
    ]

