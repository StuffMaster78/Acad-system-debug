"""
Seed GuideIndexPage + GuideArticlePage entries for every active site.

Usage:
    python manage.py seed_guides                    # all sites
    python manage.py seed_guides --site gradecrest.com
    python manage.py seed_guides --update           # overwrite existing content
"""
from django.core.management.base import BaseCommand
from wagtail.models import Site

from cms_guides.models import GuideAudience, GuideArticlePage, GuideIndexPage


# ── Guide definitions ─────────────────────────────────────────────────────────
# (slug, title, audience, icon, summary, is_featured, estimated_read_minutes, body_html)

GUIDES = [

    # =========================================================================
    # STAFF / ADMIN
    # =========================================================================

    (
        "superadmin-system-overview",
        "System Overview — Superadmin Handover",
        GuideAudience.STAFF,
        "shield-check",
        "A complete map of the platform: tenants, portals, permissions, payment flows, and the CMS.",
        True,
        8,
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
  <li><strong>Wagtail CMS</strong> — <code>/cms-admin/</code> — all public content: blog posts, service pages, guides.</li>
  <li><strong>Staff portal</strong> — financial centre, analytics, loyalty, access control.</li>
</ul>

<h2>Payment flow</h2>
<p>Each site processes payments through its own Stripe account. The statement descriptor (what appears on the client's bank statement) is set per site in <strong>Gateway config</strong>. Webhooks arrive at <code>POST /api/payments/webhooks/stripe/&lt;site-slug&gt;/</code> and are processed asynchronously by Celery.</p>

<h2>Tenant onboarding checklist</h2>
<ol>
  <li>Create <code>Website</code> record in Django admin — set <code>domain</code> and <code>root_url</code>.</li>
  <li>Run <code>python manage.py seed_guides --site [hostname]</code>.</li>
  <li>In Gateway config, set <code>secret_key_env_var</code> and <code>webhook_secret_env_var</code> to point at the site's Stripe env vars.</li>
  <li>Register the per-site webhook URL in the Stripe dashboard: <code>/api/payments/webhooks/stripe/[slug]/</code>.</li>
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
        6,
        """<h2>Starting your day</h2>
<ol>
  <li>Check the <strong>Order queue</strong> — filter by status <em>Pending assignment</em>. Assign urgent orders first.</li>
  <li>Review <strong>Escalations</strong> — any flagged order needs a decision within 2 hours.</li>
  <li>Check <strong>Disputes</strong> — active disputes block writer payout until resolved.</li>
  <li>Scan the <strong>Ops intelligence</strong> panel for overdue deliveries or stuck orders.</li>
</ol>

<h2>Assigning orders</h2>
<p>Open the order detail → <em>Staffing</em> tab → <em>Assign writer</em>. The system lists writers by subject match and availability. If no match, release to the <strong>open bid pool</strong> via the actions panel.</p>

<h2>Writer management</h2>
<ul>
  <li><strong>Applications</strong> — review pending applications under Writer Management → Applications.</li>
  <li><strong>Vetting quiz</strong> — writers must pass the subject quiz before activation.</li>
  <li><strong>Fines</strong> — issue fines for late delivery or quality failures via the writer profile.</li>
  <li><strong>Force status</strong> — in the order detail, expand <em>Force status override</em> to move a stuck order. All overrides are logged in the timeline.</li>
</ul>

<h2>Quality control</h2>
<p>Every delivered order can be sent for QA review. QA pass unlocks the file for the client. QA failure returns the order to the writer with a revision request.</p>

<h2>End of day</h2>
<ul>
  <li>Confirm all today's deadline orders are delivered or have an approved extension.</li>
  <li>Process pending refund requests: Payments → Refunds → Pending.</li>
  <li>Check the Financial centre for any failed payment applications.</li>
</ul>""",
    ),

    (
        "editor-content-management",
        "Editor — Content & CMS Guide",
        GuideAudience.STAFF,
        "file-text",
        "How to create, edit, and publish blog posts, service pages, and guides in Wagtail.",
        False,
        5,
        """<h2>Accessing the CMS</h2>
<p>Go to <code>/cms-admin/</code> and log in with your editor credentials. You will see the Wagtail page tree for your assigned site.</p>

<h2>Blog posts</h2>
<ol>
  <li>Navigate to <strong>Blog</strong> under your site root.</li>
  <li>Click <em>Add child page → Blog post</em>.</li>
  <li>Fill in title, excerpt, category, tags, and author.</li>
  <li>Build the body using blocks: paragraphs, headings, key takeaways, lists, CTAs, tables, images.</li>
  <li>Set <strong>SEO title</strong> and <strong>Search description</strong> in the Promote tab.</li>
  <li>Schedule or publish immediately.</li>
</ol>

<h2>Service pages</h2>
<p>Service pages live under the <strong>Services</strong> index. Each page maps to a flat URL like <code>/essay-writing</code>. Use the FAQ block liberally — it improves on-page SEO.</p>

<h2>Guides (this system)</h2>
<p>Navigate to <strong>Guides</strong> under your site root. Add a <em>Guide article</em>. Set the <strong>Audience</strong> to target the correct portal role. Upload a PDF via the <em>PDF attachment</em> field.</p>

<h2>Publishing checklist</h2>
<ul>
  <li>SEO title 50–60 chars; meta description 150–160 chars.</li>
  <li>Canonical slug is clean (no trailing numbers or dates unless intentional).</li>
  <li>At least one internal CTA block pointing to the order page.</li>
  <li>Thumbnail image set for social sharing.</li>
</ul>""",
    ),


    # =========================================================================
    # CLIENT GUIDES
    # =========================================================================

    (
        "client-how-to-order",
        "How to Place Your First Order",
        GuideAudience.CLIENT,
        "life-buoy",
        "Step-by-step guide to placing your first order, uploading files, and completing payment.",
        True,
        5,
        """<h2>Step 1 — Tell us what you need</h2>
<p>Click <strong>New order</strong> on your dashboard. You will go through a three-step wizard.</p>
<ul>
  <li>Choose your <strong>service type</strong>: Writing, Design, Presentation, Diagram, or a combination.</li>
  <li>Enter a clear <strong>topic</strong> (at least 3 characters).</li>
  <li>Paste or type your <strong>instructions</strong>. Include the marking rubric, preferred sources, and any specific requirements your instructor has given you. The more detail you provide, the better your result.</li>
</ul>

<h2>Step 2 — Specify the details</h2>
<ul>
  <li>Select your <strong>paper type</strong>, <strong>subject</strong>, <strong>academic level</strong>, and <strong>formatting style</strong> (APA, MLA, Chicago, etc.).</li>
  <li>Set the <strong>deadline</strong>. Allow extra time if you want to request revisions before your actual due date.</li>
  <li>Choose the number of <strong>pages</strong> and <strong>spacing</strong> (double-spaced is standard).</li>
  <li>Upload your <strong>reference materials</strong> — lecture notes, previous drafts, marking rubrics. Accepted formats: PDF, DOC, DOCX, images, ZIP.</li>
  <li>If you have worked with a writer before and want to request them again, enter their writer ID (format: W-XXXX) in the <em>Preferred writer</em> field.</li>
</ul>

<h2>Step 3 — Review price and pay</h2>
<ul>
  <li>Click <strong>Calculate price</strong> to see your total.</li>
  <li>If you have a <strong>discount code</strong>, enter it and click Apply.</li>
  <li>If you have funds in your <strong>wallet</strong>, they will be used automatically toward the total. The remainder is charged to your card.</li>
  <li>Read the <strong>payment disclosure</strong> — this tells you what will appear on your bank statement.</li>
  <li>Click <strong>Submit order</strong>.</li>
</ul>

<h2>What happens next</h2>
<p>After payment, your order moves to <em>Placed</em> status. A writer will normally be assigned within 30 minutes. You will receive an email and in-app notification when someone is assigned and again when your work is delivered.</p>

<blockquote>Tip: The sooner you place your order, the more time your writer has — and the better the result.</blockquote>""",
    ),

    (
        "client-order-statuses",
        "Understanding Your Order Status",
        GuideAudience.CLIENT,
        "help-circle",
        "What each order status means, what you should do at each stage, and how long things take.",
        False,
        4,
        """<h2>Status overview</h2>
<p>Every order moves through a series of statuses visible on your dashboard and order detail page. Here is what each one means.</p>

<h2>Placed / Pending assignment</h2>
<p>Your payment was received and your order is in the queue. A writer will be assigned shortly. No action needed from you.</p>

<h2>In progress</h2>
<p>A writer has accepted your order and is actively working on it. This is the longest stage — relax and wait. You can send additional notes via the <strong>Messages</strong> tab if needed.</p>

<h2>Under editing</h2>
<p>Your work is with our editorial team for quality review before delivery. No action needed.</p>

<h2>Awaiting your approval / Submitted</h2>
<p>Your work is ready. You should:</p>
<ol>
  <li>Download the file from the <strong>Files</strong> tab.</li>
  <li>Read it carefully against your original instructions.</li>
  <li>Either click <strong>Approve</strong> (if you are satisfied) or <strong>Request revision</strong> (if changes are needed).</li>
</ol>
<p>You have 3 days to respond. If you do not act, the order auto-approves.</p>

<h2>Revision requested / On revision</h2>
<p>You asked for changes and the writer is working on them. The revised version will be re-submitted for your approval.</p>

<h2>Completed / Approved</h2>
<p>You approved the work. The order is complete. You can still leave a <strong>rating and review</strong> from the order detail page — this helps other clients and helps us recognise great writers.</p>

<h2>Cancelled / Refunded</h2>
<p>The order was cancelled. If a refund is due, it will appear in your wallet or on your original payment method within 5–10 business days depending on your bank.</p>

<h2>Payment statuses</h2>
<ul>
  <li><strong>Unpaid</strong> — payment has not been received. Your order will not be assigned until you pay.</li>
  <li><strong>Paid</strong> — fully paid. No action needed.</li>
  <li><strong>Partially paid</strong> — you are on an installment plan. Future payments are due on the dates shown in the Billing tab.</li>
</ul>""",
    ),

    (
        "client-revisions-and-disputes",
        "Requesting Revisions & Raising Disputes",
        GuideAudience.CLIENT,
        "message-square",
        "How to request changes to your work, when to raise a dispute, and what to expect from each process.",
        False,
        5,
        """<h2>Requesting a revision</h2>
<p>Revisions are free as long as your original instructions have not changed. To request one:</p>
<ol>
  <li>Open your order and click <strong>Request revision</strong>.</li>
  <li>Describe exactly what needs to change — be specific. Instead of "fix the essay", say "the thesis statement in paragraph 1 does not address the prompt; please rewrite it to argue that…"</li>
  <li>Attach any additional reference material if needed.</li>
</ol>
<p>The writer has <strong>48 hours</strong> to deliver the revised version. You can request unlimited revisions within the revision window (14 days for standard papers, 30 days for dissertations), provided the scope stays within your original instructions.</p>

<h2>What is not covered by free revisions</h2>
<ul>
  <li>Adding pages or sections that were not in the original brief.</li>
  <li>Changing the topic, argument, or focus entirely.</li>
  <li>Changing the formatting style after delivery (e.g., switching from APA to MLA).</li>
</ul>
<p>If you need additional work beyond the original scope, <strong>place a new order</strong> or contact support to discuss options.</p>

<h2>Raising a dispute</h2>
<p>If revisions have not resolved a quality issue, or if you believe there has been a serious failure to meet your instructions, you can raise a dispute.</p>
<ol>
  <li>Go to <strong>Disputes</strong> in the sidebar.</li>
  <li>Click <strong>Raise dispute</strong>.</li>
  <li>Enter the order ID and explain the issue clearly.</li>
</ol>
<p>Our support team reviews disputes within <strong>24 hours</strong>. We may ask for additional information. Possible outcomes:</p>
<ul>
  <li><strong>Full or partial refund</strong> — credited to your wallet or original payment method.</li>
  <li><strong>Additional revision</strong> — the order is returned to the writer with specific instructions.</li>
  <li><strong>Resolved in writer's favour</strong> — if the work meets the original brief and the dispute is not supported by evidence.</li>
</ul>
<p>You can withdraw a dispute at any time if the issue is resolved directly.</p>

<h2>Tips for the best outcome</h2>
<ul>
  <li>Keep all communication in the order message thread — this is your evidence trail.</li>
  <li>Be specific: page numbers, paragraphs, exact errors.</li>
  <li>Use the revision process first before escalating to a dispute.</li>
</ul>""",
    ),

    (
        "client-wallet-and-billing",
        "Your Wallet, Payments & Billing",
        GuideAudience.CLIENT,
        "credit-card",
        "How your wallet works, how to top it up, how installments work, and how to read your receipts.",
        False,
        5,
        """<h2>Your wallet</h2>
<p>Your wallet is a prepaid balance you can use to pay for orders. It is faster than re-entering card details each time and can store refunds or discount credits.</p>
<ul>
  <li><strong>Available balance</strong> — funds you can spend immediately.</li>
  <li><strong>Pending balance</strong> — funds reserved for an active order checkout. They will return to available if the checkout is abandoned.</li>
</ul>

<h2>Topping up your wallet</h2>
<ol>
  <li>Go to <strong>Billing → Wallet</strong>.</li>
  <li>Select a preset amount ($10, $25, $50, $100, $200) or enter a custom amount.</li>
  <li>Click <strong>Top up</strong> — you will be redirected to the secure Stripe checkout.</li>
  <li>After payment, your wallet balance updates within a few seconds.</li>
</ol>
<p>What appears on your bank statement is the payment processor name configured for this site (shown on the payment screen before you confirm).</p>

<h2>Paying for orders with your wallet</h2>
<p>If your wallet balance covers the full order price, no card is needed. If your balance is lower than the order price, the wallet covers part of it and the remainder is charged to your card in a single transaction — you will see the split clearly on the checkout screen.</p>

<h2>Invoices and installments</h2>
<p>For classes and large projects, payment may be split into installments. You can see and pay each installment from <strong>Billing → Invoices</strong>.</p>
<ul>
  <li>Click on an invoice to expand it and see each installment due date and amount.</li>
  <li>Click <strong>Pay by card</strong> to pay via Stripe, or <strong>Pay from wallet</strong> to use your wallet balance instantly.</li>
  <li>Overdue installments are highlighted in amber — please pay promptly to keep your access.</li>
</ul>

<h2>Receipts</h2>
<p>Every successful payment generates a receipt viewable in <strong>Billing → Receipts</strong>. Receipts show the processor name, payment reference, amount, and currency — useful for reimbursement or record-keeping.</p>

<h2>Refunds</h2>
<p>Approved refunds are processed by our team and go either to your wallet (instant) or to your original payment method (5–10 business days depending on your bank).</p>""",
    ),

    (
        "client-special-orders",
        "Special Orders & Custom Quotes",
        GuideAudience.CLIENT,
        "file-text",
        "For complex, long-form, or non-standard projects that need a custom quote and milestone-based delivery.",
        False,
        5,
        """<h2>What is a special order?</h2>
<p>Special orders are for work that does not fit the standard per-page pricing model — dissertations, research projects, ongoing writing packages, or anything with multiple deliverable stages (milestones). You submit a brief, we quote a price, and delivery is structured around agreed milestones.</p>

<h2>How to submit a special order request</h2>
<ol>
  <li>From your dashboard or the <strong>Special Orders</strong> page, click <strong>Custom quote</strong>.</li>
  <li>Describe your project in detail: subject area, total scope, deadline, and any milestone structure you have in mind.</li>
  <li>Upload any reference materials, chapter outlines, or style guides.</li>
  <li>Submit the inquiry.</li>
</ol>

<h2>The quote process</h2>
<p>After you submit, your request moves to <em>Quote pending</em>. Our team reviews the scope and sends back a detailed quote within 24 hours. The quote includes:</p>
<ul>
  <li>Total price and milestone breakdown.</li>
  <li>Estimated delivery dates for each milestone.</li>
  <li>Payment schedule (partial upfront, remainder on delivery, or milestone-by-milestone).</li>
</ul>
<p>You can <strong>accept the quote</strong> as-is or start a negotiation if you need adjustments to scope, price, or deadline. Once accepted, payment is required to begin.</p>

<h2>Milestone delivery</h2>
<p>Each milestone has its own delivery date and approval step. When a milestone is delivered, you review it and either approve it or request a revision — just like a standard order. The next milestone begins only after the previous one is approved.</p>

<h2>Express orders</h2>
<p>For faster turnaround on a special project, click <strong>Express order</strong> — this flags the inquiry as high priority and we aim to quote within 4 hours.</p>""",
    ),

    (
        "client-class-help",
        "Getting Class Help — How It Works",
        GuideAudience.CLIENT,
        "book-open",
        "Everything you need to know about the class help service — tasks, installments, portal access, and grades.",
        False,
        6,
        """<h2>What is class help?</h2>
<p>The class help service assigns an expert to assist with an entire course over a semester. Rather than placing individual orders per assignment, you provide the class details once and your expert handles each task (discussions, essays, quizzes, labs) throughout the semester.</p>

<h2>How to request class help</h2>
<ol>
  <li>Go to <strong>Classes</strong> and click <strong>New class</strong>.</li>
  <li>Enter the class name, subject, academic level, and the semester start and end dates.</li>
  <li>Upload your syllabus, course outline, and any login credentials for the course platform if required.</li>
  <li>Submit the request.</li>
</ol>
<p>Our team reviews your submission, proposes a price, and may ask clarifying questions before accepting. Once you accept and pay the deposit, an expert is assigned.</p>

<h2>Tasks</h2>
<p>Each assignment within the class is created as a <strong>task</strong>. From your class detail page (<strong>Tasks</strong> tab) you can see:</p>
<ul>
  <li>The task title and description.</li>
  <li>The due date.</li>
  <li>The current status (pending, in progress, submitted, graded).</li>
  <li>The grade and feedback once the assignment has been returned by your instructor.</li>
</ul>
<p>Add any specific instructions or files for a task by messaging through the class communication thread.</p>

<h2>Installment payments</h2>
<p>Class help is typically paid in installments — for example, 30% upfront, 40% at midterm, 30% at completion. Your payment schedule is shown in the <strong>Installments</strong> tab. Pay each installment on or before the due date to keep the class running without interruption.</p>

<h2>Portal access</h2>
<p>If your course requires direct login access (e.g., a Canvas or Blackboard account), you can share credentials securely through the <strong>Portal Access</strong> tab. These are encrypted and visible only to your assigned expert and our admin team. Never share credentials via email or chat outside the platform.</p>

<h2>Grades and feedback</h2>
<p>Once your instructor grades an assignment, update the task with the grade so we can track progress and performance. You can enter the grade in the task's detail view. If a grade is lower than expected, discuss it with our team — we will advise whether a re-submission or appeal is appropriate.</p>""",
    ),

    (
        "client-account-security",
        "Keeping Your Account Secure",
        GuideAudience.CLIENT,
        "shield-check",
        "Two-factor authentication, active sessions, security events, and what to do if you suspect unauthorised access.",
        False,
        4,
        """<h2>Two-factor authentication (2FA)</h2>
<p>We strongly recommend enabling 2FA on your account. With 2FA, even if someone gets your password, they cannot log in without also having your phone.</p>
<ol>
  <li>Go to <strong>Account</strong> in the sidebar.</li>
  <li>Scroll to <strong>Two-factor authentication</strong>.</li>
  <li>Click <strong>Add authenticator app</strong> and scan the QR code with Google Authenticator, Authy, or 1Password.</li>
  <li>Enter the 6-digit code shown in the app to confirm the link.</li>
</ol>
<p>Also generate <strong>backup codes</strong> from the same section and store them somewhere safe (offline). These are one-time codes you can use if you lose access to your phone.</p>

<h2>Managing active sessions</h2>
<p>Your account shows all devices currently signed in. Go to <strong>Account → Active sessions</strong> to see each device, its IP address, and when it last used your account.</p>
<ul>
  <li>If you see a device you do not recognise, click the revoke button next to it.</li>
  <li>To sign out of all other devices at once, click <strong>Sign out all other sessions</strong>.</li>
</ul>

<h2>Security activity log</h2>
<p>The <strong>Security activity</strong> section on your Account page shows recent events — logins, password changes, new devices. Review this periodically. If you see activity you did not initiate, change your password immediately and contact support.</p>

<h2>Password best practices</h2>
<ul>
  <li>Use a unique password you do not use on other sites.</li>
  <li>At least 12 characters, mixing letters, numbers, and symbols.</li>
  <li>Change your password from <strong>Account → Change password</strong> if you suspect it has been compromised.</li>
</ul>

<h2>If you suspect unauthorised access</h2>
<ol>
  <li>Change your password immediately.</li>
  <li>Revoke all active sessions.</li>
  <li>Contact support — we can lock your account, review access logs, and help you recover.</li>
</ol>""",
    ),

    (
        "client-loyalty-and-referrals",
        "Loyalty Points & Referrals",
        GuideAudience.CLIENT,
        "users",
        "How to earn and spend loyalty points, what each tier unlocks, and how to refer friends.",
        False,
        3,
        """<h2>Earning points</h2>
<p>You earn loyalty points on every completed order. The exact rate is shown on your <strong>Loyalty</strong> page. Points are also awarded for:</p>
<ul>
  <li>Leaving a verified review after order completion.</li>
  <li>Referring a friend who places their first order (see below).</li>
  <li>Promotional events announced via email or dashboard banner.</li>
</ul>

<h2>Tiers</h2>
<p>Your tier is determined by your total lifetime points. Higher tiers unlock better conversion rates (points → wallet credit) and access to discounts. Your current tier and points balance are shown on the <strong>Loyalty</strong> card on your dashboard.</p>

<h2>Converting points to wallet credit</h2>
<ol>
  <li>Go to <strong>Billing → Loyalty</strong> (or use the wallet tab).</li>
  <li>Under <strong>Convert to credits</strong>, enter the number of points you want to convert.</li>
  <li>Click <strong>Convert</strong>. The equivalent dollar amount is immediately added to your wallet.</li>
</ol>

<h2>Redeeming rewards</h2>
<p>The <strong>Redeem rewards</strong> tab shows the available reward catalogue — discount vouchers, premium service upgrades, and more. Each reward shows the points required. Click <strong>Redeem</strong> if you have enough points.</p>

<h2>Referring friends</h2>
<ol>
  <li>Go to <strong>Billing → Referral</strong>.</li>
  <li>Copy your unique referral code and share it with a friend.</li>
  <li>When they sign up using your code and complete their first order, you both receive bonus points.</li>
</ol>""",
    ),


    # =========================================================================
    # WRITER GUIDES
    # =========================================================================

    (
        "writer-getting-started",
        "Getting Started as a Writer",
        GuideAudience.WRITER,
        "book-open",
        "Your first week on the platform — completing your profile, passing the quiz, picking up your first order, and getting paid.",
        True,
        6,
        """<h2>Before you can take orders</h2>
<p>New writers must complete three things before the order pool becomes visible:</p>
<ol>
  <li><strong>Complete your profile</strong> — go to <strong>Account</strong> and fill in your display name, bio, and subjects. A complete profile with clear credentials gets matched to more orders.</li>
  <li><strong>Pass the subject quiz</strong> — each discipline has a short vetting quiz. Go to <strong>Vetting</strong> in the sidebar. You must score above the pass threshold for each subject before you can take orders in that area.</li>
  <li><strong>Set your payout details</strong> — earnings can only be disbursed to a registered payout method. Set this up from your <strong>Earnings</strong> page before your first payout cycle.</li>
</ol>

<h2>Your first order</h2>
<ol>
  <li>Go to <strong>Marketplace</strong> — this shows open orders you are eligible to bid on.</li>
  <li>Browse by subject, deadline, or academic level. Urgent orders have an amber badge.</li>
  <li>Open an order to read the full brief, then click <strong>Bid</strong>.</li>
  <li>Enter your proposed price, delivery time, and a short professional message explaining why you are a good fit.</li>
  <li>Once your bid is accepted, the order moves to your <strong>Assignments</strong>.</li>
</ol>

<h2>Delivering your work</h2>
<ul>
  <li>Open the order from <strong>Assignments</strong>.</li>
  <li>Upload your completed work using the <strong>Deliver</strong> button before the deadline shown.</li>
  <li>Submit in the file format specified in the brief (usually DOCX).</li>
  <li>Add a brief delivery note explaining what you have done — clients appreciate the context.</li>
</ul>

<h2>Getting paid</h2>
<p>Earnings appear in your wallet after each completed order is approved by the client or auto-approved (3 days after delivery). Payouts process on your chosen cycle (bi-weekly or monthly). See the <strong>Earnings &amp; Levels</strong> guide for details.</p>

<h2>Staying in good standing</h2>
<ul>
  <li><strong>Deliver on time.</strong> Late delivery incurs fines and affects your level progression.</li>
  <li><strong>Communicate early.</strong> If you need more time or have a question, message the order thread — do not go silent.</li>
  <li><strong>Maintain quality.</strong> A rating below 4.0 restricts access to higher-paying orders.</li>
</ul>""",
    ),

    (
        "writer-bidding-guide",
        "How to Win Orders — The Bidding Pool",
        GuideAudience.WRITER,
        "users",
        "How the marketplace works, how to write a winning bid, and what happens after you bid.",
        False,
        4,
        """<h2>How the marketplace works</h2>
<p>The <strong>Marketplace</strong> (Available orders) shows orders that are open for bids. Orders are listed with:</p>
<ul>
  <li>Order ID, topic, and academic level.</li>
  <li>Subject, paper type, pages, deadline, and citation style.</li>
  <li>Compensation (if pre-set) or blank if the admin will negotiate.</li>
</ul>
<p>Not all orders are in the open pool — some are assigned directly by admins, and some are sent as <strong>preferred writer invitations</strong> (shown as a highlighted section on your dashboard).</p>

<h2>Writing a winning bid</h2>
<p>Your bid message is read by both the admin and sometimes the client. Keep it:</p>
<ul>
  <li><strong>Relevant</strong> — mention your specific experience with the subject or paper type.</li>
  <li><strong>Confident but not generic</strong> — avoid "I am a professional writer who can help you." Say what specifically makes you the right fit.</li>
  <li><strong>Realistic</strong> — do not underbid just to win if you cannot deliver quality at that price.</li>
</ul>

<h2>Setting your price and delivery time</h2>
<ul>
  <li>Price is per order (not per page at the bid stage). Factor in the page count, academic level, and research required.</li>
  <li>Delivery time is in hours from now. Be conservative — you can always deliver early, but delivering late has consequences.</li>
</ul>

<h2>After you bid</h2>
<p>Your bids are visible in <strong>Bids</strong>. Status options:</p>
<ul>
  <li><strong>Pending</strong> — the admin has not acted yet. You can withdraw a pending bid if you change your mind.</li>
  <li><strong>Accepted</strong> — you have been assigned. The order now appears in Assignments.</li>
  <li><strong>Rejected / Expired</strong> — the order was assigned to another writer or expired. This does not affect your standing.</li>
</ul>

<h2>Preferred writer invitations</h2>
<p>If a client has worked with you before and requests you by ID, you will see an invitation on your dashboard. These take priority — respond promptly.</p>""",
    ),

    (
        "writer-quality-and-delivery",
        "Delivering Quality Work — Standards & Checklist",
        GuideAudience.WRITER,
        "file-text",
        "What we expect from every delivery: quality standards, formatting, file requirements, and the pre-submission checklist.",
        True,
        5,
        """<h2>Before you start writing</h2>
<ul>
  <li>Read the full brief at least twice.</li>
  <li>Note the exact word/page count, deadline, formatting style, and any specific instructions.</li>
  <li>Download and read any attached rubrics, previous papers, or style guides the client uploaded.</li>
  <li>If anything is unclear, message the order thread immediately — do not wait until you are halfway through.</li>
</ul>

<h2>While writing</h2>
<ul>
  <li>Follow the formatting style exactly (APA, MLA, Chicago, Harvard, etc.) — font, margins, heading levels, references.</li>
  <li>Write to the academic level specified. A PhD-level paper requires primary sources and original analysis; a high-school essay requires clear structure and accessible language.</li>
  <li>All sources must be real and properly cited. Fabricated citations are grounds for immediate account suspension.</li>
  <li>Do not copy content from online sources without proper citation. All work is screened for plagiarism.</li>
</ul>

<h2>Pre-submission checklist</h2>
<p>Before you click <strong>Deliver</strong>, verify all of the following:</p>
<ol>
  <li>Word/page count meets or slightly exceeds the requirement.</li>
  <li>Formatting style is consistent throughout (heading levels, citation format, reference list).</li>
  <li>Your name, the platform name, or any internal notes are not in the document.</li>
  <li>File is saved in the correct format (usually DOCX; PDF only if specifically requested).</li>
  <li>Run a spell-check and grammar pass.</li>
  <li>All sources cited in-text appear in the reference list and vice versa.</li>
  <li>The work addresses the actual question or prompt, not a paraphrase of it.</li>
</ol>

<h2>File format requirements</h2>
<ul>
  <li><strong>Written papers</strong> — DOCX preferred. PDF only if requested.</li>
  <li><strong>Presentations</strong> — PPTX.</li>
  <li><strong>Diagrams</strong> — PNG or PDF (editable source file where possible).</li>
  <li><strong>Design work</strong> — PDF plus source file (PSD, AI, Figma export).</li>
</ul>

<h2>Delivery note</h2>
<p>Always include a short delivery note (2–4 sentences) explaining:</p>
<ul>
  <li>What approach you took and why.</li>
  <li>Any assumptions you made due to ambiguity in the brief.</li>
  <li>Any areas where the client may want to personalise further.</li>
</ul>
<p>This reduces revision requests and demonstrates professionalism.</p>""",
    ),

    (
        "writer-revisions",
        "Handling Revision Requests",
        GuideAudience.WRITER,
        "message-square",
        "What to do when a client requests a revision — what is in scope, how to respond, and how to avoid repeat revisions.",
        False,
        4,
        """<h2>What triggers a revision request</h2>
<p>A client clicks <strong>Request revision</strong> instead of <strong>Approve</strong>. You will receive a notification and the order moves back to <em>Revision requested</em> status in your Assignments.</p>

<h2>Reading the revision request</h2>
<p>Open the order and read the revision note carefully. Common revision categories:</p>
<ul>
  <li><strong>Genuine scope corrections</strong> — you missed something clearly in the original brief. Fix it thoroughly.</li>
  <li><strong>Clarification requests</strong> — the client wants more depth on a specific section. Expand without padding.</li>
  <li><strong>Formatting issues</strong> — wrong citation style, incorrect margins, etc. These are quick fixes.</li>
  <li><strong>Out-of-scope requests</strong> — the client is asking for something not in the original brief (a new chapter, a different topic). Do not add this without admin approval. Message the thread and flag it to the admin team.</li>
</ul>

<h2>Responding to a revision</h2>
<ol>
  <li>Acknowledge the request in the order message thread within 2 hours.</li>
  <li>Make the requested changes carefully — do not rush.</li>
  <li>Deliver the revised version using the <strong>Deliver</strong> button, noting what you changed in your delivery note.</li>
  <li>You have <strong>48 hours</strong> from when the revision was requested.</li>
</ol>

<h2>If you disagree with the revision request</h2>
<p>If you believe the original work fully meets the brief, explain your reasoning professionally in the message thread. Do not refuse to engage. The admin team may review the case and make a final decision. Avoid confrontational language — it never helps.</p>

<h2>Avoiding repeat revisions</h2>
<ul>
  <li>Address every point in the brief, not just the obvious ones.</li>
  <li>Ask questions before starting if the brief is unclear.</li>
  <li>Deliver slightly more than asked (an extra well-cited source, a stronger conclusion) — it leaves less room for dissatisfaction.</li>
  <li>Follow the pre-submission checklist before every delivery.</li>
</ul>""",
    ),

    (
        "writer-earnings-levels",
        "Earnings, Levels, Fines & Payout Cycles",
        GuideAudience.WRITER,
        "credit-card",
        "How your pay rate is determined, how to level up, what fines exist, and when and how you get paid.",
        False,
        6,
        """<h2>Writer levels and rates</h2>
<p>Your base rate per page depends on your writer level. Levels advance automatically when you meet the thresholds:</p>
<table>
  <tr><th>Level</th><th>Rate range (per page)</th><th>Requirements</th></tr>
  <tr><td>Entry</td><td>$18 – $22</td><td>Activated account, passed quiz</td></tr>
  <tr><td>Standard</td><td>$24 – $28</td><td>20+ completed orders, 4.2+ quality score</td></tr>
  <tr><td>Senior</td><td>$30 – $36</td><td>100+ completed orders, 4.5+ quality score, &lt;5% revision rate</td></tr>
  <tr><td>Expert</td><td>$38 – $45</td><td>300+ completed orders, 4.8+ quality score, postgraduate credentials verified</td></tr>
</table>
<p>Your current level and progress toward the next level are shown on the <strong>Writer level</strong> card on your workspace.</p>

<h2>Bonuses and extras</h2>
<ul>
  <li><strong>Rush bonus</strong> — orders with a deadline under 6 hours from placement carry an automatic rate bonus.</li>
  <li><strong>Difficulty bonus</strong> — PhD-level or high-complexity orders carry an additional uplift.</li>
  <li><strong>Tips</strong> — clients can tip after delivery. Tips are credited to your wallet immediately, outside the normal payout cycle.</li>
  <li><strong>Performance bonuses</strong> — issued manually by the admin team for exceptional work or high-volume months.</li>
</ul>

<h2>Fines</h2>
<p>Fines are deducted from your wallet balance. You will receive a notification when a fine is issued. Common fine types:</p>
<ul>
  <li><strong>Late delivery</strong> — charged if you deliver after the agreed deadline without an approved extension.</li>
  <li><strong>Quality failure</strong> — charged when a QA review identifies a serious quality issue.</li>
  <li><strong>Policy violation</strong> — charged for breaches of writer conduct guidelines.</li>
</ul>
<p>If you believe a fine was issued in error, click <strong>Dispute</strong> on the fine card and explain your case. You can also dispute from the <strong>Fines</strong> page in the sidebar. The admin team reviews disputes within 48 hours.</p>

<h2>Advances</h2>
<p>If you need funds before your next payout cycle, you can request an advance from the <strong>Earnings</strong> page. Advances are subject to approval and are deducted from your next payout.</p>

<h2>Payout cycles</h2>
<ul>
  <li><strong>Bi-weekly</strong> — paid on the 1st and 15th of each month.</li>
  <li><strong>Monthly</strong> — paid on the 1st of each month.</li>
</ul>
<p>Your current cycle is shown on the Earnings page. To change it, click <strong>Request change</strong> — changes take effect from the next cycle after approval. Minimum payout is $20.</p>

<h2>Understanding your earnings window</h2>
<ul>
  <li><strong>This window</strong> — earnings from the current pay period not yet disbursed.</li>
  <li><strong>Pending balance</strong> — total funds awaiting the next payout run.</li>
  <li><strong>Lifetime earned</strong> — all-time total.</li>
</ul>""",
    ),

    (
        "writer-availability-and-workload",
        "Managing Your Availability & Workload",
        GuideAudience.WRITER,
        "settings",
        "How to pause new orders, schedule time off, and stay in control of your workload.",
        False,
        3,
        """<h2>Accepting and pausing orders</h2>
<p>Your workspace shows your current availability status. The toggle at the top lets you switch between <strong>Accepting orders</strong> and <strong>Paused</strong>. When paused:</p>
<ul>
  <li>You will not appear in admin's suggested writer lists for new assignments.</li>
  <li>You cannot bid in the marketplace.</li>
  <li>Existing assignments continue — pausing only stops new orders coming in.</li>
</ul>
<p>Switch back to accepting when you are ready. There is no penalty for pausing, but frequent on/off toggling may affect your visibility in the assignment algorithm.</p>

<h2>Scheduling time off</h2>
<p>To block a specific period (holiday, exams, personal leave):</p>
<ol>
  <li>On your workspace, click <strong>Schedule off</strong> in the availability card.</li>
  <li>Set the start date, end date (optional), and a brief reason (optional — internal only).</li>
  <li>Save. The window appears in your upcoming unavailability list.</li>
</ol>
<p>Scheduled windows appear on your workspace so you and your admin team can see them. You can delete an upcoming window at any time if plans change.</p>

<h2>Managing active orders under a tight deadline</h2>
<ul>
  <li>If you are at capacity and cannot take a revision within the 48-hour window, message the order thread immediately and notify the admin team. Do not let the clock run out silently.</li>
  <li>Use the order messages to set realistic expectations — a proactive update is always better than a missed deadline.</li>
  <li>If you are going to be genuinely unable to complete an active order, contact the admin team as early as possible so the order can be re-assigned with minimal disruption to the client.</li>
</ul>""",
    ),

    (
        "writer-classes-and-special-orders",
        "Classes & Special Orders for Writers",
        GuideAudience.WRITER,
        "book-open",
        "How to handle semester-long class assignments and milestone-based special projects.",
        False,
        5,
        """<h2>Classes</h2>
<p>A class assignment spans an entire semester. You are assigned to the class as the dedicated expert for all its tasks. Classes appear in your <strong>Classes</strong> section in the sidebar.</p>

<h2>Your class dashboard</h2>
<p>Open a class to see:</p>
<ul>
  <li>Class title, subject, academic level, and semester dates.</li>
  <li>A task list with individual assignments, their due dates, and current status.</li>
  <li>Payment status (your compensation is released per installment schedule).</li>
  <li>Portal access credentials (if the client has shared login details for the course platform).</li>
</ul>

<h2>Submitting a task</h2>
<ol>
  <li>Find the task in the <strong>Tasks</strong> tab.</li>
  <li>Complete the work (offline, in the course platform, or as a document).</li>
  <li>Use the inline submit form: add notes explaining what you did, optionally attach a file URL, then click <strong>Submit task</strong>.</li>
</ol>
<p>After a task is graded by the instructor, the grade and feedback will appear in the task. Review this — patterns in feedback help you calibrate for the next tasks in the course.</p>

<h2>Communication for classes</h2>
<p>Keep all class-related communication in the class message thread. Do not use the generic messages area for class updates. This keeps a clear record.</p>

<h2>Special orders</h2>
<p>Special orders are milestone-based projects — large papers, multi-chapter dissertations, ongoing writing packages. They appear in your <strong>Special orders</strong> section.</p>
<ul>
  <li>Each milestone has its own delivery date and approval step.</li>
  <li>Deliver each milestone on time, even if it means delivering incomplete work for interim review — missing a milestone delivery is worse than a revision request.</li>
  <li>Your compensation for each milestone is released when the milestone is approved.</li>
</ul>

<h2>Portal access security</h2>
<p>If a client shares course login credentials:</p>
<ul>
  <li>Use them only for this assignment. Never access any other account or area of the platform.</li>
  <li>Do not store or forward the credentials outside the platform.</li>
  <li>Report immediately if you notice any unusual access or locked-out state.</li>
</ul>""",
    ),

    (
        "writer-conduct-and-policy",
        "Writer Conduct & Platform Policy",
        GuideAudience.WRITER,
        "shield-check",
        "Rules you must follow, what happens when rules are broken, and how to appeal a decision.",
        False,
        4,
        """<h2>Core rules</h2>
<ul>
  <li><strong>No contact outside the platform.</strong> Never share your personal contact details with clients or accept payment outside the platform. Violations result in immediate termination.</li>
  <li><strong>No plagiarism.</strong> All work must be original. Fabricated citations or copied content results in termination and any earnings for that order being withheld.</li>
  <li><strong>No subcontracting.</strong> You must complete the work yourself. Do not use AI writing tools to generate content wholesale — use them only as a research aid.</li>
  <li><strong>Confidentiality.</strong> Client briefs, instructions, and any uploaded materials are confidential. Do not share them with anyone.</li>
</ul>

<h2>What happens if a rule is broken</h2>
<ul>
  <li><strong>First offence (minor)</strong> — written warning, fine issued.</li>
  <li><strong>Repeated or serious offence</strong> — account suspension. You cannot take new orders and pending earnings are held pending review.</li>
  <li><strong>Severe offence</strong> (plagiarism, contact outside platform, credential misuse) — permanent termination and earnings forfeiture.</li>
</ul>

<h2>Appealing a fine or suspension</h2>
<p>You can dispute a fine from the <strong>Fines</strong> page or the <strong>Earnings → Fines</strong> tab. For a suspension, contact the admin team through the platform. Provide:</p>
<ul>
  <li>The specific fine or action you are disputing.</li>
  <li>Your evidence or reasoning.</li>
  <li>Any supporting screenshots or documents.</li>
</ul>
<p>Appeals are reviewed within 48 hours. The decision is final unless new evidence is presented.</p>

<h2>Maintaining your rating</h2>
<p>Your <strong>quality score</strong> is the average of all client ratings. Scores below 4.0 restrict you to entry-level orders only. Scores below 3.5 trigger a performance review. The best way to maintain your score is simple: read the brief carefully, deliver on time, and respond to revision requests promptly.</p>""",
    ),

]


# ─────────────────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Seed GuideIndexPage and onboarding GuideArticlePage for every site."

    def add_arguments(self, parser):
        parser.add_argument(
            "--site",
            default=None,
            help="Restrict to a single site hostname.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Overwrite existing guide content.",
        )

    def handle(self, *_args, **options):
        site_filter = options.get("site")
        update = options["update"]

        sites = (
            Site.objects.filter(hostname=site_filter)
            if site_filter
            else Site.objects.all()
        )

        for site in sites:
            self.stdout.write(f"\nSite: {site.hostname}")
            root = site.root_page

            # ── GuideIndexPage ────────────────────────────────────────────────
            index_qs = GuideIndexPage.objects.child_of(root).filter(slug="guides")
            if index_qs.exists():
                index_page = index_qs.first()
                self.stdout.write(
                    f"  GuideIndexPage already exists (pk={index_page.pk})"
                )
            else:
                index_page = GuideIndexPage(
                    title="Guides",
                    slug="guides",
                    depth=root.depth + 1,
                    path=root.path + "0001",
                )
                root.add_child(instance=index_page)
                index_page.save_revision().publish()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Created GuideIndexPage pk={index_page.pk}"
                    )
                )

            # ── GuideArticlePage items ────────────────────────────────────────
            for (
                slug,
                title,
                audience,
                icon,
                summary,
                is_featured,
                read_minutes,
                body,
            ) in GUIDES:
                existing = GuideArticlePage.objects.child_of(index_page).filter(
                    slug=slug
                ).first()

                if existing and not update:
                    self.stdout.write(
                        f"  SKIP {slug!r} (already exists — use --update to overwrite)"
                    )
                    continue

                if existing:
                    page = existing
                    page.title = title
                    page.audience = audience
                    page.icon = icon
                    page.summary = summary
                    page.body = body
                    page.is_featured = is_featured
                    page.estimated_read_minutes = read_minutes
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
                        is_featured=is_featured,
                        estimated_read_minutes=read_minutes,
                    )
                    index_page.add_child(instance=article)
                    article.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS(f"  CREATED {slug!r}"))

        self.stdout.write(self.style.SUCCESS("\nDone."))
