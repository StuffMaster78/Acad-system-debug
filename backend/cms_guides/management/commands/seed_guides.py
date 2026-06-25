"""
Seed GuideIndexPage + onboarding GuideArticlePage for every active site.

Usage:
    python manage.py seed_guides                    # all sites
    python manage.py seed_guides --site gradecrest.com
    python manage.py seed_guides --update           # overwrite existing content
"""
from django.core.management.base import BaseCommand
from wagtail.models import Site

from cms_guides.models import GuideAudience, GuideArticlePage, GuideIndexPage


# ── Onboarding articles ───────────────────────────────────────────────────────
# Each entry: (slug, title, audience, icon, summary, body_html, is_featured)
GUIDES = [
    # ── STAFF / ADMIN ──────────────────────────────────────────────────────
    (
        "superadmin-system-overview",
        "System Overview — Superadmin Handover",
        GuideAudience.STAFF,
        "shield-check",
        "A complete map of the platform: tenants, portals, permissions, payment flows, and the CMS.",
        True,
        """<h2>What you manage</h2>
<p>As superadmin you have cross-tenant visibility. Every website (GradeCrest, EssayManiacs, NurseMyGrade, ResearchPaperMate) runs as a separate tenant sharing one Django backend, one Celery worker, and one Wagtail CMS.</p>

<h2>Portals</h2>
<ul>
  <li><strong>Client portal</strong> — <code>app.[site].com</code> — clients place and track orders.</li>
  <li><strong>Writer portal</strong> — <code>app.writerscreek.com</code> — writers bid, write, and get paid.</li>
  <li><strong>Staff portal</strong> — <code>admin.writerscreek.com</code> — your primary admin surface.</li>
</ul>

<h2>Key admin surfaces</h2>
<ul>
  <li><strong>Django admin</strong> — <code>/admin/</code> — raw model access, migrations, permissions.</li>
  <li><strong>Wagtail CMS</strong> — <code>/cms-admin/</code> — all public content: blog posts, service pages, guides, resources.</li>
  <li><strong>Staff portal</strong> — financial centre, analytics, loyalty, access control, exit popup management.</li>
</ul>

<h2>Payment flow</h2>
<p>All payments go through <strong>OrderBridge Payments</strong> (a single Stripe account). Clients see OrderBridge on their bank statement. Webhooks arrive at <code>POST /api/payments/webhooks/stripe/</code> and are processed asynchronously by Celery. See <code>PAYMENT_ARCHITECTURE.md</code> at the repo root for a full walkthrough.</p>

<h2>Tenant onboarding checklist</h2>
<ol>
  <li>Create <code>Website</code> record in Django admin — set <code>domain</code> and <code>portal_url</code>.</li>
  <li>Run <code>seed_[site]</code> management command to create branding, portal definition, and Wagtail site.</li>
  <li>Create <code>GuideIndexPage</code> under the site root: run <code>python manage.py seed_guides --site [hostname]</code>.</li>
  <li>Set Stripe webhook in OrderBridge Stripe dashboard to point to your Django domain.</li>
  <li>Configure nginx and issue SSL via certbot.</li>
</ol>

<h2>Background workers</h2>
<p>Celery (worker + beat) runs via Docker Compose. Beat handles scheduled tasks (nightly analytics, compensation events). Monitor via Django admin → Celery results, or Flower at port 5555 if enabled.</p>""",
    ),
    (
        "admin-daily-operations",
        "Admin Daily Operations Guide",
        GuideAudience.STAFF,
        "settings",
        "Order queue management, writer assignment, escalations, and quality workflows.",
        True,
        """<h2>Starting your day</h2>
<ol>
  <li>Check the <strong>Order queue</strong> — filter by status <em>Pending assignment</em>. Assign urgent orders first.</li>
  <li>Review <strong>Escalations</strong> — any order flagged by support or a client needs a decision within 2 hours.</li>
  <li>Check <strong>Disputes</strong> — active disputes block writer payout until resolved.</li>
</ol>

<h2>Assigning orders</h2>
<p>Open the order detail → <em>Assign writer</em>. The system suggests writers by subject match and availability. If no match, post to the <strong>open bid pool</strong> via the order actions menu.</p>

<h2>Writer management</h2>
<ul>
  <li><strong>Applications</strong> — review pending applications under Writer Management → Applications.</li>
  <li><strong>Vetting quiz</strong> — writers must pass the subject quiz before activation.</li>
  <li><strong>Fines</strong> — issue fines for late delivery or quality failures via the writer profile.</li>
  <li><strong>Compensation</strong> — manual compensation adjustments go through the Compensation view.</li>
</ul>

<h2>Quality control</h2>
<p>Every delivered order can be flagged for QA review. QA passes unlock the file for the client. QA failures return the order to the writer with a revision request.</p>

<h2>End of day</h2>
<ul>
  <li>Confirm all today's deadline orders are delivered or have a valid extension.</li>
  <li>Process any pending refund requests (Refunds → Pending).</li>
  <li>Check the <strong>Financial centre</strong> for any failed payment applications.</li>
</ul>""",
    ),
    (
        "editor-content-management",
        "Editor — Content & CMS Guide",
        GuideAudience.STAFF,
        "file-text",
        "How to create, edit, and publish blog posts, service pages, and guides in Wagtail.",
        False,
        """<h2>Accessing the CMS</h2>
<p>Go to <code>/cms-admin/</code> and log in with your editor credentials. You will land on the Wagtail explorer showing the page tree for your assigned site.</p>

<h2>Blog posts</h2>
<ol>
  <li>Navigate to <strong>Blog</strong> under your site root.</li>
  <li>Click <em>Add child page → Blog post</em>.</li>
  <li>Fill in the title, excerpt, category, tags, and author.</li>
  <li>Build the body using blocks: paragraphs, headings, key takeaways, lists, CTAs, tables, images.</li>
  <li>Set <strong>SEO title</strong> and <strong>Search description</strong> in the Promote tab.</li>
  <li>Schedule or publish immediately.</li>
</ol>

<h2>Service pages</h2>
<p>Service pages live under the <strong>Services</strong> index. Each page maps to a URL like <code>/services/essay-writing</code>. Use the FAQ block liberally — it improves on-page SEO.</p>

<h2>Guides (this system)</h2>
<p>Navigate to <strong>Guides</strong> under your site root. Add a <em>Guide article</em>. Set the <strong>Audience</strong> to target the correct portal role. Upload a PDF training document via the <em>PDF attachment</em> field (choose from Documents).</p>

<h2>Uploading images and documents</h2>
<ul>
  <li><strong>Images</strong> — Wagtail sidebar → Images. Upload then embed via the image block.</li>
  <li><strong>Documents / PDFs</strong> — Wagtail sidebar → Documents. Upload then select in the <em>PDF attachment</em> field on a guide.</li>
</ul>

<h2>Publishing checklist</h2>
<ul>
  <li>SEO title (50–60 chars) and meta description (150–160 chars) filled in.</li>
  <li>Canonical slug is clean (no trailing numbers or dates unless intentional).</li>
  <li>At least one internal CTA block pointing to the order page.</li>
  <li>Thumbnail image set for social sharing.</li>
</ul>""",
    ),
    # ── WRITER ─────────────────────────────────────────────────────────────
    (
        "writer-getting-started",
        "Getting Started as a Writer",
        GuideAudience.WRITER,
        "book-open",
        "Everything you need to know in your first week — bidding, writing, revisions, and getting paid.",
        True,
        """<h2>Your first steps</h2>
<ol>
  <li>Complete your <strong>writer profile</strong> — credentials, subjects, and a short bio. A complete profile gets more order matches.</li>
  <li>Pass the <strong>subject quiz</strong> for each discipline you want to take orders in.</li>
  <li>Add your <strong>payout details</strong> so compensation can be processed.</li>
</ol>

<h2>Bidding on orders</h2>
<p>The <strong>Marketplace</strong> shows open orders matching your subjects. Bid by setting your price and deadline. Keep your bid message professional — clients and admins both see it.</p>

<h2>Writing and delivering</h2>
<ul>
  <li>Start working only after the bid is <em>accepted</em>.</li>
  <li>Upload your work via the order's <strong>Deliver</strong> button before the deadline.</li>
  <li>Always upload in the format requested (DOCX, PDF, etc.).</li>
</ul>

<h2>Revisions</h2>
<p>If a client requests a revision, you have 48 hours to deliver the updated version. Revision scope must match the original instructions — new requirements are not included.</p>

<h2>Getting paid</h2>
<p>Compensation is processed bi-weekly. Your wallet shows your current balance and pending payouts. Fines for late delivery or quality issues are deducted automatically.</p>

<h2>Staying in good standing</h2>
<ul>
  <li>Deliver on time — lateness incurs fines and hurts your ranking.</li>
  <li>Maintain a quality score above 4.0 to keep access to premium-rate orders.</li>
  <li>Communicate proactively if you need an extension — always better than going silent.</li>
</ul>""",
    ),
    (
        "writer-earnings-levels",
        "Writer Levels & Earnings Guide",
        GuideAudience.WRITER,
        "credit-card",
        "How rates are set, how you level up, and how to maximise your earnings.",
        False,
        """<h2>Writer levels</h2>
<table>
  <tr><th>Level</th><th>Rate (per page)</th><th>Requirements</th></tr>
  <tr><td>Entry</td><td>$18–$22</td><td>Activated account, passed quiz</td></tr>
  <tr><td>Standard</td><td>$24–$28</td><td>20+ orders, 4.2+ quality score</td></tr>
  <tr><td>Senior</td><td>$30–$36</td><td>100+ orders, 4.5+ quality score, <5% revision rate</td></tr>
  <tr><td>Expert</td><td>$38–$45</td><td>300+ orders, 4.8+ quality score, postgrad credentials verified</td></tr>
</table>

<h2>Rush and difficulty bonuses</h2>
<p>Orders with tight deadlines (under 6 hours) or high academic levels (PhD) carry automatic rate bonuses on top of your base level rate.</p>

<h2>Tips</h2>
<p>Clients can tip after delivery. Tips are credited to your wallet immediately and are not subject to the bi-weekly cycle.</p>

<h2>Payout schedule</h2>
<p>Bi-weekly on the 1st and 15th of each month. Minimum payout is $20. Funds are transferred via your registered payout method within 2 business days.</p>""",
    ),
    # ── CLIENT ─────────────────────────────────────────────────────────────
    (
        "client-how-to-order",
        "How to Place and Manage Your Order",
        GuideAudience.CLIENT,
        "life-buoy",
        "Step-by-step guide to placing your first order, uploading files, and communicating with your writer.",
        True,
        """<h2>Placing your order</h2>
<ol>
  <li>Click <strong>New order</strong> from your dashboard.</li>
  <li>Select the service type, academic level, subject, and deadline.</li>
  <li>Upload your instructions, marking rubric, or any reference materials.</li>
  <li>Review the price and the payment disclosure, then complete payment.</li>
</ol>

<h2>After you pay</h2>
<p>An expert writer will be assigned within 30 minutes (for most orders). You can track progress in real time from your order detail page.</p>

<h2>Communicating with your writer</h2>
<p>Use the <strong>Messages</strong> tab on your order to send clarifications or additional files. Your writer will respond — please allow up to 2 hours during business hours.</p>

<h2>Receiving your work</h2>
<p>You will receive an email and an in-app notification when your work is delivered. Download it from the <strong>Files</strong> tab. Review it against your original instructions.</p>

<h2>Requesting a revision</h2>
<p>If the work needs changes, click <strong>Request revision</strong> and describe exactly what needs to be adjusted. Revisions are free within 14 days (30 days for dissertations) as long as your original instructions haven't changed.</p>

<h2>Refunds</h2>
<p>If we cannot deliver work that meets your requirements, you are entitled to a full or partial refund. Contact support via live chat or the Help section on your dashboard.</p>""",
    ),
]


