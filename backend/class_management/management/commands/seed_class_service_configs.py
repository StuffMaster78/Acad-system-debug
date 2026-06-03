from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from class_management.models import ClassServiceConfig
from websites.models.websites import Website


class Command(BaseCommand):
    help = "Seed tenant-scoped class service configs for client intake."

    def add_arguments(self, parser):
        parser.add_argument("--website-id", type=int)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):
        website_id = options.get("website_id")
        clear = options.get("clear", False)

        websites = Website.objects.filter(is_active=True, is_deleted=False)
        if website_id:
            websites = websites.filter(id=website_id)

        if not websites.exists():
            self.stdout.write(self.style.WARNING("No active websites found."))
            return

        duration_options = [
            {"key": "4_weeks", "label": "4 weeks", "weeks": 4},
            {"key": "8_weeks", "label": "8 weeks", "weeks": 8},
            {"key": "12_weeks", "label": "12 weeks", "weeks": 12},
            {"key": "semester", "label": "Full semester", "weeks": 16},
        ]
        workload_options = [
            {
                "key": "light",
                "label": "Light",
                "complexity": "low",
                "description": "A few weekly tasks and low complexity.",
                "price_hint": "Best for low-volume courses.",
            },
            {
                "key": "standard",
                "label": "Standard",
                "complexity": "medium",
                "description": "Typical weekly assignments, discussions, and quizzes.",
                "price_hint": "Most common workload.",
            },
            {
                "key": "heavy",
                "label": "Heavy",
                "complexity": "high",
                "description": "Frequent assignments, papers, exams, or projects.",
                "price_hint": "Requires closer review.",
            },
        ]
        task_options = [
            {"key": "assignments", "label": "Assignments"},
            {"key": "discussions", "label": "Discussion posts"},
            {"key": "quizzes", "label": "Quizzes"},
            {"key": "exams", "label": "Exams"},
            {"key": "papers", "label": "Papers / reports"},
            {"key": "projects", "label": "Projects"},
            {"key": "labs", "label": "Labs / practical work"},
        ]
        configs = [
            {
                "name": "Full class management",
                "slug": "full-class-management",
                "description": "Ongoing support for the full course workload across assignments, discussions, quizzes, exams, and deliverables.",
                "service_type": "full_class",
                "base_price": Decimal("0.00"),
                "display_order": 10,
                "requires_portal_access": True,
            },
            {
                "name": "Weekly class support",
                "slug": "weekly-class-support",
                "description": "Recurring weekly help for assignments, discussions, quizzes, and routine coursework.",
                "service_type": "weekly_support",
                "base_price": Decimal("0.00"),
                "display_order": 20,
                "requires_portal_access": True,
            },
            {
                "name": "Exam and quiz support",
                "slug": "exam-quiz-support",
                "description": "Focused support around scheduled quizzes, midterms, finals, and online assessments.",
                "service_type": "exam_quiz",
                "base_price": Decimal("0.00"),
                "display_order": 30,
                "requires_portal_access": True,
            },
            {
                "name": "Assignments only",
                "slug": "assignments-only",
                "description": "Support limited to course assignments, papers, projects, and submitted deliverables.",
                "service_type": "assignments_only",
                "base_price": Decimal("0.00"),
                "display_order": 40,
                "requires_portal_access": False,
            },
        ]

        with transaction.atomic():
            if clear:
                ClassServiceConfig.objects.filter(website__in=websites).delete()

            created = 0
            updated = 0
            for website in websites:
                for config in configs:
                    obj, was_created = ClassServiceConfig.objects.update_or_create(
                        website=website,
                        slug=config["slug"],
                        defaults={
                            **config,
                            "pricing_mode": ClassServiceConfig.PRICING_MODE_QUOTE,
                            "currency": "USD",
                            "duration_options": duration_options,
                            "workload_options": workload_options,
                            "task_options": task_options,
                            "required_fields": [
                                "title",
                                "subject",
                                "academic_level",
                                "starts_on",
                                "ends_on",
                            ],
                            "allow_installments": True,
                            "require_deposit_before_start": True,
                            "deposit_percentage": Decimal("50.00"),
                            "quote_expiry_hours": 72,
                            "is_active": True,
                        },
                    )
                    created += int(was_created)
                    updated += int(not was_created)
                    self.stdout.write(
                        f"{'Created' if was_created else 'Updated'} {website.name}: {obj.name}"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded class configs. Created: {created}. Updated: {updated}."
            )
        )
