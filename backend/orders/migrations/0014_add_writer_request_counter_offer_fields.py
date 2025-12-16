# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_add_writer_acknowledgment_message_review_reminders'),
    ]

    operations = [
        migrations.AddField(
            model_name='writerrequest',
            name='client_counter_pages',
            field=models.PositiveIntegerField(blank=True, help_text="Client's counter offer for additional pages", null=True),
        ),
        migrations.AddField(
            model_name='writerrequest',
            name='client_counter_slides',
            field=models.PositiveIntegerField(blank=True, help_text="Client's counter offer for additional slides", null=True),
        ),
        migrations.AddField(
            model_name='writerrequest',
            name='client_counter_cost',
            field=models.DecimalField(blank=True, decimal_places=2, help_text="Client's counter offer cost", max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='writerrequest',
            name='client_counter_reason',
            field=models.TextField(blank=True, help_text="Client's reason for counter offer", null=True),
        ),
        migrations.AddField(
            model_name='writerrequest',
            name='has_counter_offer',
            field=models.BooleanField(default=False, help_text='Whether client has made a counter offer'),
        ),
    ]
