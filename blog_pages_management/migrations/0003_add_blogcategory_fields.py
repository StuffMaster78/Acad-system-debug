# Generated migration for adding missing fields to BlogCategory model
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog_pages_management', '0002_initial'),
    ]

    operations = [
        # Add SEO fields
        migrations.AddField(
            model_name='blogcategory',
            name='meta_title',
            field=models.CharField(
                blank=True,
                help_text='SEO title for category page',
                max_length=255
            ),
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='meta_description',
            field=models.TextField(
                blank=True,
                help_text='SEO description for category page'
            ),
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='category_image',
            field=models.ImageField(
                blank=True,
                help_text='Category featured image',
                null=True,
                upload_to='blog_categories/'
            ),
        ),
        # Add analytics fields
        migrations.AddField(
            model_name='blogcategory',
            name='post_count',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Cached count of published posts in this category'
            ),
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='total_views',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Total views across all posts in this category'
            ),
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='total_conversions',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Total conversions from posts in this category'
            ),
        ),
        # Add display fields
        migrations.AddField(
            model_name='blogcategory',
            name='display_order',
            field=models.IntegerField(
                default=0,
                help_text='Order for displaying categories'
            ),
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='is_featured',
            field=models.BooleanField(
                default=False,
                help_text='Featured categories appear first'
            ),
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Active categories are visible'
            ),
        ),
        # Add timestamp fields
        migrations.AddField(
            model_name='blogcategory',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                null=True,
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Update unique_together constraint
        migrations.AlterUniqueTogether(
            name='blogcategory',
            unique_together={('website', 'slug')},
        ),
    ]

