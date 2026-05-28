from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0001_initial'),
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='guestaccesstoken',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='guest_tokens',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='websiteintegrationconfig',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who created this integration',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_integrations',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='websitetermsacceptance',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='terms_acceptances',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='websitetermsacceptance',
            unique_together={('website', 'user', 'static_page', 'terms_version')},
        ),
        migrations.AddField(
            model_name='guestaccesstoken',
            name='order',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional: limit this token to a single order.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='guest_tokens',
                to='orders.order',
            ),
        ),
        migrations.AddIndex(
            model_name='websitetermsacceptance',
            index=models.Index(fields=['website', 'user'], name='websites_we_website_e63d85_idx'),
        ),
        migrations.AddIndex(
            model_name='guestaccesstoken',
            index=models.Index(fields=['website', 'user'], name='websites_gu_website_029b81_idx'),
        ),
        migrations.AddIndex(
            model_name='guestaccesstoken',
            index=models.Index(fields=['website', 'order'], name='websites_gu_website_e29b95_idx'),
        ),
    ]
