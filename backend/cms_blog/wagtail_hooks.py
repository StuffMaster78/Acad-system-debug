"""
Wagtail hooks for cms_blog.

Registers blog-specific admin customizations:
- Category and Tag snippet viewsets with tenant scoping
- Blog post listing enhancements
"""

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet
from wagtail import hooks

from cms_core.models import BlogCategory, BlogTag
from cms_core.services.tenant_service import filter_queryset_by_user_sites


class BlogCategorySnippetViewSet(SnippetViewSet):
    """Tenant-scoped blog category admin."""

    model = BlogCategory
    icon = "tag"
    menu_label = "Blog Categories"
    menu_name = "blog-categories"
    menu_order = 300
    add_to_admin_menu = True
    list_display = [
        "name",
        "slug",
        "site",
        "is_featured",
        "is_active",
        "display_order",
    ]
    list_filter = ["is_featured", "is_active", "site"]
    search_fields = ["name", "description"]

    def get_queryset(self, request=None):
        qs = super().get_queryset(request)
        if not request:
            return qs
        return filter_queryset_by_user_sites(qs, request.user)


class BlogTagSnippetViewSet(SnippetViewSet):
    """Tenant-scoped blog tag admin."""

    model = BlogTag
    icon = "tag"
    menu_label = "Blog Tags"
    menu_name = "blog-tags"
    menu_order = 310
    add_to_admin_menu = True
    list_display = ["name", "slug", "site"]
    list_filter = ["site"]
    search_fields = ["name"]

    def get_queryset(self, request=None):
        qs = super().get_queryset(request)
        if not request:
            return qs
        return filter_queryset_by_user_sites(qs, request.user)


register_snippet(BlogCategorySnippetViewSet)
register_snippet(BlogTagSnippetViewSet)


@hooks.register("after_publish_page")
def update_blog_substantive_timestamp(request, page):
    """Prompt editors to mark substantive updates on blog posts.

    If the page is a BlogPostPage and `last_substantive_update` is
    not set, auto-set it on first publish.
    """
    from cms_blog.models import BlogPostPage

    if not isinstance(page.specific, BlogPostPage):
        return

    blog_post = page.specific
    if blog_post.last_substantive_update is None:
        from django.utils import timezone

        blog_post.last_substantive_update = timezone.now()
        blog_post.save(update_fields=["last_substantive_update"])