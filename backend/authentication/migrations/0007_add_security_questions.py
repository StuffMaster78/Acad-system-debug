# Generated migration for security questions

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_add_security_features'),
        ('websites', '0006_enhance_file_versioning'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(help_text='The security question text', max_length=500, unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this question is available for selection')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Security Question',
                'verbose_name_plural': 'Security Questions',
                'ordering': ['question_text'],
            },
        ),
        migrations.CreateModel(
            name='UserSecurityQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_question', models.CharField(blank=True, help_text='Custom question if user chose to write their own', max_length=500)),
                ('encrypted_answer', models.TextField(help_text='Encrypted answer to the security question')),
                ('answer_hash', models.CharField(help_text='Hash of answer for quick comparison (not reversible)', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this question is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(help_text='The security question', on_delete=django.db.models.deletion.CASCADE, related_name='user_questions', to='authentication.securityquestion')),
                ('user', models.ForeignKey(help_text='User who owns this security question', on_delete=django.db.models.deletion.CASCADE, related_name='security_questions', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='user_security_questions', to='websites.website')),
            ],
            options={
                'verbose_name': 'User Security Question',
                'verbose_name_plural': 'User Security Questions',
                'unique_together': {('user', 'website', 'question')},
            },
        ),
        migrations.AddIndex(
            model_name='usersecurityquestion',
            index=models.Index(fields=['user', 'website', 'is_active'], name='authenticat_user_website_active_idx'),
        ),
        migrations.AddField(
            model_name='emailchangerequest',
            name='admin_approved',
            field=models.BooleanField(default=False, help_text='Whether admin has approved the email change'),
        ),
        migrations.AddField(
            model_name='emailchangerequest',
            name='approved_at',
            field=models.DateTimeField(blank=True, help_text='When admin approved the email change', null=True),
        ),
        migrations.AddField(
            model_name='emailchangerequest',
            name='approved_by',
            field=models.ForeignKey(blank=True, help_text='Admin who approved the email change', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_email_changes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='emailchangerequest',
            name='rejection_reason',
            field=models.TextField(blank=True, help_text='Reason for rejection if rejected'),
        ),
        migrations.AddField(
            model_name='emailchangerequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('admin_approved', 'Admin Approved'), ('email_verified', 'Email Verified'), ('completed', 'Completed'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', help_text='Current status of the email change request', max_length=20),
        ),
        migrations.AddIndex(
            model_name='emailchangerequest',
            index=models.Index(fields=['status', '-created_at'], name='authenticat_status_created_idx'),
        ),
    ]

