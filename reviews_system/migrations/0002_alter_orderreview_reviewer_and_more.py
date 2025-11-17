# Generated manually for reviewer field alterations
# Generated on 2024-12-19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_system', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderreview',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderreview_reviews_given', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='websitereview',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='websitereview_reviews_given', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='writerreview',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writerreview_reviews_given', to=settings.AUTH_USER_MODEL),
        ),
    ]

