# Generated manually to recreate WriterPerformanceMetrics model
# Migration 0020 incorrectly deleted this model, but it's still needed

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0020_alter_webhooksettings_unique_together_and_more'),
        ('websites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WriterPerformanceMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_start', models.DateField()),
                ('week_end', models.DateField()),
                ('avg_turnaround_time', models.DurationField(blank=True, null=True)),
                ('avg_rating', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('revision_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('dispute_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('lateness_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('cancellation_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('acceptance_to_completion_ratio', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('preferred_order_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('total_orders_completed', models.PositiveIntegerField(default=0)),
                ('total_pages_completed', models.PositiveIntegerField(default=0)),
                ('total_earnings', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('total_tips', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('total_bonuses', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('total_fines', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('total_profit_contribution', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Client pay - Writer earnings', max_digits=12)),
                ('hvo_orders_completed', models.PositiveIntegerField(default=0)),
                ('composite_score', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=6)),
                ('percentile_rank', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text="You're better than X% of writers", max_digits=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_metrics', to='websites.website')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_metrics', to='writer_management.writerprofile')),
            ],
            options={
                'verbose_name': 'Writer Performance Metrics',
                'verbose_name_plural': 'Writer Performance Metrics',
                'ordering': ['-week_start'],
                'unique_together': {('website', 'writer', 'week_start')},
            },
        ),
    ]

