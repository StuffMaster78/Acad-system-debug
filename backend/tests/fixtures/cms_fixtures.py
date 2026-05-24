from __future__ import annotations

import pytest


@pytest.fixture
def test_author(tenant_site):
    from cms_authors.models import Author

    return Author.objects.create(
        site=tenant_site,
        name="Dr. Jane Smith",
        slug="jane-smith",
        bio=(
            "Board-certified RN with 15 years of nursing education "
            "experience."
        ),
        credentials="MSN, RN, CCRN",
        degrees=[
            {
                "degree": "MSN",
                "institution": "Johns Hopkins",
                "year": 2015,
            }
        ],
        areas_of_expertise=(
            "Nursing Care Plans, Evidence-Based Practice"
        ),
        years_experience=15,
        role="senior_writer",
        is_active=True,
        show_publicly=True,
    )


@pytest.fixture
def blog_category(tenant_site):
    from cms_core.models import BlogCategory

    return BlogCategory.objects.create(
        site=tenant_site,
        name="Nursing Guides",
        slug="nursing-guides",
        is_active=True,
    )


@pytest.fixture
def service_category(tenant_site):
    from cms_core.models import ServiceCategory

    return ServiceCategory.objects.create(
        site=tenant_site,
        name="Nursing Services",
        slug="nursing-services",
    )


@pytest.fixture
def blog_index(tenant_site):
    from cms_blog.models import BlogIndexPage

    page = BlogIndexPage.objects.descendant_of(
        tenant_site.root_page,
    ).first()

    assert page is not None

    return page


@pytest.fixture
def service_index(tenant_site):
    from cms_service_pages.models import ServiceIndexPage

    page = ServiceIndexPage.objects.descendant_of(
        tenant_site.root_page,
    ).first()

    assert page is not None

    return page


@pytest.fixture
def test_blog_post(blog_index, test_author, blog_category):
    from cms_blog.models import BlogPostPage

    post = BlogPostPage(
        title="How to Write a Nursing Care Plan",
        slug="how-to-write-nursing-care-plan",
        primary_author=test_author,
        category=blog_category,
        excerpt=(
            "A step-by-step guide to writing effective nursing care plans."
        ),
        body=[
            ("heading", {"text": "Introduction", "level": "h2"}),
            (
                "paragraph",
                "<p>Nursing care plans are essential documents...</p>",
            ),
            ("heading", {"text": "Step 1: Assessment", "level": "h2"}),
            ("paragraph", "<p>Begin by assessing the patient...</p>"),
            ("heading", {"text": "Step 2: Diagnosis", "level": "h2"}),
            ("paragraph", "<p>Use NANDA-I nursing diagnoses...</p>"),
        ],
    )

    blog_index.add_child(instance=post)
    post.save_revision().publish()

    return post


@pytest.fixture
def test_service_page(service_index, service_category):
    from cms_service_pages.models import ServicePage

    page = ServicePage(
        title="Nursing Care Plan Writing Help",
        slug="nursing-care-plan-writing",
        service_category=service_category,
        pricing_from=15.99,
        pricing_to=45.99,
        turnaround_hours_fastest=6,
        turnaround_hours_standard=168,
        primary_cta_text="Order Now",
        primary_cta_url="/order/",
        body=[
            (
                "hero",
                {
                    "headline": "Expert Nursing Care Plan Writing",
                    "subheadline": "Written by real RNs",
                    "cta_text": "Order Now",
                    "cta_url": "/order/",
                },
            ),
            ("paragraph", "<p>Our team of certified nurses...</p>"),
        ],
    )

    service_index.add_child(instance=page)
    page.save_revision().publish()

    return page


@pytest.fixture
def test_pillar(tenant_site, test_service_page, test_blog_post):
    from cms_content_graph.models import ContentPillar

    pillar = ContentPillar.objects.create(
        site=tenant_site,
        name="Nursing Care Plans",
        slug="nursing-care-plans",
        service_page=test_service_page,
        hub_post=test_blog_post,
        target_keywords=[
            "nursing care plan",
            "care plan example",
        ],
    )

    test_blog_post.pillar = pillar
    test_blog_post.primary_service = test_service_page
    test_blog_post.save()

    return pillar