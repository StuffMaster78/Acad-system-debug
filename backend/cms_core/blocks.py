"""
CMS Block Library
=================

Defines all StreamField block types used across the platform.

Organization:
- Shared blocks: available on both blog posts and service pages
- Blog-only blocks: SourcesListBlock, RelatedPostsBlock, CodeBlock
- Service-page-only blocks: HeroBlock, TrustStripBlock, FeatureGridBlock, etc.

Two exported StreamBlocks:
- BLOG_BLOCKS: used by BlogPostPage.body
- SERVICE_PAGE_BLOCKS: used by ServicePage.body
"""

from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    IntegerBlock,
    ListBlock,
    RichTextBlock,
    StaticBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
    DecimalBlock,
    PageChooserBlock,
)
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


# ===========================================================================
# SHARED BLOCKS (available on both blog posts and service pages)
# ===========================================================================

class HeadingBlock(StructBlock):
    """Section heading. H2/H3/H4 only — H1 is the page title."""
    text = CharBlock(max_length=255)
    level = ChoiceBlock(
        choices=[("h2", "H2"), ("h3", "H3"), ("h4", "H4")],
        default="h2",
    )

    class Meta:
        icon = "title"
        label = "Heading"
        template = "cms_core/blocks/heading.html"


class ParagraphBlock(RichTextBlock):
    """Rich text paragraph. Supports bold, italic, links."""

    class Meta:
        icon = "pilcrow"
        label = "Paragraph"
        template = "cms_core/blocks/paragraph.html"


class ImageBlock(StructBlock):
    """Image with required alt text and optional caption."""
    image = ImageChooserBlock()
    alt_text = CharBlock(
        required=True,
        max_length=125,
        help_text="Required for accessibility and SEO (max 125 chars)",
    )
    caption = CharBlock(required=False, max_length=255)

    class Meta:
        icon = "image"
        label = "Image"
        template = "cms_core/blocks/image.html"


class ListBlock_(StructBlock):
    """Bulleted or numbered list."""
    style = ChoiceBlock(
        choices=[("bulleted", "Bulleted"), ("numbered", "Numbered")],
        default="bulleted",
    )
    items = ListBlock(
        RichTextBlock(features=["bold", "italic", "link"]),
        min_num=1,
    )

    class Meta:
        icon = "list-ul"
        label = "List"
        template = "cms_core/blocks/list.html"


class QuoteBlock(StructBlock):
    """Pull quote with optional attribution."""
    text = RichTextBlock(features=["bold", "italic"])
    attribution = CharBlock(required=False, max_length=255)

    class Meta:
        icon = "openquote"
        label = "Quote"
        template = "cms_core/blocks/quote.html"


class CalloutBlock(StructBlock):
    """Info box / callout with style variants."""
    style = ChoiceBlock(
        choices=[
            ("note", "Note"),
            ("tip", "Tip"),
            ("warning", "Warning"),
            ("important", "Important"),
        ],
        default="note",
    )
    text = RichTextBlock(features=["bold", "italic", "link"])

    class Meta:
        icon = "warning"
        label = "Callout"
        template = "cms_core/blocks/callout.html"


class FAQItemBlock(StructBlock):
    """Single FAQ entry. Renders as <details> for HTML semantics.
    When 3+ appear on a page, emits FAQPage schema."""
    question = CharBlock(max_length=500)
    answer = RichTextBlock()

    class Meta:
        icon = "help"
        label = "FAQ Item"
        template = "cms_core/blocks/faq_item.html"


class CTABlock(StructBlock):
    """Call-to-action button."""
    text = CharBlock(max_length=100)
    url = URLBlock()
    style = ChoiceBlock(
        choices=[
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("outline", "Outline"),
        ],
        default="primary",
    )

    class Meta:
        icon = "plus"
        label = "Call to Action"
        template = "cms_core/blocks/cta.html"


