from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now, timedelta
from django.db.models import Count
from .models import (
    BlogPost, BlogCategory, BlogTag, AuthorProfile, BlogClick, BlogConversion,
    NewsletterSubscriber, Newsletter, NewsletterAnalytics, BlogActionLog,
    AdminNotification, BlogMediaFile, BlogVideo, BlogDarkModeImage,
    SocialPlatform, BlogShare
)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from .serializers import (
    BlogPostSerializer, BlogCategorySerializer, BlogTagSerializer,
    AuthorProfileSerializer, BlogClickSerializer, BlogConversionSerializer,
    NewsletterSubscriberSerializer, NewsletterSerializer, NewsletterAnalyticsSerializer,
    AdminNotificationSerializer, BlogMediaFileSerializer, BlogPostSerializer,
    BlogVideoSerializer, BlogDarkModeImageSerializer, BlogABTestSerializer,
    BlogClickSerializer, BlogConversionSerializer, SocialPlatformSerializer,
    BlogShareSerializer, BlogShareURLSerializer
)
from websites.models import Website
from django.http import StreamingHttpResponse
from .permissions import IsAdminSuperadminEditor
from rest_framework.decorators import action
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class AdminNotificationsView(generics.ListCreateAPIView):
    """
    API for admins to view and mark notifications as read.
    """
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Returns unread notifications only.
        """
        return AdminNotification.objects.filter(user=self.request.user, is_read=False)

    def patch(self, request, *args, **kwargs):
        """
        Marks selected notifications as read.
        """
        notification_ids = request.data.get("notification_ids", [])
        if not notification_ids:
            return Response({"error": "No notifications selected."}, status=status.HTTP_400_BAD_REQUEST)

        updated_count = AdminNotification.objects.filter(id__in=notification_ids).update(is_read=True)
        return Response({"message": f"{updated_count} notifications marked as read."}, status=status.HTTP_200_OK)

class SoftDeletedBlogsWarningView(generics.ListAPIView):
    """API to list soft-deleted blogs that will be permanently removed soon."""
    serializer_class = BlogPostSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Returns soft-deleted blogs that will be auto-deleted in less than 7 days."""
        warning_threshold = now() - timedelta(days=23)  # 7 days before auto-delete
        return BlogPost.objects.filter(is_deleted=True, deleted_at__lte=warning_threshold)


