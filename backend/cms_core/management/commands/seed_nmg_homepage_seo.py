"""
Seed the NurseMyGrade TenantHomePage.home_seo_body StreamField with the
long-form SEO content from the live nursemygrade.com homepage.

Run:
    docker exec writing_project-web-1 python manage.py seed_nmg_homepage_seo
    docker exec writing_project-web-1 python manage.py seed_nmg_homepage_seo --update
"""

from django.core.management.base import BaseCommand


HOME_SEO_BLOCKS = [
    # ── 1. Leading NMG intro ─────────────────────────────────────────────────
    {
        "type": "heading",
        "value": {
            "text": "Leading Nursing Paper Writing Service",
            "level": "h2",
            "subtitle": "",
            "accent": "none",
        },
    },
    {
        "type": "paragraph",
        "value": (
            "<p>If you are a nursing student overwhelmed with assignments, homework, essays, and "
            "other academic tasks, we have the good news for you. NurseMyGrade is a leading "
            "online nursing paper writing service that you can trust to offload all these from "
            "your chest. We pride ourselves in writing the best nursing papers that are 100% "
            "unique and plagiarism-free.</p>"
            "<p>The nursing paper writers in our team research widely, read the instructions, "
            "and craft papers from scratch. We hire bright and talented writers who are "
            "themselves trained nurses. We have writers with BSN, MSN, and DNPs in our team. "
            "They understand what entails good nursing assignments and papers. No wonder we "
            "have the best reviews for our nursing paper writing services. From the reviews of "
            "our loyal clients, we have attained a rating of 4.98 out of 5 stars because of "
            "the excellent work we do.</p>"
            "<p>We are a preferred custom nursing paper website because all our written nursing "
            "papers pass plagiarism checkers. When you get the papers, you can actively read "
            "through, understand, and make necessary changes to suit your writing style "
            "further because they are professionally written. The papers are written in "
            "standard APA, AMA, or Harvard format, depending on your instructor or "
            "professor&rsquo;s wishes. All you have to do is provide your nursing writers "
            "with the instructions, specify the deadline, communicate with the writer if "
            "necessary, and wait for your paper within the best turnaround time.</p>"
            "<p>If you find out that your nursing paper or assignment is due at the last "
            "minute, you can trust us to write your assignment, discussion post or response, "
            "or essay within less than 12 hours or less than a day. Yes, our service is fast, "
            "reliable, and accurate. We work with non-traditional nursing students who want to "
            "add nursing degrees to their chest of academic qualifications. You can always "
            "trust us for the best quality nursing papers. At NurseMyGrade, you can pay "
            "someone to do your nursing term paper, research paper, or essay. Our costs are "
            "affordable.</p>"
        ),
    },
    # ── 2. Why NurseMyGrade? ─────────────────────────────────────────────────
    {
        "type": "heading",
        "value": {
            "text": "Why NurseMyGrade?",
            "level": "h2",
            "subtitle": "If you are looking for nursing papers for sale, you have all the reasons to get help from our website.",
            "accent": "none",
        },
    },
    {
        "type": "checklist",
        "value": {
            "title": "",
            "items": [
                {
                    "text": "Qualified nursing writers",
                    "detail": (
                        "We have qualified nursing writers who understand how to write various "
                        "nursing papers and completely different nursing homework. Therefore, "
                        "you can trust the nursing paper examples or model papers from our "
                        "website because they are professionally done."
                    ),
                },
                {
                    "text": "Exclusive access to our blog",
                    "detail": (
                        "You will have exclusive access to our blog that shares information "
                        "regarding different nursing papers, how to survive as a nursing "
                        "student and as a professional nurse, and everything else you need "
                        "to succeed in this noble career."
                    ),
                },
                {
                    "text": "Communicate directly with your writer",
                    "detail": (
                        "We allow you to communicate directly with your writer. You can seek "
                        "clarifications to further understand what they wrote, how they did "
                        "their research, and interpretation of difficult-to-understand areas."
                    ),
                },
                {
                    "text": "Work with a single writer for all assignments",
                    "detail": (
                        "You can work with a single writer for all your assignments for "
                        "consistency. This ensures your papers maintain a uniform voice and "
                        "style throughout your programme."
                    ),
                },
                {
                    "text": "Resources and plagiarism report on request",
                    "detail": (
                        "The writers will provide you with the resources used in your papers "
                        "upon your request. The same applies to a plagiarism report. "
                        "Terms and conditions apply."
                    ),
                },
                {
                    "text": "Always delivered before the deadline",
                    "detail": (
                        "Once you place an order, you can be sure it will be delivered before "
                        "the deadline. No assignment is too challenging or complex for our "
                        "excellent team of nursing writers."
                    ),
                },
                {
                    "text": "The best nursing assignment help website",
                    "detail": (
                        "We are the best nursing assignment help website you can trust for "
                        "all your assignments, from simple weekly posts to complex capstone "
                        "projects and dissertations."
                    ),
                },
                {
                    "text": "Country-specific references",
                    "detail": (
                        "Papers are written based on country-specific references. If you are "
                        "from Australia, the UK, the USA, or Canada, you can be sure your "
                        "papers will be written based on references from your country, unless "
                        "otherwise stated in your instructions."
                    ),
                },
                {
                    "text": "Professionalism, free revisions, and timely submission",
                    "detail": (
                        "When you pay someone to do your nursing assignment on our website, "
                        "you are guaranteed professionalism, free revisions, access to your "
                        "writer through messages, frequent drafts, and timely submission "
                        "of the assignments."
                    ),
                },
                {
                    "text": "Legit, verified, and tested by nursing students",
                    "detail": (
                        "We are a legit online nursing papers service, a website whose "
                        "services are verified, tried, and tested by different nursing "
                        "students. Get your online nursing assignments written by "
                        "NurseMyGrade experts and see the difference that step makes "
                        "in your grades."
                    ),
                },
            ],
        },
    },
    # ── 3. Class/Coursework Help ─────────────────────────────────────────────
    {
        "type": "heading",
        "value": {
            "text": "Entire Class / Coursework Help Bundles",
            "level": "h2",
            "subtitle": "",
            "accent": "none",
        },
    },
    {
        "type": "paragraph",
        "value": (
            "<p>Are your nursing classes reigning terror on you? Do you feel overwhelmed with "
            "assignments, discussion posts and responses, essays, and quizzes? We got your "
            "back. NurseMyGrade experts can take your entire nursing class. Yes, you can pay "
            "someone to take your nursing class for you.</p>"
            "<p>All you have to do is provide the details, follow up with the writer, and "
            "ensure that you revise well and understand because nursing is a very sensitive "
            "course. Then, we can take your online nursing class and ensure that you get "
            "the best grades.</p>"
            "<p>You can trust our expert nurse writers for academic excellence. A competent "
            "writer will be assigned to complete your assignments on time. Besides, you can "
            "be sure of the quality and that your submissions will not have plagiarism.</p>"
            "<p>We understand the journey of becoming a nurse. While it is a noble course, "
            "being a nurse student comes with its fair share of challenges. Sometimes you, "
            "as a person, need to relax, free yourself from deadline anxiety, and just let "
            "loose. However, you can only do so when you have someone who can reliably "
            "complete your nursing papers.</p>"
            "<p>When you are looking for a private online nursing writing service, you can be "
            "sure to trust NurseMyGrade. We have assisted many students thus far, most of "
            "whom have progressed to become nursing scholars, RNs, and advanced their studies "
            "to become top nurse leaders in different continents.</p>"
            "<p>Our team comprises people drawn from medical and nursing backgrounds. We "
            "carefully recruit, handpick, and retrain our writers so that we maintain high "
            "quality and achieve higher customer satisfaction.</p>"
            "<p>The assignments are written based on the prompts, instructions, and rubric "
            "you provide us. When you need a topic selected, your writer will cooperate with "
            "you to ensure you get a good nursing paper topic based on your coursework and "
            "readings.</p>"
            "<p>Trusting us with your online nursing classes or weeks-long coursework is like "
            "giving us your life. We never take it for granted, and that&rsquo;s why you will "
            "appreciate the results because we work hard through the writers to deliver "
            "nothing short of the best.</p>"
        ),
    },
    # ── 4. Nursing School Admissions ─────────────────────────────────────────
    {
        "type": "heading",
        "value": {
            "text": "Let's Get You Into Nursing School",
            "level": "h2",
            "subtitle": "",
            "accent": "none",
        },
    },
    {
        "type": "paragraph",
        "value": (
            "<p>With the global and nationwide nursing shortage, the entry criteria into "
            "nursing schools are becoming tougher by the day. You can be asked to write a "
            "&ldquo;why nursing&rdquo; essay, a personal statement, or a statement of "
            "purpose to demonstrate your passion for nursing and your suitability for the "
            "programme. These are not easy documents to craft, and the competition is stiff.</p>"
            "<p>NurseMyGrade has helped thousands of aspiring nursing students get into "
            "their desired programmes. Our admission essay writers know what nursing schools "
            "want to see: genuine motivation, clinical awareness, and evidence of the "
            "personal qualities that make a great nurse. We help you tell your story in a "
            "way that resonates with admissions panels.</p>"
            "<p>Whether you are applying to a BSN, ADN, MSN, DNP, or CRNA programme, "
            "our writers have navigated the same process and know what works. Your "
            "admission essay is the one part of your application you can control completely "
            "&mdash; make it count.</p>"
        ),
    },
]


class Command(BaseCommand):
    help = "Seed NurseMyGrade TenantHomePage.home_seo_body with live-site SEO content"

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Overwrite existing home_seo_body even if it is already set",
        )
        parser.add_argument(
            "--site",
            default="nursemygrade.com",
            help="Hostname of the target Wagtail site (default: nursemygrade.com)",
        )

    def handle(self, *args, **options):
        from wagtail.models import Site
        from cms_core.models import TenantHomePage

        hostname = options["site"]
        do_update = options["update"]

        try:
            site = Site.objects.get(hostname=hostname)
        except Site.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No site found for '{hostname}'"))
            return

        try:
            home = TenantHomePage.objects.get(pk=site.root_page_id)
        except TenantHomePage.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"Root page for '{hostname}' is not a TenantHomePage"
                )
            )
            return

        if home.home_seo_body and not do_update:
            self.stdout.write(
                self.style.WARNING(
                    f"home_seo_body already set on '{hostname}' home page — "
                    "pass --update to overwrite"
                )
            )
            return

        home.home_seo_body = HOME_SEO_BLOCKS
        revision = home.save_revision()
        revision.publish()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded home_seo_body on '{hostname}' ({len(HOME_SEO_BLOCKS)} blocks)"
            )
        )
