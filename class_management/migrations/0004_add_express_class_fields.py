# Generated migration for ExpressClass new fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('class_management', '0003_add_classbundle_website'),
        ('websites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='expressclass',
            name='website',
            field=models.ForeignKey(
                help_text='Website this express class belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='express_classes',
                to='websites.website',
                null=True,  # Allow null temporarily for existing records
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='assigned_writer',
            field=models.ForeignKey(
                blank=True,
                help_text='Writer assigned to this express class',
                limit_choices_to={'role': 'writer'},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_express_classes',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='status',
            field=models.CharField(
                choices=[
                    ('inquiry', 'Inquiry'),
                    ('scope_review', 'Scope Review'),
                    ('priced', 'Priced'),
                    ('assigned', 'Assigned'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='inquiry',
                help_text='Current status of the express class',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='price_approved',
            field=models.BooleanField(
                default=False,
                help_text='Whether the price has been approved by admin'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Price for the express class (set by admin after scope review)',
                max_digits=10,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='school_login_link',
            field=models.URLField(
                blank=True,
                help_text='Link to school login portal'
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='school_login_username',
            field=models.CharField(
                blank=True,
                help_text='School login username',
                max_length=255
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='school_login_password',
            field=models.CharField(
                blank=True,
                help_text='School login password (encrypted/stored securely)',
                max_length=255
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='scope_review_notes',
            field=models.TextField(
                blank=True,
                help_text='Admin notes from scope review'
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='admin_notes',
            field=models.TextField(
                blank=True,
                help_text='General admin notes'
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='reviewed_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Admin who reviewed the scope',
                limit_choices_to={'role__in': ['admin', 'superadmin', 'support']},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reviewed_express_classes',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='expressclass',
            name='reviewed_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the scope was reviewed',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='number_of_discussion_posts',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of discussion posts required'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='number_of_discussion_posts_replies',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of discussion post replies required'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='number_of_assignments',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of assignments required'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='number_of_exams',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of exams required'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='number_of_quizzes',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of quizzes required'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='number_of_projects',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of projects required'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='number_of_presentations',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of presentations required'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='number_of_papers',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of papers required'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='total_workload_in_pages',
            field=models.CharField(
                blank=True,
                help_text="Workload e.g., 'number of pages total'",
                max_length=100
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='installments_needed',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Number of installments needed (0 = full payment)'
            ),
        ),
        migrations.AlterField(
            model_name='expressclass',
            name='instructions',
            field=models.TextField(
                blank=True,
                help_text='Special instructions for the express class'
            ),
        ),
    ]

