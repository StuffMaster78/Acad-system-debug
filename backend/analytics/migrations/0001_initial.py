# Generated manually
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0004_add_admin_notifications_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_start', models.DateField(help_text='Start of analytics period')),
                ('period_end', models.DateField(help_text='End of analytics period')),
                ('total_spend', models.DecimalField(decimal_places=2, default=0.0, help_text='Total amount spent in period', max_digits=10)),
                ('average_order_value', models.DecimalField(decimal_places=2, default=0.0, help_text='Average order value', max_digits=10)),
                ('total_orders', models.PositiveIntegerField(default=0, help_text='Total orders in period')),
                ('on_time_delivery_count', models.PositiveIntegerField(default=0, help_text='Orders delivered on time')),
                ('late_delivery_count', models.PositiveIntegerField(default=0, help_text='Orders delivered late')),
                ('on_time_delivery_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of orders delivered on time', max_digits=5)),
                ('total_revisions', models.PositiveIntegerField(default=0, help_text='Total revision requests')),
                ('revision_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of orders with revisions', max_digits=5)),
                ('average_revisions_per_order', models.DecimalField(decimal_places=2, default=0.0, help_text='Average number of revisions per order', max_digits=5)),
                ('top_writers', models.JSONField(blank=True, default=list, help_text="Top performing writers: [{'writer_id': 1, 'orders': 5, 'avg_rating': 4.5}]")),
                ('average_writer_rating', models.DecimalField(decimal_places=2, default=0.0, help_text='Average rating of writers used', max_digits=3)),
                ('calculated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(limit_choices_to={'role': 'client'}, on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_analytics', to='websites.website')),
            ],
            options={
                'verbose_name': 'Client Analytics',
                'verbose_name_plural': 'Client Analytics',
                'unique_together': {('client', 'website', 'period_start', 'period_end')},
            },
        ),
        migrations.CreateModel(
            name='ClientAnalyticsSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snapshot_date', models.DateField(help_text='Date of snapshot')),
                ('snapshot_type', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='daily', max_length=20)),
                ('total_spend', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_orders', models.PositiveIntegerField(default=0)),
                ('on_time_delivery_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('revision_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(limit_choices_to={'role': 'client'}, on_delete=django.db.models.deletion.CASCADE, related_name='analytics_snapshots', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_analytics_snapshots', to='websites.website')),
            ],
            options={
                'unique_together': {('client', 'website', 'snapshot_date', 'snapshot_type')},
                'ordering': ['-snapshot_date'],
            },
        ),
        migrations.CreateModel(
            name='WriterAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('total_earnings', models.DecimalField(decimal_places=2, default=0.0, help_text='Total earnings in period', max_digits=10)),
                ('average_order_earnings', models.DecimalField(decimal_places=2, default=0.0, help_text='Average earnings per order', max_digits=10)),
                ('total_hours_worked', models.DecimalField(decimal_places=2, default=0.0, help_text='Total hours worked (estimated from orders)', max_digits=8)),
                ('effective_hourly_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Effective hourly rate (earnings / hours)', max_digits=10)),
                ('total_orders_completed', models.PositiveIntegerField(default=0)),
                ('total_orders_in_progress', models.PositiveIntegerField(default=0)),
                ('average_completion_time_hours', models.DecimalField(decimal_places=2, default=0.0, help_text='Average time to complete order', max_digits=8)),
                ('total_revisions', models.PositiveIntegerField(default=0)),
                ('revision_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of orders requiring revisions', max_digits=5)),
                ('average_revisions_per_order', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('approval_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of orders approved without revision', max_digits=5)),
                ('rejection_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of orders rejected', max_digits=5)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0.0, help_text='Average rating from feedback', max_digits=3)),
                ('quality_score', models.DecimalField(decimal_places=2, default=0.0, help_text='Calculated quality score', max_digits=5)),
                ('calculated_at', models.DateTimeField(auto_now=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_analytics', to='websites.website')),
                ('writer', models.ForeignKey(limit_choices_to={'role': 'writer'}, on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Writer Analytics',
                'verbose_name_plural': 'Writer Analytics',
                'unique_together': {('writer', 'website', 'period_start', 'period_end')},
            },
        ),
        migrations.CreateModel(
            name='WriterAnalyticsSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snapshot_date', models.DateField()),
                ('snapshot_type', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='daily', max_length=20)),
                ('total_earnings', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('effective_hourly_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('revision_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('approval_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_analytics_snapshots', to='websites.website')),
                ('writer', models.ForeignKey(limit_choices_to={'role': 'writer'}, on_delete=django.db.models.deletion.CASCADE, related_name='analytics_snapshots', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('writer', 'website', 'snapshot_date', 'snapshot_type')},
                'ordering': ['-snapshot_date'],
            },
        ),
        migrations.CreateModel(
            name='ClassPerformanceReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('summary', 'Summary'), ('detailed', 'Detailed'), ('student_list', 'Student List'), ('performance_by_group', 'Performance by Group')], default='summary', max_length=50)),
                ('report_data', models.JSONField(default=dict, help_text='Report data in JSON format')),
                ('file', models.FileField(blank=True, help_text='Exported report file (PDF, CSV, etc.)', null=True, upload_to='class_reports/')),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('class_analytics', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='analytics.classanalytics')),
                ('generated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
        migrations.CreateModel(
            name='ClassAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_name', models.CharField(help_text='Name/identifier for the class/bulk order', max_length=255)),
                ('class_id', models.CharField(blank=True, help_text='Optional class ID', max_length=100)),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('total_students', models.PositiveIntegerField(default=0, help_text='Total students in class')),
                ('active_students', models.PositiveIntegerField(default=0, help_text='Students who have placed orders')),
                ('attendance_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of students who placed orders', max_digits=5)),
                ('total_orders', models.PositiveIntegerField(default=0)),
                ('completed_orders', models.PositiveIntegerField(default=0)),
                ('completion_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of orders completed', max_digits=5)),
                ('average_grade', models.DecimalField(blank=True, decimal_places=2, help_text='Average grade/score (if applicable)', max_digits=5, null=True)),
                ('on_time_submission_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of orders submitted on time', max_digits=5)),
                ('group_performance', models.JSONField(blank=True, default=list, help_text="Performance by group: [{'group_name': 'Group A', 'completion_rate': 85.5, 'avg_grade': 4.2}]")),
                ('calculated_at', models.DateTimeField(auto_now=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_analytics', to='websites.website')),
            ],
            options={
                'verbose_name': 'Class Analytics',
                'verbose_name_plural': 'Class Analytics',
                'unique_together': {('website', 'class_name', 'class_id', 'period_start', 'period_end')},
            },
        ),
        migrations.AddIndex(
            model_name='clientanalytics',
            index=models.Index(fields=['client', 'website', 'period_start'], name='analytics_c_client__idx'),
        ),
        migrations.AddIndex(
            model_name='clientanalyticssnapshot',
            index=models.Index(fields=['client', 'website', 'snapshot_date'], name='analytics_c_client__idx'),
        ),
        migrations.AddIndex(
            model_name='writeranalytics',
            index=models.Index(fields=['writer', 'website', 'period_start'], name='analytics_w_writer__idx'),
        ),
        migrations.AddIndex(
            model_name='writeranalyticssnapshot',
            index=models.Index(fields=['writer', 'website', 'snapshot_date'], name='analytics_w_writer__idx'),
        ),
        migrations.AddIndex(
            model_name='classanalytics',
            index=models.Index(fields=['website', 'class_name', 'period_start'], name='analytics_c_website_idx'),
        ),
    ]

