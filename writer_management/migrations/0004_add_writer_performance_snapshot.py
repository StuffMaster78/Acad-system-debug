# Generated manually for WriterPerformanceSnapshot model
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0003_add_pen_name'),
        ('websites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WriterPerformanceSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('total_orders', models.PositiveIntegerField(default=0)),
                ('completed_orders', models.PositiveIntegerField(default=0)),
                ('cancelled_orders', models.PositiveIntegerField(default=0)),
                ('late_orders', models.PositiveIntegerField(default=0)),
                ('revised_orders', models.PositiveIntegerField(default=0)),
                ('disputed_orders', models.PositiveIntegerField(default=0)),
                ('hvo_orders', models.PositiveIntegerField(default=0, help_text='High value orders')),
                ('total_pages', models.PositiveIntegerField(default=0)),
                ('preferred_orders', models.PositiveIntegerField(default=0)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('bonuses', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('tips', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('client_revenue', models.DecimalField(decimal_places=2, default=0.0, help_text="Total client revenue for writer's orders", max_digits=12)),
                ('profit_contribution', models.DecimalField(decimal_places=2, default=0.0, help_text='Client revenue - writer cost', max_digits=12)),
                ('average_rating', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('completion_rate', models.DecimalField(decimal_places=4, default=0.0, max_digits=5)),
                ('lateness_rate', models.DecimalField(decimal_places=4, default=0.0, max_digits=5)),
                ('revision_rate', models.DecimalField(decimal_places=4, default=0.0, max_digits=5)),
                ('dispute_rate', models.DecimalField(decimal_places=4, default=0.0, max_digits=5)),
                ('preferred_order_rate', models.DecimalField(decimal_places=4, default=0.0, max_digits=5)),
                ('average_turnaround_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('composite_score', models.DecimalField(blank=True, decimal_places=2, help_text='Weighted score used to compare writer performance', max_digits=5, null=True)),
                ('better_than_percent', models.DecimalField(blank=True, decimal_places=2, help_text='Percent of writers this one outperforms in the same period', max_digits=5, null=True)),
                ('is_cached', models.BooleanField(default=False)),
                ('generated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_performance_snapshots', to='websites.website')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_snapshots', to='writer_management.writerprofile')),
            ],
            options={
                'verbose_name': 'Writer Performance Snapshot',
                'verbose_name_plural': 'Writer Performance Snapshots',
            },
        ),
        migrations.AddIndex(
            model_name='writerperformancesnapshot',
            index=models.Index(fields=['website', 'writer', 'period_end'], name='writer_mana_website_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='writerperformancesnapshot',
            unique_together={('website', 'writer', 'period_start', 'period_end')},
        ),
    ]