class Command(BaseCommand):
    help = "Seed GuideIndexPage and onboarding GuideArticlePage for every site."

    def add_arguments(self, parser):
        parser.add_argument("--site", default=None, help="Restrict to a single site hostname.")
        parser.add_argument("--update", action="store_true", help="Overwrite existing guide content.")

    def handle(self, *_args, **options):
        site_filter = options.get("site")
        update = options["update"]

        sites = Site.objects.filter(hostname=site_filter) if site_filter \
                else Site.objects.all()

        for site in sites:
            self.stdout.write(f"\nSite: {site.hostname}")
            root = site.root_page

            # ── 1. GuideIndexPage ─────────────────────────────────────────
            index_qs = GuideIndexPage.objects.child_of(root).filter(slug="guides")
            if index_qs.exists():
                index_page = index_qs.first()
                self.stdout.write(f"  GuideIndexPage already exists (pk={index_page.pk})")
            else:
                index_page = GuideIndexPage(
                    title="Guides",
                    slug="guides",
                    depth=root.depth + 1,
                    path=root.path + "0001",
                )
                root.add_child(instance=index_page)
                index_page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  Created GuideIndexPage pk={index_page.pk}"))

            # ── 2. GuideArticlePage items ─────────────────────────────────
            for slug, title, audience, icon, summary, featured, body in GUIDES:
                existing = GuideArticlePage.objects.child_of(index_page).filter(slug=slug).first()

                if existing and not update:
                    self.stdout.write(f"  SKIP {slug!r} (already exists — use --update to overwrite)")
                    continue

                if existing:
                    page = existing
                    page.title = title
                    page.audience = audience
                    page.icon = icon
                    page.summary = summary
                    page.body = body
                    page.is_featured = featured
                    page.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS(f"  UPDATED {slug!r}"))
                else:
                    article = GuideArticlePage(
                        title=title,
                        slug=slug,
                        audience=audience,
                        icon=icon,
                        summary=summary,
                        body=body,
                        is_featured=featured,
                        estimated_read_minutes=5,
                    )
                    index_page.add_child(instance=article)
                    article.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS(f"  CREATED {slug!r}"))

        self.stdout.write(self.style.SUCCESS("\nDone."))
