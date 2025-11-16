# Generated migration for adding external contact and unpaid override fields to Order model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_add_editing_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='external_contact_name',
            field=models.CharField(
                blank=True,
                help_text='Name of external contact for unattributed orders (e.g., from chat, WhatsApp).',
                max_length=255,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='external_contact_email',
            field=models.EmailField(
                blank=True,
                help_text='Email of external contact for unattributed orders.',
                max_length=254,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='external_contact_phone',
            field=models.CharField(
                blank=True,
                help_text='Phone number of external contact for unattributed orders.',
                max_length=20,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='allow_unpaid_access',
            field=models.BooleanField(
                default=False,
                help_text='If True, allows access to this order even if unpaid. Admin can override default unpaid access restrictions.'
            ),
        ),
    ]