class InternalLinkCardBlock(StructBlock):
    """Visual card linking to another page on the same site."""
    page = PageChooserBlock()
    custom_title = CharBlock(
        required=False,
        help_text="Override the page's title for this link",
    )
    custom_description = CharBlock(required=False, max_length=200)

    class Meta:
        icon = "link"
        label = "Internal Link Card"
        template = "cms_core/blocks/internal_link_card.html"


class AttachmentReferenceBlock(StructBlock):
    """Embed a downloadable attachment from the library."""
    attachment = SnippetChooserBlock("cms_attachments.Attachment")
    display_style = ChoiceBlock(
        choices=[
            ("card", "Card with preview"),
            ("list", "Compact list item"),
            ("hero", "Large hero card"),
            ("button", "Simple download button"),
        ],
        default="card",
    )
    custom_title = CharBlock(required=False)
    custom_cta_text = CharBlock(
        required=False,
        default="Download Now",
    )

    class Meta:
        icon = "doc-full"
        label = "Downloadable File"
        template = "cms_core/blocks/attachment_reference.html"


class VideoEmbedBlock(StructBlock):
    """YouTube or Vimeo embed."""
    url = URLBlock(help_text="YouTube or Vimeo URL")
    caption = CharBlock(required=False, max_length=255)

    class Meta:
        icon = "media"
        label = "Video Embed"
        template = "cms_core/blocks/video_embed.html"


class DividerBlock(StaticBlock):
    """Horizontal rule / section divider."""

    class Meta:
        icon = "horizontalrule"
        label = "Divider"
        admin_text = "--- Divider ---"
        template = "cms_core/blocks/divider.html"


# ===========================================================================
# CHECKLIST BLOCK (shared)
# ===========================================================================

class ChecklistItemBlock(StructBlock):
    """Single item in a checklist."""
    text = CharBlock(max_length=300)
    detail = CharBlock(
        required=False,
        max_length=500,
        help_text="Optional supporting detail shown below the item.",
    )

    class Meta:
        icon = "tick-inverse"
        label = "Checklist Item"


class ChecklistBlock(StructBlock):
    """
    Actionable checklist with optional per-item detail.

    Use for 'how-to' posts: 'thesis writing checklist',
    'APA formatting checklist'. High engagement and bookmark rate.
    """
    title = CharBlock(max_length=200)
    items = ListBlock(ChecklistItemBlock(), min_num=2, max_num=20)

    class Meta:
        icon = "tasks"
        label = "Checklist"
        template = "cms_core/blocks/checklist.html"


# ===========================================================================
# STATS HIGHLIGHT BLOCK (shared)
# ===========================================================================

class StatItemBlock(StructBlock):
    """A single stat — big number + short label."""
    value = CharBlock(
        max_length=50,
        help_text="The headline figure, e.g. '98%' or '50,000+' or '4.8★'",
    )
    label = CharBlock(
        max_length=100,
        help_text="What the figure means, e.g. 'on-time delivery'",
    )

    class Meta:
        icon = "pick"
        label = "Stat"


class StatsHighlightBlock(StructBlock):
    """
    Row of headline stats — trust signals at a glance.

    Use on service pages and top-of-funnel posts.
    2–6 stats render as a responsive grid.
    """
    stats = ListBlock(StatItemBlock(), min_num=2, max_num=6)
    supporting_text = CharBlock(
        required=False,
        max_length=255,
        help_text="Optional small-print below the stats row.",
    )

    class Meta:
        icon = "pick"
        label = "Stats Highlight"
        template = "cms_core/blocks/stats_highlight.html"


# ===========================================================================
# BEFORE / AFTER BLOCK (shared)
# ===========================================================================

