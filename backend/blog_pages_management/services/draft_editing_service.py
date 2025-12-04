"""
Service for managing drafts, auto-save, revisions, previews, and edit locks.
"""
import secrets
from typing import Optional, Dict, Tuple
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from difflib import unified_diff

try:
    from ..models import BlogPost
    from ..models.draft_editing import (
        BlogPostRevision, BlogPostAutoSave, BlogPostEditLock, BlogPostPreview
    )
except ImportError:
    from blog_pages_management.models import BlogPost
    from blog_pages_management.models.draft_editing import (
        BlogPostRevision, BlogPostAutoSave, BlogPostEditLock, BlogPostPreview
    )


class DraftEditingService:
    """Service for managing draft editing workflows."""
    
    @staticmethod
    @transaction.atomic
    def create_revision(blog: BlogPost, user, change_summary: str = "") -> BlogPostRevision:
        """
        Create a revision snapshot of the current blog post state.
        
        Args:
            blog: BlogPost instance
            user: User creating the revision
            change_summary: Optional summary of changes
        
        Returns:
            BlogPostRevision instance
        """
        # Get next revision number
        last_revision = BlogPostRevision.objects.filter(blog=blog).order_by('-revision_number').first()
        revision_number = (last_revision.revision_number + 1) if last_revision else 1
        
        # Mark previous revisions as not current
        BlogPostRevision.objects.filter(blog=blog, is_current=True).update(is_current=False)
        
        # Get authors and tags data
        authors_data = []
        tags_data = []
        try:
            authors_data = list(blog.authors.values_list('id', flat=True))
            tags_data = list(blog.tags.values_list('id', flat=True))
        except Exception:
            # If blog not fully loaded, try to get from database
            pass
        
        # Create new revision
        revision = BlogPostRevision.objects.create(
            blog=blog,
            revision_number=revision_number,
            title=blog.title,
            content=str(blog.content) if blog.content else '',  # Ensure string
            meta_title=blog.meta_title or '',
            meta_description=blog.meta_description or '',
            authors_data=authors_data,
            tags_data=tags_data,
            category_id=blog.category_id,
            created_by=user,
            change_summary=change_summary,
            is_current=True
        )
        
        return revision
    
    @staticmethod
    @transaction.atomic
    def restore_revision(blog: BlogPost, revision: BlogPostRevision, user) -> BlogPost:
        """
        Restore a blog post to a previous revision.
        
        Args:
            blog: BlogPost instance
            revision: BlogPostRevision to restore
            user: User performing the restore
        
        Returns:
            Updated BlogPost instance
        """
        # Create a revision of current state before restoring
        DraftEditingService.create_revision(blog, user, f"Restored to revision {revision.revision_number}")
        
        # Restore fields
        blog.title = revision.title
        blog.content = revision.content
        blog.meta_title = revision.meta_title
        blog.meta_description = revision.meta_description
        
        # Restore relationships
        if revision.category_id:
            from ..models import BlogCategory
            try:
                blog.category = BlogCategory.objects.get(id=revision.category_id)
            except BlogCategory.DoesNotExist:
                blog.category = None
        
        blog.save()
        
        # Restore authors and tags
        if revision.authors_data:
            try:
                from ..models import AuthorProfile
                blog.authors.set(AuthorProfile.objects.filter(id__in=revision.authors_data))
            except Exception:
                pass
        if revision.tags_data:
            try:
                from ..models import BlogTag
                blog.tags.set(BlogTag.objects.filter(id__in=revision.tags_data))
            except Exception:
                pass
        
        # Create new revision for the restored state
        try:
            DraftEditingService.create_revision(blog, user, f"Restored from revision {revision.revision_number}")
        except Exception:
            # If revision creation fails, continue anyway
            pass
        
        return blog
    
    @staticmethod
    def get_diff(revision1: BlogPostRevision, revision2: BlogPostRevision) -> Dict[str, str]:
        """
        Get a diff between two revisions.
        
        Returns:
            Dict with diff strings for different fields
        """
        diffs = {}
        
        # Content diff
        if revision1.content != revision2.content:
            content_diff = list(unified_diff(
                revision1.content.splitlines(keepends=True),
                revision2.content.splitlines(keepends=True),
                fromfile=f"Revision {revision1.revision_number}",
                tofile=f"Revision {revision2.revision_number}",
                lineterm=''
            ))
            diffs['content'] = ''.join(content_diff)
        
        # Title diff
        if revision1.title != revision2.title:
            diffs['title'] = f"- {revision1.title}\n+ {revision2.title}"
        
        # Meta description diff
        if revision1.meta_description != revision2.meta_description:
            diffs['meta_description'] = f"- {revision1.meta_description}\n+ {revision2.meta_description}"
        
        return diffs
    
    @staticmethod
    @transaction.atomic
    def auto_save_draft(blog: BlogPost, user, data: Dict, run_health_check: bool = False) -> BlogPostAutoSave:
        """
        Auto-save a draft of a blog post.
        
        Args:
            blog: BlogPost instance (can be new/unsaved)
            user: User saving the draft
            data: Dict with draft data (title, content, etc.)
            run_health_check: Whether to run content health check during auto-save
        
        Returns:
            BlogPostAutoSave instance with optional health_check_results
        """
        # If blog is new, save it first
        if not blog.pk:
            blog.save()
        
        # Get authors and tags data
        authors_data = data.get('authors', [])
        tags_data = data.get('tags', [])
        if not authors_data:
            try:
                authors_data = list(blog.authors.values_list('id', flat=True))
            except Exception:
                authors_data = []
        if not tags_data:
            try:
                tags_data = list(blog.tags.values_list('id', flat=True))
            except Exception:
                tags_data = []
        
        # Run health check if requested
        health_check_results = None
        if run_health_check:
            from ..services.content_health_service import ContentHealthService
            health_check_results = ContentHealthService.check_full_content(
                title=data.get('title', blog.title or ''),
                meta_title=data.get('meta_title', blog.meta_title or ''),
                meta_description=data.get('meta_description', blog.meta_description or ''),
                content=data.get('content', blog.content or ''),
                slug=data.get('slug', blog.slug or ''),
                min_words=300
            )
        
        autosave = BlogPostAutoSave.objects.create(
            blog=blog,
            title=data.get('title', blog.title or ''),
            content=str(data.get('content', blog.content or '')),  # Ensure string
            meta_title=data.get('meta_title', blog.meta_title or ''),
            meta_description=data.get('meta_description', blog.meta_description or ''),
            authors_data=authors_data,
            tags_data=tags_data,
            category_id=data.get('category', blog.category_id),
            saved_by=user
        )
        
        # Store health check results in autosave metadata if available
        if health_check_results and hasattr(autosave, 'metadata'):
            autosave.metadata = {'health_check': health_check_results}
            autosave.save()
        
        return autosave
    
    @staticmethod
    def get_latest_autosave(blog: BlogPost, user) -> Optional[BlogPostAutoSave]:
        """Get the most recent autosave for a blog post."""
        return BlogPostAutoSave.objects.filter(
            blog=blog,
            saved_by=user,
            is_recovered=False
        ).order_by('-saved_at').first()
    
    @staticmethod
    @transaction.atomic
    def recover_autosave(blog: BlogPost, autosave: BlogPostAutoSave) -> BlogPost:
        """
        Recover an autosaved draft and apply it to the blog post.
        
        Args:
            blog: BlogPost instance
            autosave: BlogPostAutoSave to recover
        
        Returns:
            Updated BlogPost instance
        """
        blog.title = autosave.title
        blog.content = autosave.content
        blog.meta_title = autosave.meta_title
        blog.meta_description = autosave.meta_description
        
        if autosave.category_id:
            from ..models import BlogCategory
            try:
                blog.category = BlogCategory.objects.get(id=autosave.category_id)
            except BlogCategory.DoesNotExist:
                blog.category = None
        
        blog.save()
        
        if autosave.authors_data:
            blog.authors.set(autosave.authors_data)
        if autosave.tags_data:
            blog.tags.set(autosave.tags_data)
        
        # Mark autosave as recovered
        autosave.is_recovered = True
        autosave.save(update_fields=['is_recovered'])
        
        return blog
    
    @staticmethod
    @transaction.atomic
    def acquire_edit_lock(blog: BlogPost, user, duration_minutes: int = 30) -> Tuple[BlogPostEditLock, bool]:
        """
        Acquire an edit lock for a blog post.
        
        Args:
            blog: BlogPost instance
            user: User requesting the lock
            duration_minutes: Lock duration in minutes
        
        Returns:
            Tuple of (lock, acquired) where acquired is True if lock was acquired
        """
        # Clean up expired locks
        BlogPostEditLock.objects.filter(
            blog=blog,
            is_active=True,
            expires_at__lt=timezone.now()
        ).update(is_active=False)
        
        # Check for existing active lock
        existing_lock = BlogPostEditLock.objects.filter(
            blog=blog,
            is_active=True
        ).first()
        
        if existing_lock:
            if existing_lock.locked_by == user:
                # User already has the lock, extend it
                existing_lock.extend_lock(duration_minutes)
                return existing_lock, True
            else:
                # Someone else has the lock
                return existing_lock, False
        
        # Create new lock
        lock = BlogPostEditLock.objects.create(
            blog=blog,
            locked_by=user,
            expires_at=timezone.now() + timedelta(minutes=duration_minutes)
        )
        
        return lock, True
    
    @staticmethod
    def release_edit_lock(blog: BlogPost, user):
        """Release an edit lock if the user owns it."""
        lock = BlogPostEditLock.objects.filter(
            blog=blog,
            locked_by=user,
            is_active=True
        ).first()
        
        if lock:
            lock.release_lock()
    
    @staticmethod
    @transaction.atomic
    def create_preview_token(blog: BlogPost, user, expires_hours: int = 24) -> BlogPostPreview:
        """
        Create a preview token for a blog post.
        
        Args:
            blog: BlogPost instance
            user: User creating the preview
            expires_hours: Hours until token expires
        
        Returns:
            BlogPostPreview instance
        """
        # Deactivate old previews
        BlogPostPreview.objects.filter(blog=blog, is_active=True).update(is_active=False)
        
        # Generate unique token
        token = secrets.token_urlsafe(48)
        while BlogPostPreview.objects.filter(token=token).exists():
            token = secrets.token_urlsafe(48)
        
        preview = BlogPostPreview.objects.create(
            blog=blog,
            token=token,
            created_by=user,
            expires_at=timezone.now() + timedelta(hours=expires_hours)
        )
        
        return preview
    
    @staticmethod
    def get_preview_by_token(token: str) -> Optional[BlogPostPreview]:
        """Get a valid preview by token."""
        try:
            preview = BlogPostPreview.objects.get(token=token, is_active=True)
            if preview.is_valid():
                preview.increment_view()
                return preview
        except BlogPostPreview.DoesNotExist:
            pass
        return None
    
    @staticmethod
    def cleanup_expired_locks():
        """Clean up expired edit locks (call via Celery task)."""
        expired_count = BlogPostEditLock.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        ).update(is_active=False)
        return expired_count
    
    @staticmethod
    def cleanup_old_autosaves(days: int = 7):
        """Clean up old autosaves (call via Celery task)."""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = BlogPostAutoSave.objects.filter(
            saved_at__lt=cutoff_date,
            is_recovered=True
        ).delete()
        return deleted_count

