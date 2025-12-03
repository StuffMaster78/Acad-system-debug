# Generated migration for authentication security features

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_merge_20251201_0817'),
        ('websites', '0006_enhance_file_versioning'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Password Security Models
        migrations.CreateModel(
            name='PasswordHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password_hash', models.CharField(help_text='Hashed password (stored securely)', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When this password was set')),
                ('user', models.ForeignKey(help_text='User whose password history is tracked', on_delete=django.db.models.deletion.CASCADE, related_name='password_history', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context for multi-tenancy', on_delete=django.db.models.deletion.CASCADE, related_name='password_histories', to='websites.website')),
            ],
            options={
                'verbose_name': 'Password History',
                'verbose_name_plural': 'Password Histories',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PasswordExpirationPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password_changed_at', models.DateTimeField(default=timezone.now, help_text='When the password was last changed')),
                ('expires_in_days', models.IntegerField(default=90, help_text='Number of days before password expires')),
                ('warning_days_before', models.IntegerField(default=7, help_text='Days before expiration to show warning')),
                ('is_exempt', models.BooleanField(default=False, help_text='If True, password never expires')),
                ('last_warning_sent', models.DateTimeField(blank=True, help_text='When the last expiration warning was sent', null=True)),
                ('user', models.OneToOneField(help_text='User whose password expiration is tracked', on_delete=django.db.models.deletion.CASCADE, related_name='password_expiration_policy', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='password_expiration_policies', to='websites.website')),
            ],
            options={
                'verbose_name': 'Password Expiration Policy',
                'verbose_name_plural': 'Password Expiration Policies',
            },
        ),
        migrations.CreateModel(
            name='PasswordBreachCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password_hash_prefix', models.CharField(help_text='First 5 characters of SHA-1 hash (for HIBP API)', max_length=5)),
                ('is_breached', models.BooleanField(default=False, help_text='Whether password was found in breach database')),
                ('breach_count', models.IntegerField(default=0, help_text='Number of times password appeared in breaches')),
                ('checked_at', models.DateTimeField(auto_now_add=True, help_text='When the check was performed')),
                ('action_taken', models.CharField(choices=[('none', 'No Action'), ('warned', 'User Warned'), ('forced_change', 'Password Change Forced')], default='none', help_text='Action taken based on breach check', max_length=50)),
                ('user', models.ForeignKey(help_text='User whose password was checked', on_delete=django.db.models.deletion.CASCADE, related_name='password_breach_checks', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='password_breach_checks', to='websites.website')),
            ],
            options={
                'verbose_name': 'Password Breach Check',
                'verbose_name_plural': 'Password Breach Checks',
                'ordering': ['-checked_at'],
            },
        ),
        # Account Security Models
        migrations.CreateModel(
            name='AccountSuspension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_suspended', models.BooleanField(default=False, help_text='Whether account is currently suspended')),
                ('suspended_at', models.DateTimeField(blank=True, help_text='When account was suspended', null=True)),
                ('suspension_reason', models.TextField(blank=True, help_text='Reason for suspension (user-provided)')),
                ('scheduled_reactivation', models.DateTimeField(blank=True, help_text='Scheduled reactivation date (optional)', null=True)),
                ('reactivated_at', models.DateTimeField(blank=True, help_text='When account was reactivated', null=True)),
                ('user', models.OneToOneField(help_text='User whose account is suspended', on_delete=django.db.models.deletion.CASCADE, related_name='account_suspension', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='account_suspensions', to='websites.website')),
            ],
            options={
                'verbose_name': 'Account Suspension',
                'verbose_name_plural': 'Account Suspensions',
            },
        ),
        migrations.CreateModel(
            name='IPWhitelist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(help_text='Whitelisted IP address')),
                ('label', models.CharField(blank=True, help_text="User-friendly label (e.g., 'Home', 'Office')", max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When this IP was whitelisted')),
                ('last_used', models.DateTimeField(blank=True, help_text='When this IP was last used for login', null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this whitelist entry is active')),
                ('user', models.ForeignKey(help_text='User who owns this whitelist entry', on_delete=django.db.models.deletion.CASCADE, related_name='ip_whitelist_entries', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='ip_whitelist_entries', to='websites.website')),
            ],
            options={
                'verbose_name': 'IP Whitelist Entry',
                'verbose_name_plural': 'IP Whitelist Entries',
            },
        ),
        migrations.CreateModel(
            name='UserIPWhitelistSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=False, help_text='Whether IP whitelist is enabled for this user')),
                ('allow_emergency_bypass', models.BooleanField(default=True, help_text='Allow emergency bypass via email verification')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(help_text='User whose whitelist settings are configured', on_delete=django.db.models.deletion.CASCADE, related_name='ip_whitelist_settings', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='ip_whitelist_settings', to='websites.website')),
            ],
            options={
                'verbose_name': 'IP Whitelist Settings',
                'verbose_name_plural': 'IP Whitelist Settings',
            },
        ),
        migrations.CreateModel(
            name='EmailChangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_email', models.EmailField(help_text='Current email address', max_length=254)),
                ('new_email', models.EmailField(help_text='New email address to change to', max_length=254)),
                ('verification_token', models.CharField(help_text='Token for verifying new email', max_length=255, unique=True)),
                ('old_email_verification_token', models.CharField(blank=True, help_text='Token for confirming old email', max_length=255, null=True)),
                ('verified', models.BooleanField(default=False, help_text='Whether new email has been verified')),
                ('old_email_confirmed', models.BooleanField(default=False, help_text='Whether old email change was confirmed')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When change was requested')),
                ('expires_at', models.DateTimeField(help_text='When this request expires')),
                ('completed_at', models.DateTimeField(blank=True, help_text='When email change was completed', null=True)),
                ('user', models.ForeignKey(help_text='User requesting email change', on_delete=django.db.models.deletion.CASCADE, related_name='email_change_requests', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='email_change_requests', to='websites.website')),
            ],
            options={
                'verbose_name': 'Email Change Request',
                'verbose_name_plural': 'Email Change Requests',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PhoneVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(help_text='Phone number to verify (E.164 format)', max_length=20)),
                ('verification_code', models.CharField(help_text='6-digit verification code', max_length=6)),
                ('is_verified', models.BooleanField(default=False, help_text='Whether phone number is verified')),
                ('verified_at', models.DateTimeField(blank=True, help_text='When phone was verified', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When verification was initiated')),
                ('expires_at', models.DateTimeField(help_text='When verification code expires')),
                ('attempts', models.IntegerField(default=0, help_text='Number of verification attempts')),
                ('max_attempts', models.IntegerField(default=3, help_text='Maximum verification attempts allowed')),
                ('user', models.ForeignKey(help_text='User whose phone is being verified', on_delete=django.db.models.deletion.CASCADE, related_name='phone_verifications', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='phone_verifications', to='websites.website')),
            ],
            options={
                'verbose_name': 'Phone Verification',
                'verbose_name_plural': 'Phone Verifications',
                'ordering': ['-created_at'],
            },
        ),
        # Session Limits
        migrations.CreateModel(
            name='SessionLimitPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_concurrent_sessions', models.IntegerField(default=3, help_text='Maximum number of concurrent active sessions')),
                ('allow_unlimited_trusted', models.BooleanField(default=False, help_text='Allow unlimited sessions from trusted devices')),
                ('revoke_oldest_on_limit', models.BooleanField(default=True, help_text='Revoke oldest session when limit is reached')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(help_text='User whose session limits are configured', on_delete=django.db.models.deletion.CASCADE, related_name='session_limit_policy', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='session_limit_policies', to='websites.website')),
            ],
            options={
                'verbose_name': 'Session Limit Policy',
                'verbose_name_plural': 'Session Limit Policies',
            },
        ),
        # Indexes
        migrations.AddIndex(
            model_name='passwordhistory',
            index=models.Index(fields=['user', '-created_at'], name='authenticat_user_id_created_idx'),
        ),
        migrations.AddIndex(
            model_name='passwordhistory',
            index=models.Index(fields=['website', 'user'], name='authenticat_website_user_idx'),
        ),
        migrations.AddIndex(
            model_name='passwordexpirationpolicy',
            index=models.Index(fields=['user', 'password_changed_at'], name='authenticat_user_id_changed_idx'),
        ),
        migrations.AddIndex(
            model_name='passwordexpirationpolicy',
            index=models.Index(fields=['website', 'user'], name='authenticat_website_user_pol_idx'),
        ),
        migrations.AddIndex(
            model_name='passwordbreachcheck',
            index=models.Index(fields=['user', '-checked_at'], name='authenticat_user_id_checked_idx'),
        ),
        migrations.AddIndex(
            model_name='passwordbreachcheck',
            index=models.Index(fields=['is_breached', 'action_taken'], name='authenticat_breached_action_idx'),
        ),
        migrations.AddIndex(
            model_name='accountsuspension',
            index=models.Index(fields=['user', 'is_suspended'], name='authenticat_user_id_suspended_idx'),
        ),
        migrations.AddIndex(
            model_name='accountsuspension',
            index=models.Index(fields=['scheduled_reactivation'], name='authenticat_scheduled_react_idx'),
        ),
        migrations.AddIndex(
            model_name='ipwhitelist',
            index=models.Index(fields=['user', 'is_active'], name='authenticat_user_id_active_idx'),
        ),
        migrations.AddIndex(
            model_name='ipwhitelist',
            index=models.Index(fields=['ip_address'], name='authenticat_ip_address_idx'),
        ),
        migrations.AddIndex(
            model_name='emailchangerequest',
            index=models.Index(fields=['verification_token'], name='authenticat_verification_token_idx'),
        ),
        migrations.AddIndex(
            model_name='emailchangerequest',
            index=models.Index(fields=['expires_at'], name='authenticat_expires_at_idx'),
        ),
        migrations.AddIndex(
            model_name='phoneverification',
            index=models.Index(fields=['phone_number'], name='authenticat_phone_number_idx'),
        ),
        migrations.AddIndex(
            model_name='phoneverification',
            index=models.Index(fields=['expires_at'], name='authenticat_phone_expires_idx'),
        ),
        migrations.AddConstraint(
            model_name='ipwhitelist',
            constraint=models.UniqueConstraint(fields=['user', 'website', 'ip_address'], name='unique_user_website_ip'),
        ),
    ]

