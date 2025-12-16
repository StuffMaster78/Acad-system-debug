# Generated manually for WriterOrderPriority model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_add_writer_request_counter_offer_fields'),
        ('writer_management', '0017_add_performance_indexes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WriterOrderPriority',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'priority',
                    models.CharField(
                        choices=[
                            ('high', 'High Priority'),
                            ('medium', 'Medium Priority'),
                            ('low', 'Low Priority'),
                        ],
                        default='medium',
                        help_text=(
                            'Priority level: high, medium, or low.'
                        ),
                        max_length=10
                    )
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text='When the priority was first set.'
                    )
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text='When the priority was last updated.'
                    )
                ),
                (
                    'notes',
                    models.TextField(
                        blank=True,
                        help_text=(
                            'Optional notes about why this priority '
                            'was set.'
                        ),
                        max_length=500,
                        null=True
                    )
                ),
                (
                    'order',
                    models.ForeignKey(
                        help_text=(
                            'The order this priority applies to.'
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='writer_priorities',
                        to='orders.order'
                    )
                ),
                (
                    'writer',
                    models.ForeignKey(
                        help_text='The writer who set this priority.',
                        limit_choices_to={'role': 'writer'},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='order_priorities',
                        to=settings.AUTH_USER_MODEL
                    )
                ),
            ],
            options={
                'verbose_name': 'Writer Order Priority',
                'verbose_name_plural': 'Writer Order Priorities',
                'ordering': ['-updated_at'],
                'unique_together': {('writer', 'order')},
            },
        ),
        migrations.AddIndex(
            model_name='writerorderpriority',
            index=models.Index(
                fields=['writer', 'priority'],
                name='writer_mana_writer__priority_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='writerorderpriority',
            index=models.Index(
                fields=['order', 'priority'],
                name='writer_mana_order__priority_idx'
            ),
        ),
    ]
