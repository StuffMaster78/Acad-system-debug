# Generated by Django 5.1.5 on 2025-02-04 03:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('discounts', '__first__'),
        ('order_configs', '__first__'),
        ('orders', '0001_initial'),
        ('pricing_configs', '__first__'),
        ('websites', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='dispute',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='User who created the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dispute',
            name='raised_by',
            field=models.ForeignKey(blank=True, help_text='The user who raised the dispute (admin, client, editor, support, superadmin).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disputes_raised', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dispute',
            name='updated_by',
            field=models.ForeignKey(blank=True, help_text='User who last updated the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dispute',
            name='website',
            field=models.ForeignKey(blank=True, help_text='Website this record is associated with', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='websites.website'),
        ),
        migrations.AddField(
            model_name='disputewriterresponse',
            name='dispute',
            field=models.ForeignKey(help_text='The dispute being responded to.', on_delete=django.db.models.deletion.CASCADE, related_name='writer_responses', to='orders.dispute'),
        ),
        migrations.AddField(
            model_name='disputewriterresponse',
            name='responded_by',
            field=models.ForeignKey(help_text='The writer responding to the dispute.', limit_choices_to={'role': 'writer'}, on_delete=django.db.models.deletion.CASCADE, related_name='dispute_writer_responses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='failedpayment',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='failed_payments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='academic_level',
            field=models.ForeignKey(blank=True, help_text='The academic level required.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='pricing_configs.academiclevelpricing'),
        ),
        migrations.AddField(
            model_name='order',
            name='client',
            field=models.ForeignKey(blank=True, help_text='The client who placed this order. Leave blank for admin-created orders.', limit_choices_to={'role': 'client'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_as_client', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='User who created the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_code',
            field=models.ForeignKey(blank=True, help_text='Discount code applied to this order.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='discounts.discount'),
        ),
        migrations.AddField(
            model_name='order',
            name='english_type',
            field=models.ForeignKey(blank=True, help_text='Preferred English style for the paper.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.englishtype'),
        ),
        migrations.AddField(
            model_name='order',
            name='extra_services',
            field=models.ManyToManyField(blank=True, help_text='Additional services requested by the client or admin.', related_name='orders', to='pricing_configs.additionalservice'),
        ),
        migrations.AddField(
            model_name='order',
            name='formatting_style',
            field=models.ForeignKey(blank=True, help_text='The formatting style required.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.formattingstyle'),
        ),
        migrations.AddField(
            model_name='order',
            name='paper_type',
            field=models.ForeignKey(help_text='The type of paper requested.', on_delete=django.db.models.deletion.PROTECT, to='order_configs.papertype'),
        ),
        migrations.AddField(
            model_name='order',
            name='preferred_writer',
            field=models.ForeignKey(blank=True, help_text='Preferred writer for this order.', limit_choices_to={'role': 'writer'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='subject',
            field=models.ForeignKey(blank=True, help_text='The subject of the order.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.subject'),
        ),
        migrations.AddField(
            model_name='order',
            name='type_of_work',
            field=models.ForeignKey(blank=True, help_text='The type of work requested.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.typeofwork'),
        ),
        migrations.AddField(
            model_name='order',
            name='updated_by',
            field=models.ForeignKey(blank=True, help_text='User who last updated the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='website',
            field=models.ForeignKey(blank=True, help_text='Website this record is associated with', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='websites.website'),
        ),
        migrations.AddField(
            model_name='order',
            name='writer',
            field=models.ForeignKey(blank=True, help_text='The writer assigned to this order.', limit_choices_to={'role': 'writer'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_as_writer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='writer_quality',
            field=models.ForeignKey(blank=True, help_text='Selected writer quality level.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='pricing_configs.writerquality'),
        ),
        migrations.AddField(
            model_name='failedpayment',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='failed_payments', to='orders.order'),
        ),
        migrations.AddField(
            model_name='dispute',
            name='order',
            field=models.ForeignKey(help_text='The order associated with this dispute.', on_delete=django.db.models.deletion.CASCADE, related_name='disputes', to='orders.order'),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='orders.order'),
        ),
        migrations.AddField(
            model_name='writerprogress',
            name='order',
            field=models.ForeignKey(help_text='The order associated with this progress log.', on_delete=django.db.models.deletion.CASCADE, related_name='progress_logs', to='orders.order'),
        ),
        migrations.AddField(
            model_name='writerprogress',
            name='writer',
            field=models.ForeignKey(help_text='The writer associated with this progress log.', limit_choices_to={'role': 'writer'}, on_delete=django.db.models.deletion.CASCADE, related_name='progress_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='disputewriterresponse',
            unique_together={('dispute', 'responded_by')},
        ),
    ]
