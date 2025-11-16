from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fines', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Rename created_at -> submitted_at to align with current models
        migrations.RenameField(
            model_name='fineappeal',
            old_name='created_at',
            new_name='submitted_at',
        ),

        # Remove legacy 'accepted' boolean
        migrations.RemoveField(
            model_name='fineappeal',
            name='accepted',
        ),

        # Add fields present in current model definition
        migrations.AddField(
            model_name='fineappeal',
            name='status',
            field=models.CharField(max_length=20, blank=True, null=True, default='disputed'),
        ),
        migrations.AddField(
            model_name='fineappeal',
            name='escalated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fineappeal',
            name='escalated_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='escalated_appeals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fineappeal',
            name='escalated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fineappeal',
            name='escalation_reason',
            field=models.TextField(blank=True),
        ),
        # 'reviewed_by' may already exist in some DBs; if so, skip adding
        migrations.AddField(
            model_name='fineappeal',
            name='review_decision',
            field=models.CharField(max_length=20, blank=True, null=True, default='pending'),
        ),
        migrations.AddField(
            model_name='fineappeal',
            name='review_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='fineappeal',
            name='resolution_notes',
            field=models.TextField(blank=True),
        ),
    ]


