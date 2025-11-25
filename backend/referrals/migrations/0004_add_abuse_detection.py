# Generated manually for abuse detection features

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0003_pendingreferralinvitation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add abuse detection fields to Referral model
        migrations.AddField(
            model_name='referral',
            name='is_flagged',
            field=models.BooleanField(default=False, help_text='Whether this referral has been flagged for abuse.'),
        ),
        migrations.AddField(
            model_name='referral',
            name='flagged_reason',
            field=models.TextField(blank=True, help_text='Reason for flagging this referral.', null=True),
        ),
        migrations.AddField(
            model_name='referral',
            name='is_voided',
            field=models.BooleanField(default=False, help_text='Whether this referral has been voided due to abuse.'),
        ),
        migrations.AddField(
            model_name='referral',
            name='voided_at',
            field=models.DateTimeField(blank=True, help_text='When this referral was voided.', null=True),
        ),
        migrations.AddField(
            model_name='referral',
            name='voided_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Admin who voided this referral.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='voided_referrals',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        
        # Create ReferralAbuseFlag model
        migrations.CreateModel(
            name='ReferralAbuseFlag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abuse_type', models.CharField(
                    choices=[
                        ('self_referral', 'Self Referral'),
                        ('multiple_accounts', 'Multiple Accounts'),
                        ('suspicious_ip', 'Suspicious IP Pattern'),
                        ('rapid_referrals', 'Rapid Referrals'),
                        ('fake_accounts', 'Fake Accounts'),
                        ('other', 'Other')
                    ],
                    help_text='Type of suspected abuse.',
                    max_length=30
                )),
                ('reason', models.TextField(help_text='Detailed reason for flagging this referral.')),
                ('detected_at', models.DateTimeField(auto_now_add=True, help_text='When this abuse was detected.')),
                ('detected_by', models.CharField(
                    default='system',
                    help_text='Who/what detected this (system, admin username, etc).',
                    max_length=50
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending Review'),
                        ('reviewed', 'Reviewed'),
                        ('resolved', 'Resolved'),
                        ('false_positive', 'False Positive')
                    ],
                    default='pending',
                    help_text='Current status of this abuse flag.',
                    max_length=20
                )),
                ('reviewed_at', models.DateTimeField(
                    blank=True,
                    help_text='When this flag was reviewed.',
                    null=True
                )),
                ('review_notes', models.TextField(
                    blank=True,
                    help_text='Notes from the reviewer.',
                    null=True
                )),
                ('action_taken', models.TextField(
                    blank=True,
                    help_text='Action taken (e.g., referral voided, bonus revoked).',
                    null=True
                )),
                ('referral', models.ForeignKey(
                    help_text='The referral that was flagged.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='abuse_flags',
                    to='referrals.referral'
                )),
                ('reviewed_by', models.ForeignKey(
                    blank=True,
                    help_text='Admin/superadmin who reviewed this flag.',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reviewed_abuse_flags',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'ordering': ['-detected_at'],
            },
        ),
        migrations.AddIndex(
            model_name='referralabuseflag',
            index=models.Index(fields=['status', 'abuse_type'], name='referrals_r_status_abuse_idx'),
        ),
        migrations.AddIndex(
            model_name='referralabuseflag',
            index=models.Index(fields=['referral'], name='referrals_r_referra_idx'),
        ),
    ]