class BeforeAfterBlock(StructBlock):
    """
    Side-by-side writing comparison.

    Show a weak draft alongside an improved version.
    Highly effective for writing guides and highly shareable.
    """
    heading = CharBlock(max_length=255, required=False, default="Before & After")
    label_before = CharBlock(max_length=50, default="Before")
    content_before = RichTextBlock(
        features=["bold", "italic"],
        help_text="The weak/original version.",
    )
    label_after = CharBlock(max_length=50, default="After")
    content_after = RichTextBlock(
        features=["bold", "italic"],
        help_text="The improved version.",
    )
    caption = CharBlock(required=False, max_length=255)

    class Meta:
        icon = "arrows-up-down"
        label = "Before & After"
        template = "cms_core/blocks/before_after.html"


# ===========================================================================
# SAMPLE EXCERPT BLOCK (blog-preferred, available everywhere)
# ===========================================================================

class SampleExcerptBlock(StructBlock):
    """
    Formatted preview of academic writing.

    Shows a styled excerpt that looks like a real paper, with
    formatting style and academic level badges. Links to a full
    downloadable sample via an Attachment snippet.
    """
    title = CharBlock(
        max_length=255,
        required=False,
        help_text="E.g. 'Sample APA Research Paper Introduction'",
    )
    formatting_style = ChoiceBlock(
        choices=[
            ("apa7", "APA 7th Edition"),
            ("mla9", "MLA 9th Edition"),
            ("chicago", "Chicago / Turabian"),
            ("harvard", "Harvard"),
            ("ieee", "IEEE"),
            ("none", "None / General"),
        ],
        default="apa7",
    )
    academic_level = ChoiceBlock(
        choices=[
            ("high_school", "High School"),
            ("undergraduate", "Undergraduate"),
            ("graduate", "Graduate / Masters"),
            ("phd", "PhD / Doctoral"),
        ],
        default="undergraduate",
    )
    excerpt = RichTextBlock(
        features=["bold", "italic"],
        help_text="The excerpt text. Style as you would a real paper excerpt.",
    )
    attachment = SnippetChooserBlock(
        "cms_attachments.Attachment",
        required=False,
        help_text="Full downloadable sample linked to this excerpt.",
    )
    download_cta = CharBlock(
        max_length=100,
        default="Download Full Sample",
        required=False,
    )

    class Meta:
        icon = "doc-full"
        label = "Sample Excerpt"
        template = "cms_core/blocks/sample_excerpt.html"


# ===========================================================================
# DEFINITION BLOCK (shared)
# ===========================================================================

class DefinitionBlock(StructBlock):
    """
    Inline term definition.

    Academic content is terminology-heavy. Use this to define
    jargon in-line without breaking the prose flow.
    Outputs DefinedTerm schema markup.
    """
    term = CharBlock(max_length=200)
    definition = RichTextBlock(features=["bold", "italic", "link"])
    example = CharBlock(
        required=False,
        max_length=500,
        help_text="Optional usage example in plain text.",
    )

    class Meta:
        icon = "search"
        label = "Definition"
        template = "cms_core/blocks/definition.html"


# ===========================================================================
# TIMELINE BLOCK (shared)
# ===========================================================================

class TimelineEntryBlock(StructBlock):
    """One entry in a timeline."""
    date_label = CharBlock(
        max_length=100,
        help_text="Date or step label, e.g. '1929', 'Step 3', or 'Ancient Rome'",
    )
    title = CharBlock(max_length=255)
    description = RichTextBlock(features=["bold", "italic", "link"])

    class Meta:
        icon = "time"
        label = "Timeline Entry"


class TimelineBlock(StructBlock):
    """
    Vertical timeline of events or steps.

    Use for history posts ('History of APA citation') or long
    step-by-step guides that exceed the 6-item limit of HowItWorksBlock.
    """
    heading = CharBlock(max_length=255, required=False)
    entries = ListBlock(TimelineEntryBlock(), min_num=2, max_num=15)

    class Meta:
        icon = "time"
        label = "Timeline"
        template = "cms_core/blocks/timeline.html"


# ===========================================================================
# EMBED BLOCK (shared)
# ===========================================================================

