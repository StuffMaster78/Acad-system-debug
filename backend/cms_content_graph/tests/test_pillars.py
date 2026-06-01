"""
Tests for cms_content_graph — pillars, links, relationships.
"""

import pytest


@pytest.mark.django_db
class TestContentPillar:

    def test_pillar_creation(self, test_pillar):
        assert test_pillar.name == "Nursing Care Plans"
        assert test_pillar.service_page is not None
        assert test_pillar.hub_post is not None

    def test_pillar_spoke_posts(self, test_pillar, test_blog_post):
        # The hub post is excluded from spokes
        spokes = list(test_pillar.spoke_posts)
        assert test_blog_post not in spokes # hub is excluded


@pytest.mark.django_db
class TestBlogServiceLink:

    def test_create_link(self, test_blog_post, test_service_page):
        from cms_content_graph.models import BlogServiceLink

        link = BlogServiceLink.objects.create(
            blog_post=test_blog_post,
            service_page=test_service_page,
            placement="end_cta",
            cta_text="Get your care plan written by an RN →",
            is_primary_route=True,
        )
        assert link.ctr == 0.0 # no impressions yet

    def test_ctr_calculation(self, test_blog_post, test_service_page):
        from cms_content_graph.models import BlogServiceLink

        link = BlogServiceLink.objects.create(
            blog_post=test_blog_post,
            service_page=test_service_page,
            placement="inline_card",
            cta_text="See our service",
            impressions=1000,
            clicks=45,
        )
        assert link.ctr == 4.5


@pytest.mark.django_db
class TestInternalLinkingService:

    def test_suggest_links(self, test_blog_post, test_service_page, test_pillar):
        from cms_content_graph.services.linking_service import InternalLinkingService

        suggestions = InternalLinkingService.suggest_links_for_page(test_blog_post)
        assert len(suggestions) > 0
        # Should suggest the primary service
        service_suggested = any(
            s["page_id"] == test_service_page.pk for s in suggestions
        )
        assert service_suggested
