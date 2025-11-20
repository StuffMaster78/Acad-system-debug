"""
Initialize default fine types in the database.
Run this after migrations to create common fine types.
"""

from django.db import transaction
from fines.models.fine_type_config import FineTypeConfig
from websites.models import Website


@transaction.atomic
def initialize_default_fine_types(website=None):
    """
    Create default fine type configurations.
    
    Args:
        website: Website instance (None = create global types)
        
    Returns:
        List[FineTypeConfig]: Created fine type configs
    """
    default_types = [
        {
            'code': 'late_submission',
            'name': 'Late Submission',
            'description': 'Automatic fine for submitting order after deadline',
            'is_system_defined': 'system',
            'calculation_type': 'progressive_hourly',
            # No base_amount for progressive_hourly - uses order's writer_compensation at calculation time
        },
        {
            'code': 'quality_issue',
            'name': 'Quality Issue',
            'description': 'Fine for poor quality work, grammatical errors, or failing to meet quality standards',
            'calculation_type': 'percentage',
            'percentage': 10.00,
            # base_amount=None - will use writer_compensation from order at calculation time
            'min_amount': 5.00,
            'max_amount': 50.00,
        },
        {
            'code': 'privacy_violation',
            'name': 'Privacy Violation',
            'description': 'Fine for violating client privacy or sharing confidential information',
            'calculation_type': 'fixed',
            'fixed_amount': 50.00,
        },
        {
            'code': 'excessive_revisions',
            'name': 'Excessive Revisions',
            'description': 'Fine for requiring excessive revisions due to writer error',
            'calculation_type': 'percentage',
            'percentage': 5.00,
            # base_amount=None - will use writer_compensation from order at calculation time
        },
        {
            'code': 'late_reassignment',
            'name': 'Late Reassignment Request',
            'description': 'Fine for requesting order reassignment late in the process',
            'calculation_type': 'percentage',
            'percentage': 15.00,
            # base_amount=None - will use writer_compensation from order at calculation time
        },
        {
            'code': 'dropping_order_late',
            'name': 'Dropping Order Late',
            'description': 'Fine for dropping an order after significant work has been done',
            'calculation_type': 'percentage',
            'percentage': 20.00,
            # base_amount=None - will use writer_compensation from order at calculation time
            'min_amount': 10.00,
        },
        {
            'code': 'wrong_files',
            'name': 'Uploaded Wrong Files',
            'description': 'Fine for uploading incorrect files or wrong versions',
            'calculation_type': 'fixed',
            'fixed_amount': 10.00,
        },
        {
            'code': 'plagiarism',
            'name': 'Plagiarism',
            'description': 'Fine for submitting plagiarized content',
            'calculation_type': 'fixed',
            'fixed_amount': 100.00,
        },
        {
            'code': 'inactivity',
            'name': 'Inactivity/Abandonment',
            'description': 'Fine for abandoning order or prolonged inactivity',
            'calculation_type': 'percentage',
            'percentage': 25.00,
            # base_amount=None - will use writer_compensation from order at calculation time
        },
        {
            'code': 'comm_breach',
            'name': 'Communication Breach',
            'description': 'Fine for failing to communicate or respond to client/admin messages',
            'calculation_type': 'fixed',
            'fixed_amount': 15.00,
        },
    ]
    
    created = []
    
    for type_data in default_types:
        # Check if already exists
        existing = FineTypeConfig.objects.filter(
            code=type_data['code'],
            website=website
        ).first()
        
        if not existing:
            # Prepare create data, excluding base_amount entirely (will be None by default)
            create_data = {}
            for k, v in type_data.items():
                # Skip base_amount field entirely - it should be None for percentage types
                if k != 'base_amount':
                    create_data[k] = v
            
            config = FineTypeConfig.objects.create(
                website=website,
                active=True,
                **create_data
            )
            created.append(config)
    
    return created

