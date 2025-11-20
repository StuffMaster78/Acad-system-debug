"""
Service for managing approval workflow for blog posts.
"""
from django.db import transaction
from django.utils import timezone
from typing import Optional, List

try:
    from ..models import BlogPost
    from ..models.workflow_models import (
        BlogPostWorkflow, BlogPostReviewComment, WorkflowTransition
    )
except ImportError:
    from blog_pages_management.models import BlogPost
    from blog_pages_management.models.workflow_models import (
        BlogPostWorkflow, BlogPostReviewComment, WorkflowTransition
    )


class WorkflowService:
    """Service for managing blog post approval workflows."""
    
    @staticmethod
    @transaction.atomic
    def submit_for_review(blog: BlogPost, user) -> BlogPostWorkflow:
        """
        Submit a blog post for review.
        
        Args:
            blog: BlogPost instance
            user: User submitting for review
        
        Returns:
            BlogPostWorkflow instance
        """
        workflow, created = BlogPostWorkflow.objects.get_or_create(blog=blog)
        
        if workflow.status not in ['draft', 'rejected']:
            raise ValueError(f"Cannot submit post in '{workflow.status}' status")
        
        # Update workflow
        workflow.status = 'submitted'
        workflow.submitted_by = user
        workflow.submitted_at = timezone.now()
        workflow.save()
        
        # Update blog status
        blog.status = 'submitted'
        blog.save()
        
        # Log transition
        WorkflowTransition.objects.create(
            workflow=workflow,
            from_status='draft' if created else workflow.status,
            to_status='submitted',
            transitioned_by=user,
            transition_reason="Submitted for review"
        )
        
        return workflow
    
    @staticmethod
    @transaction.atomic
    def assign_reviewer(workflow: BlogPostWorkflow, reviewer, assigned_by) -> BlogPostWorkflow:
        """
        Assign a reviewer to a blog post.
        
        Args:
            workflow: BlogPostWorkflow instance
            reviewer: User to assign as reviewer
            assigned_by: User making the assignment
        
        Returns:
            Updated BlogPostWorkflow instance
        """
        if workflow.status != 'submitted':
            raise ValueError(f"Cannot assign reviewer to post in '{workflow.status}' status")
        
        old_status = workflow.status
        workflow.assigned_reviewer = reviewer
        workflow.status = 'in_review'
        workflow.review_started_at = timezone.now()
        workflow.save()
        
        # Log transition
        WorkflowTransition.objects.create(
            workflow=workflow,
            from_status=old_status,
            to_status='in_review',
            transitioned_by=assigned_by,
            transition_reason=f"Assigned to {reviewer.username} for review"
        )
        
        return workflow
    
    @staticmethod
    @transaction.atomic
    def approve(workflow: BlogPostWorkflow, user, publish: bool = False) -> BlogPostWorkflow:
        """
        Approve a blog post.
        
        Args:
            workflow: BlogPostWorkflow instance
            user: User approving the post
            publish: Whether to immediately publish after approval
        
        Returns:
            Updated BlogPostWorkflow instance
        """
        if workflow.status not in ['submitted', 'in_review']:
            raise ValueError(f"Cannot approve post in '{workflow.status}' status")
        
        old_status = workflow.status
        workflow.status = 'approved'
        workflow.approved_by = user
        workflow.approved_at = timezone.now()
        workflow.save()
        
        # Update blog status
        blog = workflow.blog
        if publish:
            blog.status = 'published'
            blog.is_published = True
            if not blog.publish_date:
                blog.publish_date = timezone.now()
            workflow.status = 'published'
            workflow.published_by = user
            workflow.published_at = timezone.now()
            workflow.save()
        
        blog.save()
        
        # Log transition
        WorkflowTransition.objects.create(
            workflow=workflow,
            from_status=old_status,
            to_status='approved' if not publish else 'published',
            transitioned_by=user,
            transition_reason="Approved" + (" and published" if publish else "")
        )
        
        return workflow
    
    @staticmethod
    @transaction.atomic
    def reject(workflow: BlogPostWorkflow, user, reason: str = "") -> BlogPostWorkflow:
        """
        Reject a blog post.
        
        Args:
            workflow: BlogPostWorkflow instance
            user: User rejecting the post
            reason: Reason for rejection
        
        Returns:
            Updated BlogPostWorkflow instance
        """
        if workflow.status not in ['submitted', 'in_review']:
            raise ValueError(f"Cannot reject post in '{workflow.status}' status")
        
        old_status = workflow.status
        workflow.status = 'rejected'
        workflow.rejected_by = user
        workflow.rejected_at = timezone.now()
        workflow.rejection_reason = reason
        workflow.save()
        
        # Update blog status back to draft
        blog = workflow.blog
        blog.status = 'draft'
        blog.save()
        
        # Log transition
        WorkflowTransition.objects.create(
            workflow=workflow,
            from_status=old_status,
            to_status='rejected',
            transitioned_by=user,
            transition_reason=f"Rejected: {reason}" if reason else "Rejected"
        )
        
        return workflow
    
    @staticmethod
    def add_review_comment(
        workflow: BlogPostWorkflow,
        commenter,
        comment: str,
        highlighted_text: str = "",
        content_metadata: dict = None
    ) -> BlogPostReviewComment:
        """
        Add a review comment.
        
        Args:
            workflow: BlogPostWorkflow instance
            commenter: User adding the comment
            comment: Comment text
            highlighted_text: Optional text being commented on
            content_metadata: Optional metadata about the comment location
        
        Returns:
            BlogPostReviewComment instance
        """
        return BlogPostReviewComment.objects.create(
            workflow=workflow,
            commenter=commenter,
            comment=comment,
            highlighted_text=highlighted_text,
            content_metadata=content_metadata or {}
        )
    
    @staticmethod
    def resolve_comment(comment: BlogPostReviewComment, user) -> BlogPostReviewComment:
        """
        Mark a review comment as resolved.
        
        Args:
            comment: BlogPostReviewComment instance
            user: User resolving the comment
        
        Returns:
            Updated BlogPostReviewComment instance
        """
        comment.is_resolved = True
        comment.resolved_by = user
        comment.resolved_at = timezone.now()
        comment.save()
        return comment
    
    @staticmethod
    def get_pending_reviews(user=None, website=None) -> List[BlogPostWorkflow]:
        """
        Get pending reviews.
        
        Args:
            user: Optional reviewer to filter by
            website: Optional website to filter by
        
        Returns:
            List of BlogPostWorkflow instances
        """
        queryset = BlogPostWorkflow.objects.filter(
            status__in=['submitted', 'in_review']
        )
        
        if user:
            queryset = queryset.filter(assigned_reviewer=user)
        
        if website:
            queryset = queryset.filter(blog__website=website)
        
        return list(queryset.select_related('blog', 'assigned_reviewer', 'submitted_by'))

