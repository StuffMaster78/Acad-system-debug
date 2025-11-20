# Generated migration to change PreferredWriterConfig from per-writer to website-level

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pricing_configs', '0002_initial'),
        ('websites', '0001_initial'),
    ]

    operations = [
        # Remove the unique_together constraint first
        migrations.AlterUniqueTogether(
            name='preferredwriterconfig',
            unique_together=set(),
        ),
        # Remove the writer field
        migrations.RemoveField(
            model_name='preferredwriterconfig',
            name='writer',
        ),
        # Change website from ForeignKey to OneToOneField
        # First, we need to ensure there's only one config per website
        # Then alter the field
        migrations.AlterField(
            model_name='preferredwriterconfig',
            name='website',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='preferred_writer_config',
                to='websites.website',
                help_text='Website this configuration applies to'
            ),
        ),
    ]

