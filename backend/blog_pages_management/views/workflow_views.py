"""
Views for approval workflow management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from ..models.workflow_models import (
    BlogPostWorkflow, BlogPostReviewComment, WorkflowTransition, ContentTemplate, ContentSnippet
)
from ..models import BlogPost
from ..services.workflow_service import WorkflowService
from ..serializers.workflow_serializers import (
    BlogPostWorkflowSerializer, BlogPostReviewCommentSerializer,
    WorkflowTransitionSerializer, ContentTemplateSerializer, ContentSnippetSerializer
)


class BlogPostWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog post workflows."""
    queryset = BlogPostWorkflow.objects.all()
    serializer_class = BlogPostWorkflowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'assigned_reviewer', 'blog__website']
    
    def get_queryset(self):
        """Filter based on user permissions."""
        queryset = super().get_queryset().select_related(
            'blog', 'submitted_by', 'assigned_reviewer', 'approved_by'
        )
        
        # Admins see all, others see their own
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                blog__authors=self.request.user
            ) | queryset.filter(
                assigned_reviewer=self.request.user
            )
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit a blog post for review."""
        blog_id = request.data.get('blog_id')
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            workflow = WorkflowService.submit_for_review(blog, request.user)
            serializer = self.get_serializer(workflow)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def assign_reviewer(self, request, pk=None):
        """Assign a reviewer to a workflow."""
        workflow = self.get_object()
        reviewer_id = request.data.get('reviewer_id')
        
        try:
            from authentication.models import User
            reviewer = User.objects.get(id=reviewer_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Reviewer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            workflow = WorkflowService.assign_reviewer(workflow, reviewer, request.user)
            serializer = self.get_serializer(workflow)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a blog post."""
        workflow = self.get_object()
        publish = request.data.get('publish', False)
        
        try:
            workflow = WorkflowService.approve(workflow, request.user, publish=publish)
            serializer = self.get_serializer(workflow)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a blog post."""
        workflow = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            workflow = WorkflowService.reject(workflow, request.user, reason)
            serializer = self.get_serializer(workflow)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def pending_reviews(self, request):
        """Get pending reviews for the current user or all if admin."""
        if request.user.is_staff:
            workflows = WorkflowService.get_pending_reviews(website=request.query_params.get('website_id'))
        else:
            workflows = WorkflowService.get_pending_reviews(user=request.user)
        
        serializer = self.get_serializer(workflows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BlogPostReviewCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing review comments."""
    queryset = BlogPostReviewComment.objects.all()
    serializer_class = BlogPostReviewCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['workflow', 'is_resolved', 'commenter']
    
    def get_queryset(self):
        return super().get_queryset().select_related('workflow', 'commenter', 'resolved_by')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a comment as resolved."""
        comment = self.get_object()
        comment = WorkflowService.resolve_comment(comment, request.user)
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkflowTransitionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing workflow transitions."""
    queryset = WorkflowTransition.objects.all()
    serializer_class = WorkflowTransitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['workflow', 'from_status', 'to_status']


class ContentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing content templates."""
    queryset = ContentTemplate.objects.all()
    serializer_class = ContentTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website', 'template_type', 'is_active']
    
    def get_queryset(self):
        return super().get_queryset().filter(
            website__id=self.request.query_params.get('website_id')
        )
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply template to a blog post."""
        template = self.get_object()
        blog_id = request.data.get('blog_id')
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from ..services.template_service import TemplateService
        template_variables = request.data.get('variables', {})
        
        blog = TemplateService.create_from_template(blog, template, template_variables)
        blog.save()
        
        from ..serializers import BlogPostSerializer
        serializer = BlogPostSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def instantiate(self, request, pk=None):
        """
        Instantiate a new draft blog post or service page from this template.

        Body:
        {
            "target": "blog_post" | "service_page",
            "website_id": ...,
            "variables": { ...optional substitutions... }
        }
        """
        template = self.get_object()
        target = request.data.get('target')
        website_id = request.data.get('website_id')
        template_variables = request.data.get('variables', {})

        if target not in ['blog_post', 'service_page']:
            return Response(
                {'error': 'target must be "blog_post" or "service_page".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not website_id:
            return Response(
                {'error': 'website_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from websites.models import Website
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        from ..services.template_service import TemplateService

        if target == 'blog_post':
            if template.template_type != 'blog_post':
                return Response(
                    {'error': 'Template is not a blog_post template.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Create new draft blog post
            blog = BlogPost.objects.create(
                website=website,
                status='draft',
                is_published=False,
            )
            blog = TemplateService.create_from_template(blog, template, template_variables)
            blog.save()
            from ..serializers import BlogPostSerializer
            serializer = BlogPostSerializer(blog)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Service page target
        if template.template_type != 'service_page':
            return Response(
                {'error': 'Template is not a service_page template.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from service_pages_management.models import ServicePage

        page = ServicePage.objects.create(
            website=website,
            is_published=False,
            created_by=request.user,
            updated_by=request.user,
            title='',
            header='',
            content='',
        )
        page = TemplateService.create_service_page_from_template(
            page, template, template_variables
        )
        page.save()

        from service_pages_management.serializers import ServicePageSerializer
        serializer = ServicePageSerializer(page)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContentSnippetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing content snippets."""
    queryset = ContentSnippet.objects.all()
    serializer_class = ContentSnippetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website', 'snippet_type', 'is_active']
    
    def get_queryset(self):
        return super().get_queryset().filter(
            website__id=self.request.query_params.get('website_id')
        )

    @action(detail=True, methods=['post'])
    def render(self, request, pk=None):
        """
        Render a snippet for insertion into an editor.

        Body:
        {
            "format": "html" | "markdown"  # currently returns raw snippet.content
        }
        """
        snippet = self.get_object()
        format_type = request.data.get('format', 'html')

        # For now, we simply return the raw content; frontends can decide
        # how to insert it into their editors.
        return Response(
            {
                'id': snippet.id,
                'name': snippet.name,
                'snippet_type': snippet.snippet_type,
                'content': snippet.content,
                'format': format_type,
            },
            status=status.HTTP_200_OK,
        )

