import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files_management', '0002_filequota'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ----------------------------------------------------------------
        # Add delivery tracking fields to FileAttachment
        # ----------------------------------------------------------------
        migrations.AddField(
            model_name='fileattachment',
            name='delivery_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('submitted', 'Submitted for Delivery'),
                    ('locked', 'Locked — Payment Required'),
                    ('approved', 'Approved for Download'),
                    ('rejected', 'Rejected by Staff'),
                ],
                db_index=True,
                default='pending',
                help_text='Delivery lifecycle state for final and milestone files.',
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='is_submitted',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text=(
                    'True once the writer (or staff) has explicitly submitted '
                    'this file as the delivery candidate.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='submitted_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Who pressed Submit Final.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='submitted_file_attachments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='submitted_on_behalf_of',
            field=models.ForeignKey(
                blank=True,
                help_text='Writer the staff member acted for, if applicable.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='file_attachments_submitted_on_behalf',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='submission_reason',
            field=models.TextField(
                blank=True,
                help_text='Required when staff submits on behalf of a writer.',
            ),
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='submitted_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the file was submitted for delivery.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='first_downloaded_at',
            field=models.DateTimeField(
                blank=True,
                help_text="Timestamp of the client's first successful download.",
                null=True,
            ),
        ),

        # ----------------------------------------------------------------
        # Create FileDeliveryGuardResult
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name='FileDeliveryGuardResult',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'result',
                    models.CharField(
                        choices=[
                            ('allowed', 'Allowed'),
                            ('blocked', 'Blocked'),
                        ],
                        db_index=True,
                        max_length=16,
                    ),
                ),
                (
                    'blocked_reason',
                    models.CharField(
                        blank=True,
                        choices=[
                            ('balance_due', 'Outstanding Balance'),
                            ('scan_pending', 'Scan Not Completed'),
                            ('scan_failed', 'Scan Failed or Infected'),
                            ('not_submitted', 'File Not Submitted for Delivery'),
                            ('approval_pending', 'Awaiting Staff Approval'),
                            ('rejected', 'File Rejected by Staff'),
                            ('guard_error', 'Guard Check Error'),
                        ],
                        help_text='Populated only when result is blocked.',
                        max_length=32,
                    ),
                ),
                (
                    'amount_due',
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text='Outstanding balance at the time of check, for display.',
                        max_digits=12,
                        null=True,
                    ),
                ),
                (
                    'checked_at',
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                (
                    'unlocked_at',
                    models.DateTimeField(
                        blank=True,
                        help_text='Set when the guard first returns ALLOWED for this attachment.',
                        null=True,
                    ),
                ),
                (
                    'attachment',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='delivery_guard_results',
                        to='files_management.fileattachment',
                    ),
                ),
                (
                    'checked_by',
                    models.ForeignKey(
                        blank=True,
                        help_text='User who triggered the guard check. Null for system checks.',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='delivery_guard_checks',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['-checked_at'],
            },
        ),
        migrations.AddIndex(
            model_name='filedeliveryguardresult',
            index=models.Index(
                fields=['attachment', 'result'],
                name='files_mgmt_guard_attach_result_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='filedeliveryguardresult',
            index=models.Index(
                fields=['attachment', 'checked_at'],
                name='files_mgmt_guard_attach_checked_idx',
            ),
        ),
    ]
