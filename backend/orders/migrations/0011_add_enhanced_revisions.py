# Generated manually
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_add_order_drafts_and_presets'),
        ('websites', '0002_add_payment_settings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RevisionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Brief title/summary of the revision request', max_length=255)),
                ('description', models.TextField(help_text='Detailed description of what needs to be changed')),
                ('changes_required', models.JSONField(blank=True, default=list, help_text="List of specific changes: [{'section': 'Introduction', 'issue': '...', 'request': '...'}]")),
                ('severity', models.CharField(choices=[('minor', 'Minor'), ('moderate', 'Moderate'), ('major', 'Major'), ('critical', 'Critical')], default='moderate', help_text='Severity of the revision', max_length=20)),
                ('priority', models.PositiveIntegerField(default=5, help_text='Priority level (1-10, higher = more urgent)')),
                ('requested_deadline', models.DateTimeField(blank=True, help_text="Client's requested deadline for the revision", null=True)),
                ('agreed_deadline', models.DateTimeField(blank=True, help_text='Agreed deadline (may differ from requested)', null=True)),
                ('completed_at', models.DateTimeField(blank=True, help_text='When the revision was completed', null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('client_notes', models.TextField(blank=True, help_text='Additional notes from client')),
                ('writer_notes', models.TextField(blank=True, help_text='Notes from writer during revision')),
                ('is_urgent', models.BooleanField(default=False, help_text='Marked as urgent by client')),
                ('requires_client_review', models.BooleanField(default=True, help_text='Whether client needs to review after completion')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['writer', 'editor']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revision_requests_assigned', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revision_requests', to='orders.order')),
                ('requested_by', models.ForeignKey(limit_choices_to={'role': 'client'}, on_delete=django.db.models.deletion.CASCADE, related_name='revision_requests_made', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revision_requests', to='websites.website')),
            ],
            options={
                'verbose_name': 'Revision Request',
                'verbose_name_plural': 'Revision Requests',
                'ordering': ['-priority', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='revisionrequest',
            index=models.Index(fields=['order', 'status'], name='orders_revis_order_i_idx'),
        ),
        migrations.AddIndex(
            model_name='revisionrequest',
            index=models.Index(fields=['requested_by', 'status'], name='orders_revis_request_idx'),
        ),
        migrations.AddIndex(
            model_name='revisionrequest',
            index=models.Index(fields=['assigned_to', 'status'], name='orders_revis_assigne_idx'),
        ),
        migrations.AddIndex(
            model_name='revisionrequest',
            index=models.Index(fields=['severity', 'status'], name='orders_revis_severit_idx'),
        ),
    ]

