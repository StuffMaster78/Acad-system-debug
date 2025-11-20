"""
Views for draft, revision, preview, and edit lock management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from ..models.draft_editing import (
    BlogPostRevision, BlogPostAutoSave, BlogPostEditLock, BlogPostPreview
)
from ..models import BlogPost
from ..services.draft_editing_service import DraftEditingService
from ..serializers.draft_serializers import (
    BlogPostRevisionSerializer, BlogPostAutoSaveSerializer,
    BlogPostEditLockSerializer, BlogPostPreviewSerializer
)


class BlogPostRevisionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing and managing blog post revisions."""
    queryset = BlogPostRevision.objects.all()
    serializer_class = BlogPostRevisionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog', 'created_by', 'is_current']
    
    def get_queryset(self):
        """Optimize queryset."""
        return super().get_queryset().select_related('blog', 'created_by')
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a blog post to this revision."""
        revision = self.get_object()
        blog = revision.blog
        
        try:
            restored_blog = DraftEditingService.restore_revision(blog, revision, request.user)
            from ..serializers import BlogPostSerializer
            serializer = BlogPostSerializer(restored_blog)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f"Failed to restore revision: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def diff(self, request, pk=None):
        """Get diff between this revision and another (or current)."""
        revision = self.get_object()
        compare_to_id = request.query_params.get('compare_to')
        
        if compare_to_id:
            try:
                compare_to = BlogPostRevision.objects.get(id=compare_to_id)
            except BlogPostRevision.DoesNotExist:
                return Response(
                    {'error': 'Revision not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Compare to current blog post
            from ..models.draft_editing import BlogPostRevision
            current_revision = BlogPostRevision.objects.filter(
                blog=revision.blog,
                is_current=True
            ).first()
            if not current_revision:
                return Response({'error': 'No current revision found'}, status=status.HTTP_404_NOT_FOUND)
            compare_to = current_revision
        
        diffs = DraftEditingService.get_diff(revision, compare_to)
        return Response({
            'from_revision': revision.revision_number,
            'to_revision': compare_to.revision_number,
            'diffs': diffs
        }, status=status.HTTP_200_OK)


class BlogPostAutoSaveViewSet(viewsets.ModelViewSet):
    """ViewSet for managing auto-saved drafts."""
    queryset = BlogPostAutoSave.objects.all()
    serializer_class = BlogPostAutoSaveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog', 'saved_by', 'is_recovered']
    
    def get_queryset(self):
        """Filter to user's autosaves."""
        queryset = super().get_queryset().select_related('blog', 'saved_by')
        # Only show autosaves for blogs user can access
        return queryset.filter(saved_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def save_draft(self, request):
        """Auto-save a draft."""
        blog_id = request.data.get('blog_id')
        
        if not blog_id:
            return Response(
                {'error': 'blog_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        autosave = DraftEditingService.auto_save_draft(
            blog=blog,
            user=request.user,
            data=request.data
        )
        
        serializer = self.get_serializer(autosave)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest autosave for a blog."""
        blog_id = request.query_params.get('blog_id')
        
        if not blog_id:
            return Response(
                {'error': 'blog_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        autosave = DraftEditingService.get_latest_autosave(blog, request.user)
        
        if not autosave:
            return Response(
                {'message': 'No autosave found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(autosave)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def recover(self, request, pk=None):
        """Recover an autosaved draft."""
        autosave = self.get_object()
        blog = autosave.blog
        
        # Verify user owns the autosave
        if autosave.saved_by != request.user:
            return Response(
                {'error': 'You do not have permission to recover this autosave'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            recovered_blog = DraftEditingService.recover_autosave(blog, autosave)
            from ..serializers import BlogPostSerializer
            serializer = BlogPostSerializer(recovered_blog)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f"Failed to recover autosave: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class BlogPostEditLockViewSet(viewsets.ModelViewSet):
    """ViewSet for managing edit locks."""
    queryset = BlogPostEditLock.objects.all()
    serializer_class = BlogPostEditLockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show active locks."""
        return super().get_queryset().filter(is_active=True).select_related('blog', 'locked_by')
    
    @action(detail=False, methods=['post'])
    def acquire(self, request):
        """Acquire an edit lock for a blog post."""
        blog_id = request.data.get('blog_id')
        duration = int(request.data.get('duration_minutes', 30))
        
        if not blog_id:
            return Response(
                {'error': 'blog_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        lock, acquired = DraftEditingService.acquire_edit_lock(blog, request.user, duration)
        
        if not acquired:
            serializer = self.get_serializer(lock)
            return Response({
                'acquired': False,
                'message': f'Blog is currently locked by {lock.locked_by.username}',
                'lock': serializer.data
            }, status=status.HTTP_409_CONFLICT)
        
        serializer = self.get_serializer(lock)
        return Response({
            'acquired': True,
            'lock': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        """Extend an edit lock."""
        lock = self.get_object()
        
        if lock.locked_by != request.user:
            return Response(
                {'error': 'You do not own this lock'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        duration = int(request.data.get('duration_minutes', 30))
        lock.extend_lock(duration)
        
        serializer = self.get_serializer(lock)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """Release an edit lock."""
        lock = self.get_object()
        
        if lock.locked_by != request.user:
            return Response(
                {'error': 'You do not own this lock'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        lock.release_lock()
        return Response({'message': 'Lock released'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """Check if a blog post is locked."""
        blog_id = request.query_params.get('blog_id')
        
        if not blog_id:
            return Response(
                {'error': 'blog_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        lock = BlogPostEditLock.objects.filter(
            blog=blog,
            is_active=True
        ).first()
        
        if lock and not lock.is_expired():
            serializer = self.get_serializer(lock)
            return Response({
                'is_locked': True,
                'lock': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Clean up expired lock
            if lock:
                lock.release_lock()
            return Response({
                'is_locked': False
            }, status=status.HTTP_200_OK)


class BlogPostPreviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing preview tokens."""
    queryset = BlogPostPreview.objects.all()
    serializer_class = BlogPostPreviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter to user's previews."""
        return super().get_queryset().filter(
            created_by=self.request.user
        ).select_related('blog', 'created_by')
    
    @action(detail=False, methods=['post'])
    def create_token(self, request):
        """Create a preview token for a blog post."""
        blog_id = request.data.get('blog_id')
        expires_hours = int(request.data.get('expires_hours', 24))
        
        if not blog_id:
            return Response(
                {'error': 'blog_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        preview = DraftEditingService.create_preview_token(blog, request.user, expires_hours)
        serializer = self.get_serializer(preview, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a preview token."""
        preview = self.get_object()
        
        if preview.created_by != request.user:
            return Response(
                {'error': 'You do not own this preview'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        preview.is_active = False
        preview.save(update_fields=['is_active'])
        
        return Response({'message': 'Preview deactivated'}, status=status.HTTP_200_OK)

