"""
seed_writerscreek — one-time production setup for writerscreek.com.

Idempotent: safe to run multiple times. Creates or updates; never deletes.

Usage:
    python manage.py seed_writerscreek
    python manage.py seed_writerscreek --superadmin-email admin@writerscreek.com
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError


GRAMMAR_QUIZ = {
    "title": "Grammar & Style Test",
    "description": (
        "Assesses core grammar, punctuation, and style skills required "
        "for all writing assignments on the platform."
    ),
    "instructions": (
        "Read each question carefully and choose the best answer. "
        "You have 30 minutes. A score of 75% or higher is required to pass."
    ),
    "quiz_type": "grammar",
    "pass_score": 75,
    "time_limit_minutes": 30,
    "max_attempts": 3,
    "is_active": True,
    "is_required_for_approval": True,
}

GRAMMAR_QUESTIONS = [
    {
        "text": "Which sentence is punctuated correctly?",
        "question_type": "multiple_choice",
        "points": 1,
        "order": 1,
        "choices": [
            {"text": "Its a beautiful day, isnt it?", "is_correct": False},
            {"text": "It's a beautiful day, isn't it?", "is_correct": True},
            {"text": "Its a beautiful day isn't it?", "is_correct": False},
            {"text": "It's a beautiful day isn't, it?", "is_correct": False},
        ],
    },
    {
        "text": "Choose the correctly spelled word.",
        "question_type": "multiple_choice",
        "points": 1,
        "order": 2,
        "choices": [
            {"text": "Accomodate", "is_correct": False},
            {"text": "Acommodate", "is_correct": False},
            {"text": "Accommodate", "is_correct": True},
            {"text": "Accommadate", "is_correct": False},
        ],
    },
    {
        "text": "Which sentence uses the correct subject-verb agreement?",
        "question_type": "multiple_choice",
        "points": 1,
        "order": 3,
        "choices": [
            {"text": "The team are playing well today.", "is_correct": False},
            {"text": "The team is playing well today.", "is_correct": True},
            {"text": "The team were playing well today.", "is_correct": False},
            {"text": "The team be playing well today.", "is_correct": False},
        ],
    },
    {
        "text": "A semicolon can be used to join two independent clauses.",
        "question_type": "true_false",
        "points": 1,
        "order": 4,
        "choices": [
            {"text": "True", "is_correct": True},
            {"text": "False", "is_correct": False},
        ],
    },
    {
        "text": "Which word correctly completes this sentence: 'She had __ idea what to do next.'",
        "question_type": "multiple_choice",
        "points": 1,
        "order": 5,
        "choices": [
            {"text": "no", "is_correct": True},
            {"text": "know", "is_correct": False},
            {"text": "not", "is_correct": False},
            {"text": "nor", "is_correct": False},
        ],
    },
    {
        "text": "Identify the passive voice sentence.",
        "question_type": "multiple_choice",
        "points": 1,
        "order": 6,
        "choices": [
            {"text": "The chef prepared the meal.", "is_correct": False},
            {"text": "The meal was prepared by the chef.", "is_correct": True},
            {"text": "The chef is preparing the meal.", "is_correct": False},
            {"text": "The chef will prepare the meal.", "is_correct": False},
        ],
    },
    {
        "text": "Which sentence contains a dangling modifier?",
        "question_type": "multiple_choice",
        "points": 1,
        "order": 7,
        "choices": [
            {"text": "Running quickly, she caught the bus.", "is_correct": False},
            {"text": "Having finished the report, the meeting was adjourned.", "is_correct": True},
            {"text": "After he finished the report, the team held a meeting.", "is_correct": False},
            {"text": "She finished the report and adjourned the meeting.", "is_correct": False},
        ],
    },
    {
        "text": "An Oxford comma is placed before the final item in a list of three or more.",
        "question_type": "true_false",
        "points": 1,
        "order": 8,
        "choices": [
            {"text": "True", "is_correct": True},
            {"text": "False", "is_correct": False},
        ],
    },
    {
        "text": "Which option correctly uses 'affect' and 'effect'?",
        "question_type": "multiple_choice",
        "points": 1,
        "order": 9,
        "choices": [
            {"text": "The weather effected her mood; the affect was noticeable.", "is_correct": False},
            {"text": "The weather affected her mood; the effect was noticeable.", "is_correct": True},
            {"text": "The weather affected her mood; the affect was noticeable.", "is_correct": False},
            {"text": "The weather effected her mood; the effect was noticeable.", "is_correct": False},
        ],
    },
    {
        "text": "Which sentence avoids wordiness?",
        "question_type": "multiple_choice",
        "points": 1,
        "order": 10,
        "choices": [
            {"text": "Due to the fact that it was raining, we stayed inside.", "is_correct": False},
            {"text": "In the event that it rains, we will stay inside.", "is_correct": False},
            {"text": "Because it was raining, we stayed inside.", "is_correct": True},
            {"text": "On account of the rain, we made the decision to stay inside.", "is_correct": False},
        ],
    },
]

ESSAY_QUIZ = {
    "title": "Writing Sample",
    "description": (
        "Submit a short writing sample so our editors can assess your "
        "style, structure, and argumentation."
    ),
    "instructions": (
        "Write a 300–500 word response to the prompt below. You may type "
        "your answer directly or upload a document (PDF, DOCX). "
        "There is no time limit. Your response will be reviewed manually "
        "by an editor within 1–3 business days."
    ),
    "quiz_type": "essay",
    "pass_score": 75,
    "time_limit_minutes": 0,
    "max_attempts": 2,
    "is_active": True,
    "is_required_for_approval": True,
}

ESSAY_QUESTION = {
    "text": (
        "In 300–500 words, discuss the advantages and disadvantages of "
        "remote work. Present a balanced argument and conclude with your "
        "own reasoned position. Focus on clarity, structure, and style."
    ),
    "question_type": "essay",
    "points": 1,
    "order": 1,
}


class Command(BaseCommand):
    help = "Seed writerscreek.com production data: website record, writer levels, and starter vetting quizzes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--superadmin-email",
            default="",
            help="Email for the superadmin account (skipped if empty).",
        )
        parser.add_argument(
            "--superadmin-password",
            default="",
            help="Password for the superadmin account.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== seed_writerscreek ===\n"))

        website = self._seed_website()
        self._seed_branding(website)
        self._seed_writer_levels(website)
        self._seed_writer_level_settings(website)
        self._seed_grammar_quiz(website)
        self._seed_essay_quiz(website)

        email = options["superadmin_email"]
        password = options["superadmin_password"]
        if email and password:
            self._seed_superadmin(website, email, password)
        elif email:
            self.stdout.write(self.style.WARNING(
                "  superadmin-email given but --superadmin-password missing — skipping superadmin creation."
            ))

        self.stdout.write(self.style.SUCCESS("\nDone. writerscreek.com is ready.\n"))

    # ── Website ───────────────────────────────────────────────────────────────

    def _seed_website(self):
        from websites.models.websites import Website

        website, created = Website.objects.update_or_create(
            domain="writerscreek.com",
            defaults={
                "name": "Writers Creek",
                "slug": "writerscreek",
                "is_active": True,
                "is_deleted": False,
            },
        )
        self._log("Website", website.name, created)
        return website

    # ── Branding ──────────────────────────────────────────────────────────────

    def _seed_branding(self, website):
        from websites.models.website_branding import WebsiteBranding

        branding, created = WebsiteBranding.objects.update_or_create(
            website=website,
            defaults={
                "brand_name": "Writers Creek",
                "tagline": "A selective academic writing network.",
                "homepage_headline": "Write at the highest standard.",
                "homepage_subheadline": (
                    "Competitive per-page rates, flexible assignments, and reliable "
                    "bi-weekly payouts — for writers who take their craft seriously."
                ),
                "primary_color": "#0f172a",   # slate-900
                "secondary_color": "#1e293b", # slate-800
                "accent_color": "#38bdf8",    # sky-400
                "is_public": False,
            },
        )
        self._log("WebsiteBranding", branding.brand_name, created)
        return branding

    # ── Writer levels ─────────────────────────────────────────────────────────

    def _seed_writer_levels(self, website):
        try:
            from writer_management.models.writer_level import WriterLevel
        except ImportError:
            self.stdout.write(self.style.WARNING("  WriterLevel model not found — skipping."))
            return

        levels = [
            {"name": "Entry",    "display_order": 1},
            {"name": "Standard", "display_order": 2},
            {"name": "Senior",   "display_order": 3},
            {"name": "Expert",   "display_order": 4},
        ]
        for data in levels:
            obj, created = WriterLevel.objects.update_or_create(
                website=website,
                name=data["name"],
                defaults={"display_order": data["display_order"]},
            )
            self._log("WriterLevel", obj.name, created)

    # ── Writer level settings (rate card) ─────────────────────────────────────

    def _seed_writer_level_settings(self, website):
        from writer_management.models.writer_level import WriterLevel
        from writer_management.models.writer_level_settings import WriterLevelSettings

        # Base per-page rates match the published homepage tiers.
        # Use the floor of each range so writers are never paid less
        # than advertised; bonuses and urgency uplifts take them higher.
        level_settings = [
            {
                "name": "Entry",
                "earning_mode": "fixed_per_page",
                "base_pay_per_page": "4.00",
                "base_pay_per_slide": "3.00",
                "base_pay_per_chart": "3.00",
                "urgent_time_threshold_hours": 12,
                "urgent_order_surcharge": "0.50",
                "urgent_multiplier": "1.10",
                "tip_percentage": "100.00",
                "max_active_orders": 3,
                "max_manual_takes": 2,
                "max_pending_assignments": 3,
            },
            {
                "name": "Standard",
                "earning_mode": "fixed_per_page",
                "base_pay_per_page": "6.00",
                "base_pay_per_slide": "4.50",
                "base_pay_per_chart": "4.50",
                "urgent_time_threshold_hours": 12,
                "urgent_order_surcharge": "0.75",
                "urgent_multiplier": "1.15",
                "tip_percentage": "100.00",
                "max_active_orders": 6,
                "max_manual_takes": 4,
                "max_pending_assignments": 6,
            },
            {
                "name": "Senior",
                "earning_mode": "fixed_per_page",
                "base_pay_per_page": "9.00",
                "base_pay_per_slide": "7.00",
                "base_pay_per_chart": "7.00",
                "urgent_time_threshold_hours": 8,
                "urgent_order_surcharge": "1.00",
                "urgent_multiplier": "1.20",
                "tip_percentage": "100.00",
                "max_active_orders": 10,
                "max_manual_takes": 6,
                "max_pending_assignments": 10,
            },
            {
                "name": "Expert",
                "earning_mode": "fixed_per_page",
                "base_pay_per_page": "13.00",
                "base_pay_per_slide": "10.00",
                "base_pay_per_chart": "10.00",
                "urgent_time_threshold_hours": 6,
                "urgent_order_surcharge": "1.50",
                "urgent_multiplier": "1.25",
                "tip_percentage": "100.00",
                "max_active_orders": 15,
                "max_manual_takes": 10,
                "max_pending_assignments": 15,
            },
        ]

        for config in level_settings:
            level_name = config.pop("name")
            try:
                level = WriterLevel.objects.get(website=website, name=level_name)
            except WriterLevel.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"  WriterLevel '{level_name}' not found — skipping settings."
                ))
                continue

            settings, created = WriterLevelSettings.objects.update_or_create(
                writer_level=level,
                defaults=config,
            )
            self._log(f"WriterLevelSettings ({level_name})", f"{config['base_pay_per_page']}/page", created)

    # ── Grammar quiz ──────────────────────────────────────────────────────────

    def _seed_grammar_quiz(self, website):
        from writer_vetting.models import VettingChoice, VettingQuestion, VettingQuiz

        quiz, created = VettingQuiz.objects.update_or_create(
            website=website,
            title=GRAMMAR_QUIZ["title"],
            defaults={k: v for k, v in GRAMMAR_QUIZ.items() if k != "title"},
        )
        self._log("VettingQuiz (grammar)", quiz.title, created)

        for q_data in GRAMMAR_QUESTIONS:
            choices = q_data.pop("choices")
            question, q_created = VettingQuestion.objects.update_or_create(
                quiz=quiz,
                order=q_data["order"],
                defaults=q_data,
            )
            if q_created:
                for c_data in choices:
                    VettingChoice.objects.create(question=question, **c_data)

            q_data["choices"] = choices  # restore for idempotency

    # ── Essay quiz ────────────────────────────────────────────────────────────

    def _seed_essay_quiz(self, website):
        from writer_vetting.models import VettingQuestion, VettingQuiz

        quiz, created = VettingQuiz.objects.update_or_create(
            website=website,
            title=ESSAY_QUIZ["title"],
            defaults={k: v for k, v in ESSAY_QUIZ.items() if k != "title"},
        )
        self._log("VettingQuiz (essay)", quiz.title, created)

        VettingQuestion.objects.update_or_create(
            quiz=quiz,
            order=ESSAY_QUESTION["order"],
            defaults={k: v for k, v in ESSAY_QUESTION.items() if k != "order"},
        )

    # ── Superadmin ────────────────────────────────────────────────────────────

    def _seed_superadmin(self, website, email, password):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user, created = User.objects.update_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "role": "superadmin",
                "website": None,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "email_verified": True,
            },
        )
        if created or not user.has_usable_password():
            user.set_password(password)
            user.save(update_fields=["password"])
        self._log("Superadmin", email, created)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _log(self, model: str, name: str, created: bool) -> None:
        verb = self.style.SUCCESS("created") if created else "already exists"
        self.stdout.write(f"  {model}: {name} — {verb}")
