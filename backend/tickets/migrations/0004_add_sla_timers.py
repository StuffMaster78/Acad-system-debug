# Generated manually
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_add_content_type_fields'),
        ('websites', '0004_add_admin_notifications_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='has_sla',
            field=models.BooleanField(default=False, help_text='Whether SLA tracking is enabled'),
        ),
        migrations.CreateModel(
            name='TicketSLA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('first_response_deadline', models.DateTimeField(help_text='Deadline for first response')),
                ('resolution_deadline', models.DateTimeField(help_text='Deadline for resolution')),
                ('first_response_at', models.DateTimeField(blank=True, help_text='When first response was sent', null=True)),
                ('resolved_at', models.DateTimeField(blank=True, help_text='When ticket was resolved', null=True)),
                ('first_response_breached', models.BooleanField(default=False, help_text='Whether first response SLA was breached')),
                ('resolution_breached', models.BooleanField(default=False, help_text='Whether resolution SLA was breached')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], help_text='Priority level (affects SLA)', max_length=20)),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sla_tracking', to='tickets.ticket')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_slas', to='websites.website')),
            ],
            options={
                'verbose_name': 'Ticket SLA',
                'verbose_name_plural': 'Ticket SLAs',
            },
        ),
        migrations.AddIndex(
            model_name='ticketsla',
            index=models.Index(fields=['ticket', 'resolution_deadline'], name='tickets_tick_ticket__idx'),
        ),
        migrations.AddIndex(
            model_name='ticketsla',
            index=models.Index(fields=['website', 'resolution_breached'], name='tickets_tick_website_idx'),
        ),
    ]

