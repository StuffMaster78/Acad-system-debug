"""
Tests for cms_engagement — views, reactions, shares, bookmarks.
"""

import pytest
from django.contrib.contenttypes.models import ContentType


@pytest.mark.django_db
class TestPageViewTracking:

    def test_track_page_view(self, test_blog_post, tenant_site):
        from cms_engagement.models import PageView

        ct = ContentType.objects.get_for_model(test_blog_post)
        PageView.objects.create(
            content_type=ct,
            object_id=test_blog_post.pk,
            site=tenant_site,
            session_id="test-session-123",
            time_on_page=45,
            scroll_depth=72,
        )
        assert PageView.objects.filter(
            content_type=ct, object_id=test_blog_post.pk
        ).count() == 1


@pytest.mark.django_db
class TestReactions:

    def test_add_reaction(self, test_blog_post, tenant_site, editor_user):
        from cms_engagement.models import PageReaction

        ct = ContentType.objects.get_for_model(test_blog_post)
        reaction = PageReaction.objects.create(
            content_type=ct,
            object_id=test_blog_post.pk,
            site=tenant_site,
            user=editor_user,
            reaction_type="useful",
        )
        assert reaction.reaction_type == "useful"

    def test_unique_per_user(self, test_blog_post, tenant_site, editor_user):
        from cms_engagement.models import PageReaction

        ct = ContentType.objects.get_for_model(test_blog_post)
        PageReaction.objects.create(
            content_type=ct,
            object_id=test_blog_post.pk,
            site=tenant_site,
            user=editor_user,
            reaction_type="thumbs_up",
        )
        # Second reaction by same user should violate constraint
        from django.db import IntegrityError

        with pytest.raises(IntegrityError):
            PageReaction.objects.create(
                content_type=ct,
                object_id=test_blog_post.pk,
                site=tenant_site,
                user=editor_user,
                reaction_type="love",
            )