ALLOWED_EMBED_DOMAINS = [
    "docs.google.com",
    "sheets.google.com",
    "slides.google.com",
    "public.tableau.com",
    "app.flourish.studio",
    "datawrapper.dwcdn.net",
    "www.canva.com",
    "prezi.com",
    "airtable.com",
    "app.powerbi.com",
]


class EmbedBlock(StructBlock):
    """
    Sandboxed iframe embed for third-party data tools.

    Accepted sources: Google Sheets/Slides/Docs, Tableau,
    Flourish, Datawrapper, Canva, Prezi, Airtable, Power BI.
    Domain is validated on save — arbitrary iframes are rejected.
    """
    embed_url = URLBlock(
        help_text=(
            "Embed URL from the share/publish dialog. "
            "Accepted: Google Sheets/Docs/Slides, Tableau, Flourish, "
            "Datawrapper, Canva, Prezi, Airtable, Power BI."
        ),
    )
    height = IntegerBlock(
        default=480,
        min_value=200,
        max_value=1200,
        help_text="Height in pixels (200–1200).",
    )
    caption = CharBlock(required=False, max_length=255)

    class Meta:
        icon = "code"
        label = "Embed (chart / sheet / slides)"
        template = "cms_core/blocks/embed.html"

    def clean(self, value):
        value = super().clean(value)
        url = str(value.get("embed_url", ""))
        from urllib.parse import urlparse
        try:
            host = urlparse(url).netloc.lower().lstrip("www.")
        except Exception:
            host = ""
        allowed = {d.lstrip("www.") for d in ALLOWED_EMBED_DOMAINS}
        if url and not any(host == d or host.endswith("." + d) for d in allowed):
            from wagtail.blocks import StreamBlockValidationError
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f"Embed domain '{host}' is not allowed. "
                f"Accepted: {', '.join(sorted(allowed))}"
            )
        return value


# ===========================================================================
# KEY TAKEAWAYS BLOCK (shared)
# ===========================================================================

class KeyTakeawaysBlock(StructBlock):
    """
    'Key Takeaways' summary box — typically placed just after the intro.

    Signals to Google what the post covers; frequently pulled into
    featured snippets. Each item should be one clear, standalone sentence.
    """
    heading = CharBlock(max_length=100, default="Key Takeaways")
    items = ListBlock(
        CharBlock(max_length=300),
        min_num=2,
        max_num=8,
        help_text="Each item becomes one bullet. Keep to one sentence per takeaway.",
    )

    class Meta:
        icon = "list-ul"
        label = "Key Takeaways"
        template = "cms_core/blocks/key_takeaways.html"


# ===========================================================================
# TABLE OF CONTENTS BLOCK (shared)
# ===========================================================================

class TocEntryBlock(StructBlock):
    """One entry in the table of contents."""
    label = CharBlock(max_length=200, help_text="Visible link text, e.g. 'Introduction'")
    anchor = CharBlock(
        max_length=100,
        help_text="Heading ID without the #, e.g. 'introduction'. Must match a heading id on the page.",
    )

    class Meta:
        icon = "link"
        label = "TOC Entry"


class TableOfContentsBlock(StructBlock):
    """
    Manual table of contents with anchor links.

    Place near the top of long posts. Google uses TOC blocks to generate
    jump-link rich results under the page title in search.
    Anchor values must match heading IDs on the rendered page.
    """
    heading = CharBlock(max_length=100, default="In This Article", required=False)
    entries = ListBlock(TocEntryBlock(), min_num=2, max_num=20)

    class Meta:
        icon = "list-ol"
        label = "Table of Contents"
        template = "cms_core/blocks/toc.html"


# ===========================================================================
# AUTHOR REVIEW BADGE BLOCK (shared)
# ===========================================================================

