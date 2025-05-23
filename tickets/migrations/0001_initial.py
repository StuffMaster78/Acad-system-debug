# Generated by Django 5.1.5 on 2025-02-04 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the ticket.', max_length=255)),
                ('description', models.TextField(help_text='Detailed description of the issue.')),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('closed', 'Closed'), ('awaiting_response', 'Awaiting Response'), ('escalated', 'Escalated')], default='open', help_text='Current status of the ticket.', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', help_text='Priority level of the ticket.', max_length=10)),
                ('category', models.CharField(choices=[('general', 'General Inquiry'), ('payment', 'Payment Issues'), ('technical', 'Technical Support'), ('feedback', 'Feedback'), ('order', 'Order Issues')], default='general', help_text='Category of the ticket.', max_length=20)),
                ('is_escalated', models.BooleanField(default=False, help_text='Indicates if the ticket is escalated.')),
                ('resolution_time', models.DateTimeField(blank=True, help_text='When the ticket was resolved.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the ticket was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When the ticket was last updated.')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TicketLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(help_text='Description of the action taken.', max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='When this action was performed.')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='TicketMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='The content of the message.')),
                ('is_internal', models.BooleanField(default=False, help_text='Indicates if this is an internal message (admins/support only).')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When this message was sent.')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='TicketStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_tickets', models.IntegerField(default=0, help_text='Total number of tickets.')),
                ('resolved_tickets', models.IntegerField(default=0, help_text='Total number of resolved tickets.')),
                ('average_resolution_time', models.FloatField(default=0.0, help_text='Average resolution time in hours.')),
                ('created_at', models.DateField(auto_now_add=True, help_text='Date of the statistic.')),
            ],
        ),
    ]
