# Generated migration to add universal file categories

from django.db import migrations


def create_universal_categories(apps, schema_editor):
    """
    Create universal file categories that will be available to all websites.
    """
    OrderFileCategory = apps.get_model('order_files', 'OrderFileCategory')
    Website = apps.get_model('websites', 'Website')
    
    # Universal categories (website=None means available to all websites)
    universal_categories = [
        # Writer categories
        {
            'name': 'Final Draft',
            'allowed_extensions': ['pdf', 'docx', 'doc'],
            'is_final_draft': True,
            'is_extra_service': False,
        },
        {
            'name': 'First Draft',
            'allowed_extensions': ['pdf', 'docx', 'doc'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'DRAFT',
            'allowed_extensions': ['pdf', 'docx', 'doc'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Outline',
            'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Resource',
            'allowed_extensions': ['pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Plagiarism Report',
            'allowed_extensions': ['pdf'],
            'is_final_draft': False,
            'is_extra_service': True,
        },
        {
            'name': 'AI Similarity Report',
            'allowed_extensions': ['pdf'],
            'is_final_draft': False,
            'is_extra_service': True,
        },
        # Client categories
        {
            'name': 'Materials',
            'allowed_extensions': ['pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png', 'zip', 'rar'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Sample',
            'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'My Previous Papers',
            'allowed_extensions': ['pdf', 'docx', 'doc'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Friends Paper',
            'allowed_extensions': ['pdf', 'docx', 'doc'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Reading Materials',
            'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Syllabus',
            'allowed_extensions': ['pdf', 'docx', 'doc'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Rubric',
            'allowed_extensions': ['pdf', 'docx', 'doc'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Guidelines',
            'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
        {
            'name': 'Order Instructions',
            'allowed_extensions': ['pdf', 'docx', 'doc', 'txt'],
            'is_final_draft': False,
            'is_extra_service': False,
        },
    ]
    
    # Create universal categories (website=None)
    for category_data in universal_categories:
        # Check if category already exists (by name, regardless of website)
        existing = OrderFileCategory.objects.filter(name=category_data['name']).first()
        if not existing:
            OrderFileCategory.objects.create(
                website=None,  # Universal category
                **category_data
            )


def reverse_universal_categories(apps, schema_editor):
    """
    Remove universal categories (website=None) that were created by this migration.
    """
    OrderFileCategory = apps.get_model('order_files', 'OrderFileCategory')
    
    # List of category names to remove
    category_names = [
        'Final Draft', 'First Draft', 'DRAFT', 'Outline', 'Resource',
        'Plagiarism Report', 'AI Similarity Report',
        'Materials', 'Sample', 'My Previous Papers', 'Friends Paper',
        'Reading Materials', 'Syllabus', 'Rubric', 'Guidelines', 'Order Instructions'
    ]
    
    # Remove universal categories with these names
    OrderFileCategory.objects.filter(website__isnull=True, name__in=category_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('order_files', '0007_make_category_website_nullable'),
    ]

    operations = [
        migrations.RunPython(create_universal_categories, reverse_universal_categories),
    ]