class AuthorReviewBadgeBlock(StructBlock):
    """
    Expert review attribution badge — inline E-E-A-T signal.

    Different from the page-level primary_author field. Use this to
    surface the reviewing expert mid-article or in a sidebar position.
    Outputs ReviewedBy schema markup.
    """
    reviewer_name = CharBlock(max_length=100, help_text="Full name of the reviewing expert.")
    credentials = CharBlock(
        max_length=255,
        help_text="E.g. 'PhD in Clinical Psychology, Harvard University'",
    )
    review_date = CharBlock(
        max_length=50,
        help_text="Display date, e.g. 'June 2026' or '2026-06-01'.",
    )
    photo = ImageChooserBlock(required=False)
    reviewer_url = URLBlock(
        required=False,
        help_text="Link to the reviewer's author bio page.",
    )

    class Meta:
        icon = "user"
        label = "Expert Review Badge"
        template = "cms_core/blocks/author_review_badge.html"


# ===========================================================================
# DISCLAIMER BLOCK (shared)
# ===========================================================================

class DisclaimerBlock(StructBlock):
    """
    Legal or academic notice block.

    The 'academic_integrity' style is the most important for a writing
    services platform — it must appear on any post that could be
    misconstrued as contract cheating promotion.
    """
    style = ChoiceBlock(
        choices=[
            ("academic_integrity", "Academic Integrity"),
            ("copyright", "Copyright Notice"),
            ("medical", "Medical / Health"),
            ("general", "General Notice"),
        ],
        default="academic_integrity",
    )
    text = RichTextBlock(
        features=["bold", "italic", "link"],
        help_text="The full disclaimer text. Keep factual and plain.",
    )

    class Meta:
        icon = "warning"
        label = "Disclaimer / Notice"
        template = "cms_core/blocks/disclaimer.html"


# ===========================================================================
# DATA TABLE BLOCK (shared)
# ===========================================================================

class TableDataBlock(StructBlock):
    """
    Editable data table with an optional caption.

    The inner TableBlock is backed by Handsontable in the Wagtail admin.
    Editors can set whether the first row and/or first column are headers.
    Data is stored as a 2-D array of strings.
    """
    caption = CharBlock(
        required=False,
        max_length=255,
        help_text="Optional caption displayed below the table.",
    )
    table = TableBlock(
        table_options={
            "minSpareRows": 1,
            "startRows": 4,
            "startCols": 3,
            "colHeaders": False,
            "rowHeaders": False,
            "contextMenu": True,
        },
        help_text="Enter data. Use Table → Options to mark header rows/columns.",
    )

    class Meta:
        icon = "table"
        label = "Data Table"
        template = "cms_core/blocks/table.html"


# ===========================================================================
# CHART BLOCK (shared)
# ===========================================================================

class ChartDatasetBlock(StructBlock):
    """One data series inside a chart."""
    label = CharBlock(max_length=100, help_text="Series name, e.g. 'Revenue'")
    values = CharBlock(
        help_text="Comma-separated numbers matching the x-axis labels, e.g. 10,20,30,15",
    )
    color = CharBlock(
        required=False,
        max_length=30,
        help_text="Hex color code, e.g. #7c3aed. Leave blank for auto.",
    )

    class Meta:
        icon = "list-ul"
        label = "Dataset"


class ChartBlock(StructBlock):
    """
    Inline data chart. Renders via ECharts on the frontend.

    Bar and line charts support multiple datasets. Pie/doughnut use
    only the first dataset.
    """
    chart_type = ChoiceBlock(
        choices=[
            ("bar", "Bar chart"),
            ("line", "Line chart"),
            ("pie", "Pie chart"),
            ("doughnut", "Doughnut chart"),
        ],
        default="bar",
    )
    title = CharBlock(max_length=255)
    caption = CharBlock(
        required=False,
        max_length=255,
        help_text="Optional caption displayed below the chart.",
    )
    x_labels = CharBlock(
        help_text="Category labels (comma-separated), e.g. Jan,Feb,Mar,Apr",
    )
    datasets = ListBlock(
        ChartDatasetBlock(),
        min_num=1,
        max_num=5,
        help_text="Add one dataset per series. Pie/doughnut uses the first dataset only.",
    )

    class Meta:
        icon = "media"
        label = "Chart"
        template = "cms_core/blocks/chart.html"


