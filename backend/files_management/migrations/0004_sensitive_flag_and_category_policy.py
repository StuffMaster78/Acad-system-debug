from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files_management', '0003_delivery_fields_and_guard_result'),
    ]

    operations = [
        # ----------------------------------------------------------------
        # FileAttachment — is_sensitive flag
        # ----------------------------------------------------------------
        migrations.AddField(
            model_name='fileattachment',
            name='is_sensitive',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text=(
                    'Sensitive files (credentials, portal screenshots, private '
                    'access documents) require an explicit FileAccessGrant for '
                    'non-staff users. Every access is audited. Full vault mode '
                    'enforced here.'
                ),
            ),
        ),

        # ----------------------------------------------------------------
        # FileCategory — per-category policy fields
        # ----------------------------------------------------------------
        migrations.AddField(
            model_name='filecategory',
            name='default_visibility',
            field=models.CharField(
                choices=[
                    ('private', 'Private'),
                    ('public', 'Public'),
                    ('staff_only', 'Staff Only'),
                    ('owner_only', 'Owner Only'),
                    ('tenant_staff', 'Tenant Staff'),
                    ('internal_only', 'Internal Only'),
                    ('order_participants', 'Order Participants'),
                    ('conversation_participants', 'Conversation Participants'),
                    ('writer_and_staff', 'Writer And Staff'),
                    ('client_and_staff', 'Client And Staff'),
                    ('client_writer_staff', 'Client Writer Staff'),
                    ('cms_public', 'CMS Public'),
                ],
                default='private',
                help_text=(
                    'Default visibility applied to attachments in this category '
                    'when no visibility is explicitly set by the uploader.'
                ),
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name='filecategory',
            name='max_file_size_bytes',
            field=models.PositiveBigIntegerField(
                blank=True,
                help_text=(
                    'Maximum upload size for this category in bytes. '
                    'Overrides the FilePolicy limit when set.'
                ),
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='filecategory',
            name='require_scan_before_download',
            field=models.BooleanField(
                default=True,
                help_text=(
                    'Block downloads until the file scan has passed. '
                    'Disable only for categories where scan latency is '
                    'unacceptable.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='filecategory',
            name='require_approval_before_download',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Require explicit staff approval before files in this '
                    'category become downloadable. Useful for screenshots and '
                    'grade evidence.'
                ),
            ),
        ),
    ]
