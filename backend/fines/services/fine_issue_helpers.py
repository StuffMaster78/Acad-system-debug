"""
Helper functions for issuing common fine types.
These use FineTypeService to issue fines with predefined codes.
"""

from orders.models import Order
from fines.services.fine_type_service import FineTypeService
from django.core.exceptions import ValidationError


class FineIssueHelpers:
    """
    Convenience methods for issuing common fine types.
    """
    
    @staticmethod
    def issue_quality_fine(order: Order, reason: str, issued_by, custom_amount=None):
        """
        Issue a quality-related fine.
        
        Args:
            order: Order to fine
            reason: Detailed reason
            issued_by: Admin/user issuing fine
            custom_amount: Optional override amount
            
        Returns:
            Fine: Created fine
        """
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='quality_issue',
            reason=reason,
            issued_by=issued_by,
            custom_amount=custom_amount
        )
    
    @staticmethod
    def issue_privacy_violation_fine(order: Order, reason: str, issued_by, custom_amount=None):
        """Issue a privacy violation fine."""
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='privacy_violation',
            reason=reason,
            issued_by=issued_by,
            custom_amount=custom_amount
        )
    
    @staticmethod
    def issue_excessive_revisions_fine(order: Order, reason: str, issued_by, revision_count=None, custom_amount=None):
        """Issue a fine for excessive revisions."""
        reason_with_count = reason
        if revision_count:
            reason_with_count = f"{reason} (Revision count: {revision_count})"
        
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='excessive_revisions',
            reason=reason_with_count,
            issued_by=issued_by,
            custom_amount=custom_amount
        )
    
    @staticmethod
    def issue_late_reassignment_fine(order: Order, reason: str, issued_by, custom_amount=None):
        """Issue a fine for late reassignment request."""
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='late_reassignment',
            reason=reason,
            issued_by=issued_by,
            custom_amount=custom_amount
        )
    
    @staticmethod
    def issue_dropping_order_late_fine(order: Order, reason: str, issued_by, hours_into_order=None, custom_amount=None):
        """Issue a fine for dropping an order late."""
        reason_with_hours = reason
        if hours_into_order:
            reason_with_hours = f"{reason} (Hours into order: {hours_into_order})"
        
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='dropping_order_late',
            reason=reason_with_hours,
            issued_by=issued_by,
            custom_amount=custom_amount
        )
    
    @staticmethod
    def issue_wrong_files_fine(order: Order, reason: str, issued_by, custom_amount=None):
        """Issue a fine for uploading wrong files."""
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='wrong_files',
            reason=reason,
            issued_by=issued_by,
            custom_amount=custom_amount
        )
    
    @staticmethod
    def issue_plagiarism_fine(order: Order, reason: str, issued_by, custom_amount=None):
        """Issue a plagiarism fine."""
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='plagiarism',
            reason=reason,
            issued_by=issued_by,
            custom_amount=custom_amount
        )
    
    @staticmethod
    def issue_inactivity_fine(order: Order, reason: str, issued_by, days_inactive=None, custom_amount=None):
        """Issue an inactivity/abandonment fine."""
        reason_with_days = reason
        if days_inactive:
            reason_with_days = f"{reason} (Days inactive: {days_inactive})"
        
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='inactivity',
            reason=reason_with_days,
            issued_by=issued_by,
            custom_amount=custom_amount
        )
    
    @staticmethod
    def issue_communication_breach_fine(order: Order, reason: str, issued_by, custom_amount=None):
        """Issue a communication breach fine."""
        return FineTypeService.issue_fine(
            order=order,
            fine_type_code='comm_breach',
            reason=reason,
            issued_by=issued_by,
            custom_amount=custom_amount
        )