# ===========================================================================
# BLOG-ONLY BLOCKS
# ===========================================================================

class SourceItemBlock(StructBlock):
    """One entry in the 'Articles Consulted' list."""
    title = CharBlock(max_length=500)
    url = URLBlock()
    author = CharBlock(required=False, max_length=255)
    publication = CharBlock(required=False, max_length=255)
    year = CharBlock(required=False, max_length=10)

    class Meta:
        icon = "link-external"
        label = "Source"


class SourcesListBlock(StructBlock):
    """The 'Articles Consulted' / 'References' section at the bottom of a blog post.
    This is the default citation mode (EssayPro pattern)."""
    heading = CharBlock(max_length=100, default="Articles Consulted")
    sources = ListBlock(SourceItemBlock(), min_num=1, max_num=30)

    class Meta:
        icon = "list-ul"
        label = "Sources / References"
        template = "cms_core/blocks/sources_list.html"


class RelatedPostsBlock(StructBlock):
    """Curated list of related blog posts."""
    heading = CharBlock(max_length=100, default="Related Articles")
    posts = ListBlock(
        PageChooserBlock(page_type="cms_blog.BlogPostPage"),
        max_num=5,
    )

    class Meta:
        icon = "grip"
        label = "Related Posts"
        template = "cms_core/blocks/related_posts.html"


class CodeBlock(StructBlock):
    """Code or citation sample block."""
    language = ChoiceBlock(
        choices=[
            ("text", "Plain Text"),
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("html", "HTML"),
            ("css", "CSS"),
            ("apa", "APA Citation Sample"),
        ],
        default="text",
    )
    code = TextBlock()
    caption = CharBlock(required=False, max_length=255)

    class Meta:
        icon = "code"
        label = "Code Block"
        template = "cms_core/blocks/code.html"


# ===========================================================================
# SERVICE-PAGE-ONLY BLOCKS
# ===========================================================================

class HeroBlock(StructBlock):
    """Hero section for top of service pages."""
    headline = CharBlock(max_length=255)
    subheadline = CharBlock(required=False, max_length=500)
    cta_text = CharBlock(max_length=100, default="Order Now")
    cta_url = URLBlock()
    background_image = ImageChooserBlock(required=False)

    class Meta:
        icon = "pick"
        label = "Hero Section"
        template = "cms_core/blocks/hero.html"


class TrustStripBlock(StructBlock):
    """Trust indicators bar — rating, reviews, experience."""
    rating_value = DecimalBlock(max_value=5.0)
    review_count = IntegerBlock()
    years_in_business = IntegerBlock()
    orders_completed = IntegerBlock()

    class Meta:
        icon = "tick-inverse"
        label = "Trust Strip"
        template = "cms_core/blocks/trust_strip.html"


class FeatureItemBlock(StructBlock):
    icon_name = CharBlock(required=False, max_length=50, help_text="Icon name")
    title = CharBlock(max_length=255)
    description = RichTextBlock()


class FeatureGridBlock(StructBlock):
    """'What You Get' feature highlights."""
    heading = CharBlock(max_length=255, default="What You Get")
    features = ListBlock(FeatureItemBlock(), min_num=3, max_num=6)

    class Meta:
        icon = "grip"
        label = "Feature Grid"
        template = "cms_core/blocks/feature_grid.html"


class ProcessStepBlock(StructBlock):
    step_number = IntegerBlock()
    title = CharBlock(max_length=255)
    description = RichTextBlock()