class ResetBlogEngagementView(APIView):
    """API to allow admins to reset clicks & conversions for blogs."""
    permission_classes = [IsAdminUser]

    def post(self, request, blog_id):
        """Resets engagement stats for a blog post."""
        try:
            blog = BlogPost.objects.get(id=blog_id)
            blog.click_count = 0
            blog.daily_clicks = 0
            blog.weekly_clicks = 0
            blog.monthly_clicks = 0
            blog.semi_annual_clicks = 0
            blog.annual_clicks = 0
            blog.conversion_count = 0
            blog.save(update_fields=[
                "click_count", "daily_clicks", "weekly_clicks", "monthly_clicks",
                "semi_annual_clicks", "annual_clicks", "conversion_count"
            ])
            return Response(
                {"message": f"Engagement stats reset for '{blog.title}'"},
                status=status.HTTP_200_OK
            )
        except BlogPost.DoesNotExist:
            return Response(
                {"error": "Blog not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        

class RestoreSoftDeletedBlogView(APIView):
    """API to restore a soft-deleted blog before permanent deletion."""
    permission_classes = [IsAdminUser]

    def post(self, request, blog_id):
        """Restores a soft-deleted blog and logs the action."""
        try:
            blog = BlogPost.objects.get(id=blog_id, is_deleted=True)
            blog.restore()
            BlogActionLog.objects.create(user=request.user, blog=blog, action="restored")
            return Response(
                {"message": f"Blog '{blog.title}' has been restored."},
                status=status.HTTP_200_OK
            )
        except BlogPost.DoesNotExist:
            return Response(
                {"error": "Blog not found or not soft-deleted."},
                status=status.HTTP_404_NOT_FOUND
            )

class PermanentlyDeleteBlogView(APIView):
    """API to permanently delete a blog and log the action."""
    permission_classes = [IsAdminUser]

    def delete(self, request, blog_id):
        """Permanently deletes a blog and logs the action."""
        try:
            blog = BlogPost.objects.get(id=blog_id, is_deleted=True)
            BlogActionLog.objects.create(user=request.user, blog=blog, action="deleted")
            blog.delete()
            return Response(
                {"message": f"Blog '{blog.title}' has been permanently deleted."},
                status=status.HTTP_200_OK
            )
        except BlogPost.DoesNotExist:
            return Response(
                {"error": "Blog not found or not soft-deleted."},
                status=status.HTTP_404_NOT_FOUND
            )

# ------------------ BLOG CATEGORY VIEWSET ------------------

class BlogCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog categories."""
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [IsAdminUser]


# ------------------ BLOG TAG VIEWSET ------------------

class BlogTagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog tags."""
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    permission_classes = [IsAdminUser]


# ------------------ AUTHOR PROFILE VIEWSET ------------------

class AuthorProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing author profiles."""
    queryset = AuthorProfile.objects.all()
    serializer_class = AuthorProfileSerializer
    permission_classes = [IsAdminUser]


# ------------------ BLOG POST VIEWSET ------------------

class BlogPostViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog posts."""
    queryset = BlogPost.objects.filter(
        is_deleted=False
    ).select_related(
        "category"
    ).prefetch_related(
        "authors", "tags", "media_files"
    ).only(
        "id", "website", "title", "slug", "click_count", "conversion_count",
        "is_published", "created_at", "updated_at"
    ).defer("content")  # Large fields are loaded only when needed
    
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "tags", "authors", "is_published", 'website']
    search_fields = ["title", "meta_title", "meta_description"]
    ordering_fields = ["publish_date", "click_count", "conversion_count"]

    def perform_destroy(self, instance):
        """Soft delete instead of actual delete."""
        instance.soft_delete()

    @action(detail=True, methods=["get"])
    def related_posts(self, request, pk=None):
        """Returns AI-powered related posts based on category and tags."""
        blog = self.get_object()

        related_blogs = BlogPost.objects.filter(
            website=blog.website, is_published=True
        ).exclude(id=blog.id).annotate(
            tag_match_count=Count("tags", filter=models.Q(tags__in=blog.tags.all())),
            category_match=models.Case(
                models.When(category=blog.category, then=1),
                default=0, output_field=models.IntegerField()
            )
        ).order_by("-category_match", "-tag_match_count")[:5]  # Prioritize same category, then tags

        serializer = self.get_serializer(related_blogs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def detect_broken_links(self, request, pk=None):
        """Detects broken internal links."""
        blog = self.get_object()
        soup = BeautifulSoup(blog.content, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("/")]

        # Query all slugs in a single query
        slugs = {link.strip("/").split("/")[-1] for link in links}
        existing_slugs = set(BlogPost.objects.filter(website=blog.website, slug__in=slugs).values_list("slug", flat=True))

        broken_links = [link for link in links if link.strip("/").split("/")[-1] not in existing_slugs]
        return Response({"broken_links": broken_links})


    @action(detail=True, methods=["post"])
    def fix_broken_links(self, request, pk=None):
        """Removes broken links from the blog content."""
        blog = self.get_object()
        soup = BeautifulSoup(blog.content, "html.parser")

        for a in soup.find_all("a", href=True):
            slug = a["href"].strip("/").split("/")[-1]
            if not BlogPost.objects.filter(website=blog.website, slug=slug).exists():
                a.unwrap()  # Remove the broken <a> tag but keep the text

        blog.content = str(soup)
        blog.save()

        return Response({"message": "Broken links removed successfully!"}, status=status.HTTP_200_OK)


# ------------------ BLOG ENGAGEMENT & ANALYTICS (APIView) ------------------

class BlogEngagementStatsView(APIView):
    """API for real-time engagement analytics."""
    permission_classes = [IsAdminUser]

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def get(self, request):
        """Returns trending blogs, most engaged, and click trends."""
        last_week = now() - timedelta(days=7)

        trending_blogs = BlogPost.objects.filter(
            updated_at__gte=last_week
        ).order_by('-click_count')[:5]

        most_engaging_blogs = BlogPost.objects.filter(
            updated_at__gte=last_week
        ).order_by('-conversion_count')[:5]

        return Response({
            "trending_blogs": [
                {"title": blog.title, "clicks": blog.click_count}
                for blog in trending_blogs
            ],
            "most_engaging_blogs": [
                {"title": blog.title, "conversions": blog.conversion_count}
                for blog in most_engaging_blogs
            ]
        })


class BlogClickView(APIView):
    """API for tracking blog post clicks."""
    permission_classes = [IsAuthenticated]

    def post(self, request, blog_id):
        """Increments click count for a blog post."""
        try:
            blog = BlogPost.objects.get(id=blog_id)
            blog.increment_clicks(request.user, request.META.get("REMOTE_ADDR"))
            return Response({"message": "Click recorded"}, status=status.HTTP_200_OK)
        except BlogPost.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)


class BlogConversionView(APIView):
    """API for tracking blog post conversions."""
    permission_classes = [IsAuthenticated]

    def post(self, request, blog_id):
        """Increments conversion count for a blog post."""
        action = request.data.get("action")
        try:
            blog = BlogPost.objects.get(id=blog_id)
            blog.increment_conversions(request.user, action)
            return Response({"message": "Conversion recorded"}, status=status.HTTP_200_OK)
        except BlogPost.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)


