import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms_blog', '0001_initial'),
        ('cms_content_graph', '0001_initial'),
        ('cms_service_pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpostpage',
            name='pillar',
            field=models.ForeignKey(
                blank=True,
                help_text='Which content pillar / funnel this post feeds',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='spoke_posts',
                to='cms_content_graph.contentpillar',
            ),
        ),
        migrations.AddField(
            model_name='blogpostpage',
            name='primary_service',
            field=models.ForeignKey(
                blank=True,
                help_text='The service page this blog post primarily routes readers toward',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='blog_post_sources',
                to='cms_service_pages.servicepage',
            ),
        ),
    ]
