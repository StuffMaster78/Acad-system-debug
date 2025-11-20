# Generated migration for WriterLevel enhancements

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0001_initial'),
        ('websites', '0001_initial'),
    ]

    operations = [
        # Change related_name for website
        migrations.AlterField(
            model_name='writerlevel',
            name='website',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='writer_levels',
                to='websites.website'
            ),
        ),
        
        # Add new fields
        migrations.AddField(
            model_name='writerlevel',
            name='description',
            field=models.TextField(blank=True, help_text='Description of this level and its benefits.'),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='earning_mode',
            field=models.CharField(
                choices=[
                    ('fixed_per_page', 'Fixed Per Page/Slide'),
                    ('percentage_of_order_cost', 'Percentage of Order Cost'),
                    ('percentage_of_order_total', 'Percentage of Order Total'),
                ],
                default='fixed_per_page',
                help_text='How writer earnings are calculated',
                max_length=30
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='earnings_percentage_of_cost',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                help_text='Percentage of order cost (before discounts) writer earns',
                max_digits=5
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='earnings_percentage_of_total',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                help_text='Percentage of order total (after discounts) writer earns',
                max_digits=5
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='urgency_additional_per_page',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                help_text='Additional amount per page for urgent orders (beyond percentage increase)',
                max_digits=10
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='urgent_order_deadline_hours',
            field=models.PositiveIntegerField(
                default=8,
                help_text='Hours before deadline that order is considered urgent for this level'
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='deadline_percentage',
            field=models.DecimalField(
                decimal_places=2,
                default=80.00,
                help_text='Percentage of client deadline writer receives (e.g., 80% means writer gets 80% of client deadline time)',
                max_digits=5
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='tips_percentage',
            field=models.DecimalField(
                decimal_places=2,
                default=100.00,
                help_text='Percentage of tips writer receives (alias for tip_percentage)',
                max_digits=5
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='min_orders_to_attain',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Minimum number of completed orders required to reach this level'
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='min_rating_to_attain',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                help_text='Minimum average rating required to reach this level',
                max_digits=3
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='min_takes_to_attain',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Minimum number of successful order takes required to reach this level'
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='min_completion_rate',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                help_text='Minimum order completion rate (%) required',
                max_digits=5
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='max_revision_rate',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Maximum acceptable revision rate (%) for this level',
                max_digits=5,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='max_lateness_rate',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Maximum acceptable lateness rate (%) for this level',
                max_digits=5,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='bonus_per_order_completed',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                help_text='Fixed bonus per completed order',
                max_digits=10
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='bonus_per_rating_above_threshold',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                help_text='Bonus for orders rated above threshold (e.g., 4.5+)',
                max_digits=10
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='rating_threshold_for_bonus',
            field=models.DecimalField(
                decimal_places=2,
                default=4.50,
                help_text='Rating threshold to qualify for bonus',
                max_digits=3
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='display_order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Display order (lower = higher level, used for sorting)'
            ),
        ),
        migrations.AddField(
            model_name='writerlevel',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Whether this level is active and can be assigned'
            ),
        ),
        
        # Remove unique constraint on name, add unique_together for website+name
        migrations.AlterField(
            model_name='writerlevel',
            name='name',
            field=models.CharField(
                help_text='Name of the writer level (e.g., Novice, Intermediate, Expert).',
                max_length=50
            ),
        ),
        migrations.AlterUniqueTogether(
            name='writerlevel',
            unique_together={('website', 'name')},
        ),
        
        # Update ordering
        migrations.AlterModelOptions(
            name='writerlevel',
            options={
                'ordering': ['display_order', 'name'],
                'verbose_name': 'Writer Level',
                'verbose_name_plural': 'Writer Levels',
            },
        ),
    ]

