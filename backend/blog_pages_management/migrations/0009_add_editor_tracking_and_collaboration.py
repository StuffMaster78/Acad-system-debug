# Generated manually for editor tracking and collaboration features

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_pages_management', '0008_alter_blogpost_meta_description_and_more'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('websites', '0008_set_guest_checkout_safe_defaults'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add fields to ContentTemplate for template inheritance
        migrations.AddField(
            model_name='contenttemplate',
            name='parent_template',
            field=models.ForeignKey(
                blank=True,
                help_text='Parent template for inheritance',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='child_templates',
                to='blog_pages_management.contenttemplate'
            ),
        ),
        migrations.AddField(
            model_name='contenttemplate',
            name='template_variables',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Available template variables and their descriptions'
            ),
        ),
        
        # Add metadata field to BlogPostAutoSave
        migrations.AddField(
            model_name='blogpostautosave',
            name='metadata',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Additional metadata (e.g., health check results)'
            ),
        ),
        
        # Create EditorSession model
        migrations.CreateModel(
            name='EditorSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_id', models.PositiveIntegerField()),
                ('session_start', models.DateTimeField(auto_now_add=True)),
                ('session_end', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('total_keystrokes', models.PositiveIntegerField(default=0)),
                ('total_actions', models.PositiveIntegerField(default=0)),
                ('characters_added', models.PositiveIntegerField(default=0)),
                ('characters_removed', models.PositiveIntegerField(default=0)),
                ('templates_used', models.PositiveIntegerField(default=0)),
                ('snippets_used', models.PositiveIntegerField(default=0)),
                ('blocks_used', models.PositiveIntegerField(default=0)),
                ('health_checks_run', models.PositiveIntegerField(default=0)),
                ('auto_saves_count', models.PositiveIntegerField(default=0)),
                ('manual_saves_count', models.PositiveIntegerField(default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editor_sessions', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editor_sessions', to='websites.website')),
            ],
            options={
                'ordering': ['-session_start'],
                'indexes': [
                    models.Index(fields=['user', 'session_start'], name='blog_pages__user_sess_123abc_idx'),
                    models.Index(fields=['website', 'is_active'], name='blog_pages__website_active_idx'),
                ],
            },
        ),
        
        # Create EditorAction model
        migrations.CreateModel(
            name='EditorAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[
                    ('keystroke', 'Keystroke'),
                    ('format', 'Format Change'),
                    ('insert', 'Content Insert'),
                    ('delete', 'Content Delete'),
                    ('template_use', 'Template Used'),
                    ('snippet_use', 'Snippet Used'),
                    ('block_use', 'Block Used'),
                    ('health_check', 'Health Check'),
                    ('save', 'Save'),
                    ('auto_save', 'Auto Save'),
                    ('undo', 'Undo'),
                    ('redo', 'Redo'),
                    ('copy', 'Copy'),
                    ('paste', 'Paste'),
                ], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional action data (e.g., format type, content length)')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='blog_pages_management.editorsession')),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['session', 'timestamp'], name='blog_pages__session_time_idx'),
                    models.Index(fields=['action_type', 'timestamp'], name='blog_pages__action_type_idx'),
                ],
            },
        ),
        
        # Create EditorProductivityMetrics model
        migrations.CreateModel(
            name='EditorProductivityMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('total_sessions', models.PositiveIntegerField(default=0)),
                ('average_session_duration', models.FloatField(default=0, help_text='Average session duration in minutes')),
                ('longest_session', models.FloatField(default=0, help_text='Longest session in minutes')),
                ('total_keystrokes', models.PositiveIntegerField(default=0)),
                ('average_keystrokes_per_session', models.FloatField(default=0)),
                ('total_characters_written', models.PositiveIntegerField(default=0)),
                ('templates_used_count', models.PositiveIntegerField(default=0)),
                ('snippets_used_count', models.PositiveIntegerField(default=0)),
                ('blocks_used_count', models.PositiveIntegerField(default=0)),
                ('health_checks_count', models.PositiveIntegerField(default=0)),
                ('words_per_minute', models.FloatField(default=0, help_text='Average words per minute')),
                ('content_quality_score', models.FloatField(default=0, help_text='Average content health score')),
                ('productivity_score', models.FloatField(default=0, help_text='Overall productivity score')),
                ('calculated_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productivity_metrics', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productivity_metrics', to='websites.website')),
            ],
            options={
                'unique_together': {('user', 'website', 'period_start', 'period_end')},
                'indexes': [
                    models.Index(fields=['user', 'period_start'], name='blog_pages__user_period_idx'),
                    models.Index(fields=['website', 'productivity_score'], name='blog_pages__website_score_idx'),
                ],
            },
        ),
        
        # Create CollaborativeSession model
        migrations.CreateModel(
            name='CollaborativeSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_id', models.PositiveIntegerField()),
                ('session_id', models.CharField(help_text='Unique session identifier', max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborative_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-last_activity'],
                'indexes': [
                    models.Index(fields=['content_type', 'content_id', 'is_active'], name='blog_pages__collab_content_idx'),
                    models.Index(fields=['session_id'], name='blog_pages__collab_session_idx'),
                ],
            },
        ),
        
        # Create CollaborativeEditor model
        migrations.CreateModel(
            name='CollaborativeEditor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('cursor_position', models.PositiveIntegerField(default=0, help_text='Current cursor position in content')),
                ('selection_start', models.PositiveIntegerField(blank=True, help_text='Selection start position', null=True)),
                ('selection_end', models.PositiveIntegerField(blank=True, help_text='Selection end position', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editors', to='blog_pages_management.collaborativesession')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborative_edits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('session', 'user')},
                'indexes': [
                    models.Index(fields=['session', 'is_active'], name='blog_pages__collab_editor_idx'),
                ],
            },
        ),
        
        # Create CollaborativeChange model
        migrations.CreateModel(
            name='CollaborativeChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_type', models.CharField(choices=[
                    ('insert', 'Insert'),
                    ('delete', 'Delete'),
                    ('format', 'Format'),
                    ('cursor', 'Cursor Move'),
                ], max_length=20)),
                ('position', models.PositiveIntegerField(help_text='Position in content where change occurred')),
                ('length', models.PositiveIntegerField(default=0, help_text='Length of change (for delete/format)')),
                ('content', models.TextField(blank=True, help_text='Content inserted or changed')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional change metadata (formatting, etc.)')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('applied', models.BooleanField(default=False, help_text='Whether change has been applied to content')),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='changes', to='blog_pages_management.collaborativeeditor')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='changes', to='blog_pages_management.collaborativesession')),
            ],
            options={
                'ordering': ['timestamp'],
                'indexes': [
                    models.Index(fields=['session', 'timestamp'], name='blog_pages__collab_change_sess_idx'),
                    models.Index(fields=['applied', 'timestamp'], name='blog_pages__collab_change_applied_idx'),
                ],
            },
        ),
        
        # Create CollaborativePresence model
        migrations.CreateModel(
            name='CollaborativePresence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_heartbeat', models.DateTimeField(auto_now=True)),
                ('is_online', models.BooleanField(default=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='presence', to='blog_pages_management.collaborativesession')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborative_presence', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('session', 'user')},
                'indexes': [
                    models.Index(fields=['session', 'is_online'], name='blog_pages__collab_presence_idx'),
                    models.Index(fields=['last_heartbeat'], name='blog_pages__collab_heartbeat_idx'),
                ],
            },
        ),
    ]