class HowItWorksBlock(StructBlock):
    """Numbered process steps."""
    heading = CharBlock(max_length=255, default="How It Works")
    steps = ListBlock(ProcessStepBlock(), min_num=3, max_num=6)

    class Meta:
        icon = "list-ol"
        label = "How It Works"
        template = "cms_core/blocks/how_it_works.html"


class TestimonialItemBlock(StructBlock):
    quote = RichTextBlock()
    author_name = CharBlock(max_length=255)
    author_title = CharBlock(required=False, max_length=255)
    rating = IntegerBlock(min_value=1, max_value=5)


class TestimonialGroupBlock(StructBlock):
    """Group of customer testimonials."""
    heading = CharBlock(max_length=255, default="What Our Clients Say")
    testimonials = ListBlock(TestimonialItemBlock(), min_num=1, max_num=10)

    class Meta:
        icon = "group"
        label = "Testimonials"
        template = "cms_core/blocks/testimonial_group.html"


class PricingRowBlock(StructBlock):
    service = CharBlock(max_length=255)
    price = CharBlock(max_length=50)
    turnaround = CharBlock(max_length=100)


class PricingTableBlock(StructBlock):
    """Service pricing display."""
    heading = CharBlock(max_length=255, default="Pricing")
    rows = ListBlock(PricingRowBlock(), min_num=2)

    class Meta:
        icon = "form"
        label = "Pricing Table"
        template = "cms_core/blocks/pricing_table.html"


class ComparisonRowBlock(StructBlock):
    feature = CharBlock(max_length=255)
    us = CharBlock(max_length=255)
    competitor = CharBlock(max_length=255)


class ComparisonTableBlock(StructBlock):
    """Us vs competitors comparison."""
    heading = CharBlock(max_length=255, default="Why Choose Us")
    competitor_name = CharBlock(max_length=255)
    rows = ListBlock(ComparisonRowBlock(), min_num=3)

    class Meta:
        icon = "table"
        label = "Comparison Table"
        template = "cms_core/blocks/comparison_table.html"


class GuaranteeItemBlock(StructBlock):
    icon_name = CharBlock(required=False, max_length=50)
    title = CharBlock(max_length=255)
    description = CharBlock(max_length=500)


class GuaranteesBlock(StructBlock):
    """Money-back, on-time, plagiarism-free guarantees."""
    heading = CharBlock(max_length=255, default="Our Guarantees")
    guarantees = ListBlock(GuaranteeItemBlock(), min_num=2, max_num=5)

    class Meta:
        icon = "tick-inverse"
        label = "Guarantees"
        template = "cms_core/blocks/guarantees.html"


# ===========================================================================
# COMPOSED STREAMBLOCKS — the two exports other apps use
# ===========================================================================

class CalculatorBlock(StructBlock):
    """
    Embeds an interactive pricing calculator widget inside a service page or
    blog post. The frontend renders this as a Vue component that calls the
    pricing quote API in real time — no page reload needed.

    Admin fields configure the pre-selected defaults so each embed is
    contextually relevant (e.g., a nursing essay page defaults to nursing
    subject and standard deadline).
    """

    title = CharBlock(
        required=False,
        max_length=120,
        help_text="Heading shown above the calculator (e.g. 'Get your instant price').",
    )
    subtitle = CharBlock(
        required=False,
        max_length=255,
        help_text="Optional supporting line beneath the heading.",
    )
    service_code = ChoiceBlock(
        choices=[
            ("standard_paper", "Standard Paper (essay, research paper, etc.)"),
            ("design",         "Design / Presentation (slides, infographic)"),
            ("diagram",        "Diagram / Chart"),
        ],
        default="standard_paper",
        help_text="Which pricing service this calculator quotes.",
    )
    default_pages = IntegerBlock(
        required=False,
        default=1,
        min_value=1,
        max_value=500,
        help_text="Pre-selected page count when the widget loads.",
    )
    default_deadline_hours = IntegerBlock(
        required=False,
        default=48,
        min_value=1,
        help_text="Pre-selected deadline (hours) when the widget loads.",
    )
    default_academic_level_code = CharBlock(
        required=False,
        max_length=50,
        help_text="Pre-selected academic level code (e.g. 'undergraduate'). Leave blank for no default.",
    )
    default_paper_type_code = CharBlock(
        required=False,
        max_length=50,
        help_text="Pre-selected paper type code (e.g. 'essay'). Leave blank for no default.",
    )
    show_line_breakdown = ChoiceBlock(
        choices=[
            ("yes", "Yes — show full price breakdown"),
            ("no",  "No — show final price only"),
        ],
        default="yes",
        help_text="Whether to show the line-item breakdown after calculation.",
    )
    cta_text = CharBlock(
        required=False,
        default="Place Order",
        max_length=60,
        help_text="CTA button label.",
    )
    cta_url = CharBlock(
        required=False,
        default="/auth/register",
        max_length=255,
        help_text="Where the CTA sends the user (default: registration).",
    )

    class Meta:
        icon = "calculator"
        label = "Pricing Calculator"
        template = None  # Rendered entirely client-side by Vue