# ------------------ NEWSLETTER VIEWSET ------------------

class NewsletterViewSet(viewsets.ModelViewSet):
    """ViewSet for managing newsletters."""
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [IsAdminUser]


class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    """ViewSet for managing newsletter subscribers."""
    queryset = NewsletterSubscriber.objects.all()
    serializer_class = NewsletterSubscriberSerializer
    permission_classes = [IsAuthenticated]


class NewsletterAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for retrieving newsletter analytics."""
    queryset = NewsletterAnalytics.objects.all()
    serializer_class = NewsletterAnalyticsSerializer
    permission_classes = [IsAdminUser]


class BlogMediaFileViewSet(viewsets.ModelViewSet):
    """Manages uploading and listing blog media files (images, videos, PDFs)."""
    queryset = BlogMediaFile.objects.all()
    serializer_class = BlogMediaFileSerializer
    parser_classes = (MultiPartParser, FormParser)  # Allows file uploads

    @action(detail=False, methods=["post"])
    def upload_media(self, request):
        """Handles file uploads (images, videos, PDFs)."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "File uploaded successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class BlogVideoViewSet(viewsets.ModelViewSet):
    """Handles embedding videos (YouTube, Vimeo, self-hosted)."""
    queryset = BlogVideo.objects.all()
    serializer_class = BlogVideoSerializer

class BlogDarkModeImageViewSet(viewsets.ModelViewSet):
    """Handles retrieving dark mode images."""
    queryset = BlogDarkModeImage.objects.all()
    serializer_class = BlogDarkModeImageSerializer


class OutdatedBlogsViewSet(viewsets.ReadOnlyModelViewSet):
    """Returns blogs that need updating based on freshness score."""
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        """Fetches blogs with a freshness score below 40."""
        return BlogPost.objects.filter(is_published=True).filter(freshness_score__lt=40).order_by("freshness_score")


class RelatedBlogsViewSet(viewsets.ReadOnlyModelViewSet):
    """Returns AI-powered related blogs."""
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        blog_id = self.request.query_params.get("blog_id")
        if not blog_id:
            return BlogPost.objects.none()

        blog = BlogPost.objects.filter(id=blog_id).first()
        return blog.find_related_blogs() if blog else BlogPost.objects.none()

class BlogABTestViewSet(viewsets.ModelViewSet):
    """Handles click tracking & winner selection for A/B tests."""
    serializer_class = BlogABTestSerializer

    def track_click(self, request, *args, **kwargs):
        """Tracks clicks on either version A or B."""
        ab_test = self.get_object()
        version = request.data.get("version")

        if version == "A":
            BlogABTest.objects.filter(id=ab_test.id).update(click_count_a=models.F("click_count_a") + 1)
        else:
            BlogABTest.objects.filter(id=ab_test.id).update(click_count_b=models.F("click_count_b") + 1)

        ab_test.determine_winner()
        ab_test.save()
        return Response({"message": "Click recorded"}, status=200)


