# Generated migration to add default generator for registration_id and backfill blanks
from django.db import migrations, models
import client_management.models


def backfill_registration_ids(apps, schema_editor):
    ClientProfile = apps.get_model('client_management', 'ClientProfile')
    for cp in ClientProfile.objects.all():
        if not getattr(cp, 'registration_id', None) or cp.registration_id.strip() == '':
            # assign a generated id, ensure uniqueness by retry loop
            for _ in range(5):
                candidate = client_management.models.generate_registration_id()
                if not ClientProfile.objects.filter(registration_id=candidate).exists():
                    cp.registration_id = candidate
                    cp.save(update_fields=['registration_id'])
                    break


class Migration(migrations.Migration):

    dependencies = [
        ('client_management', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientprofile',
            name='registration_id',
            field=models.CharField(
                max_length=50,
                unique=True,
                default=client_management.models.generate_registration_id,
                help_text='Unique client registration ID (e.g., Client #12345).'
            ),
        ),
        migrations.RunPython(backfill_registration_ids, migrations.RunPython.noop),
    ]