BLOG_BLOCKS = StreamBlock([
    ("key_takeaways", KeyTakeawaysBlock()),
    ("toc", TableOfContentsBlock()),
    ("heading", HeadingBlock()),
    ("paragraph", ParagraphBlock()),
    ("image", ImageBlock()),
    ("list", ListBlock_()),
    ("checklist", ChecklistBlock()),
    ("quote", QuoteBlock()),
    ("callout", CalloutBlock()),
    ("stats_highlight", StatsHighlightBlock()),
    ("before_after", BeforeAfterBlock()),
    ("sample_excerpt", SampleExcerptBlock()),
    ("definition", DefinitionBlock()),
    ("timeline", TimelineBlock()),
    ("author_review", AuthorReviewBadgeBlock()),
    ("disclaimer", DisclaimerBlock()),
    ("faq", FAQItemBlock()),
    ("cta", CTABlock()),
    ("internal_link", InternalLinkCardBlock()),
    ("attachment", AttachmentReferenceBlock()),
    ("table", TableDataBlock()),
    ("chart", ChartBlock()),
    ("embed", EmbedBlock()),
    ("divider", DividerBlock()),
    ("video", VideoEmbedBlock()),
    ("calculator", CalculatorBlock()),
    ("sources", SourcesListBlock()),
    ("related_posts", RelatedPostsBlock()),
    ("code", CodeBlock()),
])

SERVICE_PAGE_BLOCKS = StreamBlock([
    ("hero", HeroBlock()),
    ("trust_strip", TrustStripBlock()),
    ("heading", HeadingBlock()),
    ("paragraph", ParagraphBlock()),
    ("image", ImageBlock()),
    ("list", ListBlock_()),
    ("checklist", ChecklistBlock()),
    ("feature_grid", FeatureGridBlock()),
    ("how_it_works", HowItWorksBlock()),
    ("stats_highlight", StatsHighlightBlock()),
    ("before_after", BeforeAfterBlock()),
    ("definition", DefinitionBlock()),
    ("timeline", TimelineBlock()),
    ("pricing_table", PricingTableBlock()),
    ("comparison_table", ComparisonTableBlock()),
    ("testimonials", TestimonialGroupBlock()),
    ("guarantees", GuaranteesBlock()),
    ("author_review", AuthorReviewBadgeBlock()),
    ("disclaimer", DisclaimerBlock()),
    ("faq", FAQItemBlock()),
    ("cta", CTABlock()),
    ("table", TableDataBlock()),
    ("chart", ChartBlock()),
    ("embed", EmbedBlock()),
    ("attachment", AttachmentReferenceBlock()),
    ("internal_link", InternalLinkCardBlock()),
    ("calculator", CalculatorBlock()),
    ("divider", DividerBlock()),
])