class BlogClickViewSet(viewsets.ModelViewSet):
    """Tracks unique clicks per user/IP on blog posts."""
    queryset = BlogClick.objects.all()
    serializer_class = BlogClickSerializer
    permission_classes = [AllowAny]  # Public tracking
    
    def create(self, request, *args, **kwargs):
        """Records a click event if it hasn't been tracked before."""
        blog_id = request.data.get("blog_id")
        user = request.user if request.user.is_authenticated else None
        ip_address = self.get_client_ip(request)

        # Ensure valid blog
        blog = BlogPost.objects.filter(id=blog_id, is_published=True).first()
        if not blog:
            return Response({"error": "Invalid blog ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate click tracking
        if BlogClick.objects.filter(blog=blog, user=user, ip_address=ip_address).exists():
            return Response({"message": "Click already recorded"}, status=status.HTTP_200_OK)

        # Create click event
        BlogClick.objects.create(blog=blog, user=user, ip_address=ip_address)
        blog.increment_clicks(user, ip_address)
        return Response({"message": "Click recorded"}, status=status.HTTP_201_CREATED)

    def get_client_ip(self, request):
        """Retrieves the client's IP address for tracking."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class BlogConversionViewSet(viewsets.ModelViewSet):
    """Tracks conversions from blog posts (Clicked Order Page & Placed Order)."""
    queryset = BlogConversion.objects.all()
    serializer_class = BlogConversionSerializer
    permission_classes = [AllowAny]  # Public tracking

    def create(self, request, *args, **kwargs):
        """Tracks conversion actions (clicked order page, placed order)."""
        blog_id = request.data.get("blog_id")
        action = request.data.get("action")  # Expected: "clicked_order_page" or "placed_order"
        user = request.user if request.user.is_authenticated else None

        # Ensure valid blog
        blog = BlogPost.objects.filter(id=blog_id, is_published=True).first()
        if not blog:
            return Response({"error": "Invalid blog ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create conversion record
        conversion, created = BlogConversion.objects.get_or_create(blog=blog, user=user)

        # Update conversion type
        if action == "clicked_order_page":
            conversion.clicked_order_page = True
        elif action == "placed_order":
            conversion.order_placed = True
        else:
            return Response({"error": "Invalid conversion action"}, status=status.HTTP_400_BAD_REQUEST)

        conversion.save()
        blog.increment_conversions(user, action)

        return Response({"message": f"Conversion recorded for {action}"}, status=status.HTTP_201_CREATED)
    

class SocialPlatformViewSet(viewsets.ModelViewSet):
    """Manages available social platforms."""
    serializer_class = SocialPlatformSerializer
    queryset = SocialPlatform.objects.all()
    permission_classes = [IsAdminSuperadminEditor]

    def get_queryset(self):
        """Filters platforms based on the website and active status."""
        website_id = self.request.query_params.get("website_id")
        queryset = SocialPlatform.objects.filter(is_active=True, is_disabled_by_owner=False)

        if website_id:
            queryset = queryset.filter(website_id=website_id)

        return queryset

    @action(detail=True, methods=["PATCH"])
    def toggle_platform_status(self, request, pk=None):
        """Allows only Admins, Superadmins, and Editors to enable/disable a platform."""
        platform = self.get_object()

        if not request.user or request.user.role not in ["admin", "superadmin", "editor"]:
            return Response({"error": "Permission denied."}, status=403)

        platform.is_disabled_by_owner = not platform.is_disabled_by_owner
        platform.save(update_fields=["is_disabled_by_owner"])

        status = "disabled" if platform.is_disabled_by_owner else "enabled"
        return Response(
            {"message": f"{platform.name} has been {status} for {platform.website.name}."}, status=200
        )


class BlogShareViewSet(viewsets.ModelViewSet):
    """Tracks shares for blog posts."""
    serializer_class = BlogShareSerializer

    def get_queryset(self):
        """Filters shares based on website and blog."""
        website_id = self.request.query_params.get("website_id")
        blog_id = self.request.query_params.get("blog_id")

        queryset = BlogShare.objects.all()
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        if blog_id:
            queryset = queryset.filter(blog_id=blog_id)
        return queryset

    @action(detail=False, methods=["POST"])
    def generate_share_url(self, request):
        """Generates a dynamic social share URL."""
        serializer = BlogShareURLSerializer(data=request.data)
        if serializer.is_valid():
            share_url = serializer.get_share_url()
            return Response({"share_url": share_url}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"])
    def increment_share(self, request):
        """Increments share count when a blog is shared."""
        blog_id = request.data.get("blog_id")
        platform_id = request.data.get("platform_id")

        blog = BlogPost.objects.filter(id=blog_id, is_published=True).first()
        platform = SocialPlatform.objects.filter(id=platform_id, is_active=True).first()

        if not blog or not platform:
            return Response({"error": "Invalid blog or platform"}, status=status.HTTP_400_BAD_REQUEST)

        share, created = BlogShare.objects.get_or_create(blog=blog, platform=platform)
        share.increment_share()
        return Response({"message": "Share count updated"}, status=status.HTTP_200_OK) 