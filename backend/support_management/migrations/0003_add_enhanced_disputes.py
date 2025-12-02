# Generated manually
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support_management', '0002_initial'),
        ('orders', '0011_add_enhanced_revisions'),
        ('websites', '0004_add_admin_notifications_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderDispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Brief title/summary of the dispute', max_length=255)),
                ('description', models.TextField(help_text='Detailed description of the dispute')),
                ('status', models.CharField(choices=[('open', 'Open'), ('under_review', 'Under Review'), ('resolved', 'Resolved'), ('escalated', 'Escalated'), ('closed', 'Closed')], default='open', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20)),
                ('resolution_notes', models.TextField(blank=True, help_text='Resolution notes from support/admin')),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_outcome', models.CharField(blank=True, help_text="Outcome: 'client_wins', 'writer_wins', 'partial_refund', etc.", max_length=50)),
                ('escalated_at', models.DateTimeField(blank=True, null=True)),
                ('escalation_reason', models.TextField(blank=True, help_text='Reason for escalation')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['support', 'admin', 'superadmin']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disputes_assigned', to=settings.AUTH_USER_MODEL)),
                ('escalated_to', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'superadmin']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disputes_escalated_to', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enhanced_disputes', to='orders.order')),
                ('other_party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disputes_against', to=settings.AUTH_USER_MODEL)),
                ('raised_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disputes_raised', to=settings.AUTH_USER_MODEL)),
                ('resolved_by', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['support', 'admin', 'superadmin']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disputes_resolved', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_disputes', to='websites.website')),
            ],
            options={
                'verbose_name': 'Order Dispute',
                'verbose_name_plural': 'Order Disputes',
                'ordering': ['-priority', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DisputeMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_internal', models.BooleanField(default=False, help_text='Internal note (not visible to other party)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('dispute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='support_management.orderdispute')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispute_messages_sent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='orderdispute',
            index=models.Index(fields=['order', 'status'], name='support_man_order_i_idx'),
        ),
        migrations.AddIndex(
            model_name='orderdispute',
            index=models.Index(fields=['raised_by', 'status'], name='support_man_raised__idx'),
        ),
        migrations.AddIndex(
            model_name='orderdispute',
            index=models.Index(fields=['assigned_to', 'status'], name='support_man_assigne_idx'),
        ),
        migrations.AddIndex(
            model_name='orderdispute',
            index=models.Index(fields=['status', 'priority'], name='support_man_status__idx'),
        ),
    ]

