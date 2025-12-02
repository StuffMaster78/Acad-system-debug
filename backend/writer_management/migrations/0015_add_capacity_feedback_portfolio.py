# Generated manually
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('order_configs', '0004_alter_englishtype_code_alter_englishtype_name_and_more'),
        ('writer_management', '0014_add_advance_payment_models'),
        ('websites', '0002_add_payment_settings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WriterCapacity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_active_orders', models.PositiveIntegerField(default=5, help_text='Maximum number of active orders at once')),
                ('current_active_orders', models.PositiveIntegerField(default=0, help_text='Current number of active orders (auto-updated)')),
                ('is_available', models.BooleanField(default=True, help_text='Whether writer is currently accepting new orders')),
                ('availability_message', models.TextField(blank=True, help_text="Optional message about availability (e.g., 'On vacation until...')")),
                ('blackout_dates', models.JSONField(blank=True, default=list, help_text="List of blackout dates: [{'start': '2024-01-01', 'end': '2024-01-07', 'reason': 'Vacation'}]")),
                ('preferred_deadline_buffer_days', models.PositiveIntegerField(default=3, help_text='Preferred minimum days before deadline when accepting orders')),
                ('max_orders_per_day', models.PositiveIntegerField(blank=True, help_text='Maximum orders to accept per day (null = unlimited)', null=True)),
                ('auto_accept_orders', models.BooleanField(default=False, help_text='Automatically accept orders matching preferences')),
                ('auto_accept_preferred_only', models.BooleanField(default=False, help_text='Only auto-accept from preferred clients')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_capacities', to='websites.website')),
                ('writer', models.OneToOneField(limit_choices_to={'role': 'writer'}, on_delete=django.db.models.deletion.CASCADE, related_name='capacity_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Writer Capacity',
                'verbose_name_plural': 'Writer Capacities',
                'unique_together': {('writer', 'website')},
            },
        ),
        migrations.CreateModel(
            name='EditorWorkload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_active_tasks', models.PositiveIntegerField(default=10, help_text='Maximum number of active editing tasks')),
                ('current_active_tasks', models.PositiveIntegerField(default=0, help_text='Current number of active tasks (auto-updated)')),
                ('is_available', models.BooleanField(default=True, help_text='Whether editor is currently accepting new tasks')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('editor', models.OneToOneField(limit_choices_to={'role': 'editor'}, on_delete=django.db.models.deletion.CASCADE, related_name='workload_settings', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editor_workloads', to='websites.website')),
            ],
            options={
                'verbose_name': 'Editor Workload',
                'verbose_name_plural': 'Editor Workloads',
                'unique_together': {('editor', 'website')},
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_type', models.CharField(choices=[('editor_to_writer', 'Editor to Writer'), ('client_to_writer', 'Client to Writer'), ('client_to_editor', 'Client to Editor'), ('writer_to_client', 'Writer to Client')], max_length=20)),
                ('overall_rating', models.PositiveIntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], help_text='Overall rating (1-5)')),
                ('quality_rating', models.PositiveIntegerField(blank=True, choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], null=True)),
                ('communication_rating', models.PositiveIntegerField(blank=True, choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], null=True)),
                ('timeliness_rating', models.PositiveIntegerField(blank=True, choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], null=True)),
                ('professionalism_rating', models.PositiveIntegerField(blank=True, choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], null=True)),
                ('strengths', models.TextField(blank=True, help_text='What went well / strengths')),
                ('areas_for_improvement', models.TextField(blank=True, help_text='Areas that need improvement')),
                ('specific_feedback', models.TextField(blank=True, help_text='Specific, actionable feedback')),
                ('feedback_points', models.JSONField(blank=True, default=list, help_text="List of specific feedback points: [{'section': 'Introduction', 'issue': '...', 'suggestion': '...'}]")),
                ('is_public', models.BooleanField(default=False, help_text='Whether this feedback is visible to others (for portfolios)')),
                ('is_anonymous', models.BooleanField(default=False, help_text='Whether feedback is anonymous')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks_given', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='orders.order')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks_received', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='websites.website')),
            ],
            options={
                'verbose_name': 'Feedback',
                'verbose_name_plural': 'Feedbacks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FeedbackHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_feedbacks', models.PositiveIntegerField(default=0)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('average_quality_rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('average_communication_rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('average_timeliness_rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('editor_feedbacks_count', models.PositiveIntegerField(default=0)),
                ('client_feedbacks_count', models.PositiveIntegerField(default=0)),
                ('last_30_days_rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('last_90_days_rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('last_calculated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_history', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_histories', to='websites.website')),
            ],
            options={
                'verbose_name': 'Feedback History',
                'verbose_name_plural': 'Feedback Histories',
                'unique_together': {('user', 'website')},
            },
        ),
        migrations.CreateModel(
            name='WriterPortfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=False, help_text='Whether portfolio is enabled (opt-in)')),
                ('visibility', models.CharField(choices=[('private', 'Private'), ('clients_only', 'Clients Only'), ('public', 'Public')], default='clients_only', max_length=20)),
                ('bio', models.TextField(blank=True, help_text='Writer bio/introduction')),
                ('years_of_experience', models.PositiveIntegerField(blank=True, help_text='Years of writing experience', null=True)),
                ('education', models.TextField(blank=True, help_text='Educational background')),
                ('certifications', models.JSONField(blank=True, default=list, help_text="List of certifications: [{'name': '...', 'issuer': '...', 'year': 2020}]")),
                ('total_orders_completed', models.PositiveIntegerField(default=0, help_text='Total orders completed')),
                ('average_rating', models.DecimalField(decimal_places=2, default=0.0, help_text='Average rating from feedback', max_digits=3)),
                ('on_time_delivery_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of orders delivered on time', max_digits=5)),
                ('show_contact_info', models.BooleanField(default=False, help_text='Whether to show contact information')),
                ('show_order_history', models.BooleanField(default=False, help_text='Whether to show order history')),
                ('show_earnings', models.BooleanField(default=False, help_text='Whether to show earnings information')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('writer', models.OneToOneField(limit_choices_to={'role': 'writer'}, on_delete=django.db.models.deletion.CASCADE, related_name='portfolio', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_portfolios', to='websites.website')),
            ],
            options={
                'verbose_name': 'Writer Portfolio',
                'verbose_name_plural': 'Writer Portfolios',
                'unique_together': {('writer', 'website')},
            },
        ),
        migrations.CreateModel(
            name='PortfolioSample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the sample work', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description of the sample')),
                ('file', models.FileField(blank=True, help_text='Sample file (anonymized if from order)', null=True, upload_to='portfolio_samples/')),
                ('content_preview', models.TextField(blank=True, help_text='Text preview of the sample')),
                ('is_anonymized', models.BooleanField(default=True, help_text='Whether client information has been removed')),
                ('is_featured', models.BooleanField(default=False, help_text='Whether this is a featured sample')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source_order', models.ForeignKey(blank=True, help_text='The order this sample came from (if applicable)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portfolio_samples', to='orders.order')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.subject')),
                ('type_of_work', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.typeofwork')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_samples', to='websites.website')),
                ('writer', models.ForeignKey(limit_choices_to={'role': 'writer'}, on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_samples', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Portfolio Sample',
                'verbose_name_plural': 'Portfolio Samples',
                'ordering': ['-is_featured', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='writercapacity',
            index=models.Index(fields=['writer', 'website', 'is_available'], name='writer_mana_capacity_writer_idx'),
        ),
        migrations.AddIndex(
            model_name='writercapacity',
            index=models.Index(fields=['is_available', 'current_active_orders'], name='writer_mana_capacity_available_idx'),
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['order', 'feedback_type'], name='writer_mana_feedback_order_idx'),
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['to_user', 'feedback_type'], name='writer_mana_feedback_to_user_idx'),
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['from_user', 'created_at'], name='writer_mana_feedback_from_user_idx'),
        ),
        migrations.AddIndex(
            model_name='feedbackhistory',
            index=models.Index(fields=['user', 'website'], name='writer_mana_feedback_history_user_idx'),
        ),
        migrations.AddIndex(
            model_name='feedbackhistory',
            index=models.Index(fields=['average_rating'], name='writer_mana_feedback_history_rating_idx'),
        ),
        migrations.AddIndex(
            model_name='writerportfolio',
            index=models.Index(fields=['writer', 'website', 'is_enabled'], name='writer_mana_portfolio_writer_idx'),
        ),
        migrations.AddIndex(
            model_name='writerportfolio',
            index=models.Index(fields=['is_enabled', 'visibility'], name='writer_mana_portfolio_enabled_idx'),
        ),
        migrations.AddIndex(
            model_name='portfoliosample',
            index=models.Index(fields=['writer', 'website'], name='writer_mana_portfolio_sample_writer_idx'),
        ),
        migrations.AddIndex(
            model_name='portfoliosample',
            index=models.Index(fields=['is_featured'], name='writer_mana_is_feat_idx'),
        ),
        migrations.AddField(
            model_name='writercapacity',
            name='preferred_subjects',
            field=models.ManyToManyField(blank=True, help_text='Subjects this writer prefers to work on', related_name='preferred_writers', to='order_configs.subject'),
        ),
        migrations.AddField(
            model_name='writercapacity',
            name='preferred_types_of_work',
            field=models.ManyToManyField(blank=True, help_text='Types of work this writer prefers', related_name='preferred_writers', to='order_configs.typeofwork'),
        ),
        migrations.AddField(
            model_name='editorworkload',
            name='preferred_subjects',
            field=models.ManyToManyField(blank=True, related_name='preferred_editors', to='order_configs.subject'),
        ),
        migrations.AddField(
            model_name='editorworkload',
            name='preferred_types_of_work',
            field=models.ManyToManyField(blank=True, related_name='preferred_editors', to='order_configs.typeofwork'),
        ),
        migrations.AddField(
            model_name='writerportfolio',
            name='specialties',
            field=models.ManyToManyField(blank=True, help_text='Subjects this writer specializes in', related_name='portfolio_specialists', to='order_configs.subject'),
        ),
        # Note: sample_works ManyToMany is added after PortfolioSample is created
        migrations.AddField(
            model_name='writerportfolio',
            name='sample_works',
            field=models.ManyToManyField(blank=True, help_text='Sample work pieces', related_name='portfolios', to='writer_management.portfoliosample'),
        ),
    ]

