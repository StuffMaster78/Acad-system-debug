"""
Tests for cms_blog — blog post creation, validation, properties.
"""

import pytest


@pytest.mark.django_db
class TestBlogPostCreation:

    def test_create_blog_post(self, blog_index, test_author):
        from cms_blog.models import BlogPostPage

        post = BlogPostPage(
            title="Test Post",
            slug="test-post",
            primary_author=test_author,
            excerpt="A test post.",
            body=[
                ("heading", {"text": "Introduction", "level": "h2"}),
                ("paragraph", "<p>This is a test paragraph with enough words to count.</p>"),
            ],
        )
        blog_index.add_child(instance=post)
        assert post.pk is not None
        assert post.url.endswith("/test-post/")

    def test_blog_post_word_count(self, test_blog_post):
        assert test_blog_post.word_count > 0

    def test_blog_post_reading_time(self, test_blog_post):
        assert "min read" in test_blog_post.reading_time

    def test_blog_post_toc(self, test_blog_post):
        toc = test_blog_post.toc
        assert len(toc) >= 3  # Introduction, Step 1, Step 2

    def test_blog_post_requires_author(self, blog_index):
        from cms_blog.models import BlogPostPage

        post = BlogPostPage(
            title="No Author Post",
            slug="no-author",
            body=[("paragraph", "<p>Content</p>")],
        )
        # Should fail validation on publish (author required)
        blog_index.add_child(instance=post)
        from cms_core.validators import validate_page_for_publish

        result = validate_page_for_publish(post)
        has_author_blocker = any(
            "author" in b["message"].lower()
            for b in result.blockers
        )
        assert has_author_blocker


@pytest.mark.django_db
class TestBlogPostPublishing:

    def test_publish_sets_first_published_at(self, test_blog_post):
        assert test_blog_post.first_published_at is not None

    def test_revision_created(self, test_blog_post):
        assert test_blog_post.revisions.count() >= 1
