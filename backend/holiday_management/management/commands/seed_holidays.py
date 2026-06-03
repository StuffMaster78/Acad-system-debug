"""
Seed pre-defined holidays and special days.

Run once on deploy:  python manage.py seed_holidays
Re-run to add new:   python manage.py seed_holidays          (safe, idempotent)
Force-update all:    python manage.py seed_holidays --update
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from holiday_management.models import SpecialDay

# ---------------------------------------------------------------------------
# Holiday catalogue
# Each entry uses `date` as the month/day reference (year is ignored for
# is_annual=True entries). Floating holidays include a `date_rule` so that
# get_date_for_year() computes the correct date each year.
#
# date_rule types:
#   nth_weekday  — {month, n, weekday, offset_days?}  weekday: 0=Mon … 6=Sun
#   last_weekday — {month, weekday}
#   easter       — {offset_days?}  (offset from Easter Sunday)
# ---------------------------------------------------------------------------

HOLIDAYS = [

    # ── International ────────────────────────────────────────────────────────

    {
        "name": "New Year's Day",
        "description": "First day of the Gregorian calendar year.",
        "event_type": "holiday",
        "date": "2000-01-01",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "critical",
        "reminder_days_before": 10,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "NEWYEAR",
        "discount_valid_days": 3,
    },
    {
        "name": "Valentine's Day",
        "description": "Celebration of love and affection.",
        "event_type": "special_day",
        "date": "2000-02-14",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "VALENTINE",
        "discount_valid_days": 3,
    },
    {
        "name": "International Women's Day",
        "description": "Global celebration of women's social, economic, cultural, and political achievements.",
        "event_type": "special_day",
        "date": "2000-03-08",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "medium",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "IWD",
        "discount_valid_days": 1,
    },
    {
        "name": "Good Friday",
        "description": "Christian observance — two days before Easter Sunday.",
        "event_type": "holiday",
        "date": "2000-04-21",  # reference only; rule drives the real date
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "medium",
        "reminder_days_before": 7,
        "auto_generate_discount": False,
        "discount_percentage": None,
        "discount_code_prefix": "",
        "discount_valid_days": 1,
        "date_rule": {"type": "easter", "offset_days": -2},
    },
    {
        "name": "Easter Sunday",
        "description": "Christian celebration of the resurrection of Jesus Christ.",
        "event_type": "holiday",
        "date": "2000-04-23",  # reference only
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "high",
        "reminder_days_before": 10,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "EASTER",
        "discount_valid_days": 4,
        "date_rule": {"type": "easter", "offset_days": 0},
    },
    {
        "name": "Easter Monday",
        "description": "Day after Easter Sunday, public holiday in many countries.",
        "event_type": "holiday",
        "date": "2000-04-24",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "medium",
        "reminder_days_before": 7,
        "auto_generate_discount": False,
        "discount_percentage": None,
        "discount_code_prefix": "",
        "discount_valid_days": 1,
        "date_rule": {"type": "easter", "offset_days": 1},
    },
    {
        "name": "Earth Day",
        "description": "Annual event promoting environmental awareness.",
        "event_type": "special_day",
        "date": "2000-04-22",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "low",
        "reminder_days_before": 5,
        "auto_generate_discount": False,
        "discount_percentage": None,
        "discount_code_prefix": "",
        "discount_valid_days": 1,
    },
    {
        "name": "International Labour Day",
        "description": "International Workers' Day observed on 1 May.",
        "event_type": "holiday",
        "date": "2000-05-01",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "medium",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "MAYDAY",
        "discount_valid_days": 1,
    },
    {
        "name": "Mother's Day",
        "description": "Celebration honouring mothers — 2nd Sunday of May.",
        "event_type": "special_day",
        "date": "2000-05-14",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "MOTHERS",
        "discount_valid_days": 3,
        "date_rule": {"type": "nth_weekday", "month": 5, "n": 2, "weekday": 6},
    },
    {
        "name": "Father's Day",
        "description": "Celebration honouring fathers — 3rd Sunday of June.",
        "event_type": "special_day",
        "date": "2000-06-18",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "12.00",
        "discount_code_prefix": "FATHERS",
        "discount_valid_days": 3,
        "date_rule": {"type": "nth_weekday", "month": 6, "n": 3, "weekday": 6},
    },
    {
        "name": "World Students' Day",
        "description": "UNESCO day celebrating students worldwide — Oct 15.",
        "event_type": "special_day",
        "date": "2000-10-15",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "20.00",
        "discount_code_prefix": "STUDENTS",
        "discount_valid_days": 3,
    },
    {
        "name": "Halloween",
        "description": "Annual celebration observed on 31 October.",
        "event_type": "special_day",
        "date": "2000-10-31",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "medium",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "HALLOWEEN",
        "discount_valid_days": 1,
    },
    {
        "name": "Christmas Day",
        "description": "Annual Christian festival and worldwide cultural celebration on 25 December.",
        "event_type": "holiday",
        "date": "2000-12-25",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "critical",
        "reminder_days_before": 14,
        "auto_generate_discount": True,
        "discount_percentage": "25.00",
        "discount_code_prefix": "CHRISTMAS",
        "discount_valid_days": 7,
    },
    {
        "name": "New Year's Eve",
        "description": "Last day of the Gregorian calendar year.",
        "event_type": "special_day",
        "date": "2000-12-31",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "NYE",
        "discount_valid_days": 1,
    },

    # ── Back to School (USA/international) ───────────────────────────────────
    {
        "name": "Back to School",
        "description": "Late-summer period when students return to school — prime academic demand.",
        "event_type": "seasonal",
        "date": "2000-08-28",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "critical",
        "reminder_days_before": 21,
        "auto_generate_discount": True,
        "discount_percentage": "20.00",
        "discount_code_prefix": "BACKTOSCHOOL",
        "discount_valid_days": 14,
    },

    # ── United States ────────────────────────────────────────────────────────

    {
        "name": "Martin Luther King Jr. Day",
        "description": "US federal holiday honouring civil rights leader MLK — 3rd Monday of January.",
        "event_type": "holiday",
        "date": "2000-01-17",
        "is_annual": True,
        "is_international": False,
        "countries": ["US"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": False,
        "discount_percentage": None,
        "discount_code_prefix": "",
        "discount_valid_days": 1,
        "date_rule": {"type": "nth_weekday", "month": 1, "n": 3, "weekday": 0},
    },
    {
        "name": "Presidents' Day",
        "description": "US federal holiday honouring all presidents — 3rd Monday of February.",
        "event_type": "holiday",
        "date": "2000-02-21",
        "is_annual": True,
        "is_international": False,
        "countries": ["US"],
        "priority": "low",
        "reminder_days_before": 5,
        "auto_generate_discount": False,
        "discount_percentage": None,
        "discount_code_prefix": "",
        "discount_valid_days": 1,
        "date_rule": {"type": "nth_weekday", "month": 2, "n": 3, "weekday": 0},
    },
    {
        "name": "Memorial Day",
        "description": "US federal holiday honouring fallen military — last Monday of May.",
        "event_type": "holiday",
        "date": "2000-05-29",
        "is_annual": True,
        "is_international": False,
        "countries": ["US"],
        "priority": "medium",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "MEMORIAL",
        "discount_valid_days": 3,
        "date_rule": {"type": "last_weekday", "month": 5, "weekday": 0},
    },
    {
        "name": "Independence Day (US)",
        "description": "US national day celebrating the Declaration of Independence — July 4.",
        "event_type": "holiday",
        "date": "2000-07-04",
        "is_annual": True,
        "is_international": False,
        "countries": ["US"],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "JULY4",
        "discount_valid_days": 3,
    },
    {
        "name": "Labor Day (US)",
        "description": "US federal holiday honouring workers — 1st Monday of September.",
        "event_type": "holiday",
        "date": "2000-09-04",
        "is_annual": True,
        "is_international": False,
        "countries": ["US"],
        "priority": "medium",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "LABORDAY",
        "discount_valid_days": 3,
        "date_rule": {"type": "nth_weekday", "month": 9, "n": 1, "weekday": 0},
    },
    {
        "name": "Veterans Day",
        "description": "US federal holiday honouring military veterans — November 11.",
        "event_type": "holiday",
        "date": "2000-11-11",
        "is_annual": True,
        "is_international": False,
        "countries": ["US"],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "VETERANS",
        "discount_valid_days": 1,
    },
    {
        "name": "Thanksgiving Day (US)",
        "description": "US harvest festival — 4th Thursday of November.",
        "event_type": "holiday",
        "date": "2000-11-23",
        "is_annual": True,
        "is_international": False,
        "countries": ["US"],
        "priority": "critical",
        "reminder_days_before": 10,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "THANKS",
        "discount_valid_days": 4,
        "date_rule": {"type": "nth_weekday", "month": 11, "n": 4, "weekday": 3},
    },
    {
        "name": "Black Friday",
        "description": "Major shopping day — day after US Thanksgiving.",
        "event_type": "special_day",
        "date": "2000-11-24",
        "is_annual": True,
        "is_international": False,
        "countries": ["US", "CA", "GB", "AU"],
        "priority": "critical",
        "reminder_days_before": 14,
        "auto_generate_discount": True,
        "discount_percentage": "20.00",
        "discount_code_prefix": "BLACKFRIDAY",
        "discount_valid_days": 1,
        "date_rule": {"type": "nth_weekday", "month": 11, "n": 4, "weekday": 3, "offset_days": 1},
    },
    {
        "name": "Cyber Monday",
        "description": "Online shopping day — Monday after US Thanksgiving.",
        "event_type": "special_day",
        "date": "2000-11-27",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "critical",
        "reminder_days_before": 14,
        "auto_generate_discount": True,
        "discount_percentage": "20.00",
        "discount_code_prefix": "CYBER",
        "discount_valid_days": 1,
        "date_rule": {"type": "nth_weekday", "month": 11, "n": 4, "weekday": 3, "offset_days": 4},
    },

    # ── United Kingdom / Ireland ─────────────────────────────────────────────

    {
        "name": "St. Patrick's Day",
        "description": "Cultural and religious celebration of Ireland's patron saint — March 17.",
        "event_type": "holiday",
        "date": "2000-03-17",
        "is_annual": True,
        "is_international": False,
        "countries": ["IE", "GB"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "STPATRICK",
        "discount_valid_days": 1,
    },
    {
        "name": "Boxing Day",
        "description": "Public holiday on 26 December observed in UK, Canada, Australia, and others.",
        "event_type": "holiday",
        "date": "2000-12-26",
        "is_annual": True,
        "is_international": False,
        "countries": ["GB", "CA", "AU", "NZ", "ZA"],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "BOXING",
        "discount_valid_days": 3,
    },

    # ── Canada ────────────────────────────────────────────────────────────────

    {
        "name": "Canada Day",
        "description": "Canadian national holiday celebrating Confederation — July 1.",
        "event_type": "holiday",
        "date": "2000-07-01",
        "is_annual": True,
        "is_international": False,
        "countries": ["CA"],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "CANADA",
        "discount_valid_days": 2,
    },
    {
        "name": "Thanksgiving Day (Canada)",
        "description": "Canadian Thanksgiving — 2nd Monday of October.",
        "event_type": "holiday",
        "date": "2000-10-09",
        "is_annual": True,
        "is_international": False,
        "countries": ["CA"],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "12.00",
        "discount_code_prefix": "CANTHANKS",
        "discount_valid_days": 3,
        "date_rule": {"type": "nth_weekday", "month": 10, "n": 2, "weekday": 0},
    },

    # ── Australia / New Zealand ──────────────────────────────────────────────

    {
        "name": "Australia Day",
        "description": "Australian national day — January 26.",
        "event_type": "holiday",
        "date": "2000-01-26",
        "is_annual": True,
        "is_international": False,
        "countries": ["AU"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "AUSTRALIA",
        "discount_valid_days": 1,
    },
    {
        "name": "ANZAC Day",
        "description": "Australia and New Zealand day of remembrance — April 25.",
        "event_type": "holiday",
        "date": "2000-04-25",
        "is_annual": True,
        "is_international": False,
        "countries": ["AU", "NZ"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": False,
        "discount_percentage": None,
        "discount_code_prefix": "",
        "discount_valid_days": 1,
    },

    # ── India ────────────────────────────────────────────────────────────────

    {
        "name": "Republic Day (India)",
        "description": "Indian national holiday commemorating the constitution — January 26.",
        "event_type": "holiday",
        "date": "2000-01-26",
        "is_annual": True,
        "is_international": False,
        "countries": ["IN"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "REPUBLIC",
        "discount_valid_days": 1,
    },
    {
        "name": "Independence Day (India)",
        "description": "Indian national day celebrating independence from British rule — August 15.",
        "event_type": "holiday",
        "date": "2000-08-15",
        "is_annual": True,
        "is_international": False,
        "countries": ["IN"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "INDIAINDY",
        "discount_valid_days": 1,
    },
    {
        "name": "Diwali",
        "description": "Hindu festival of lights — typically October or November (date varies by lunar calendar).",
        "event_type": "cultural",
        "date": "2000-10-20",
        "is_annual": True,
        "is_international": False,
        "countries": ["IN", "NP", "SG", "MY"],
        "priority": "high",
        "reminder_days_before": 10,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "DIWALI",
        "discount_valid_days": 5,
    },

    # ── Kenya / East Africa ──────────────────────────────────────────────────

    {
        "name": "Madaraka Day",
        "description": "Kenyan national holiday commemorating self-governance — June 1.",
        "event_type": "holiday",
        "date": "2000-06-01",
        "is_annual": True,
        "is_international": False,
        "countries": ["KE"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "MADARAKA",
        "discount_valid_days": 1,
    },
    {
        "name": "Mashujaa Day",
        "description": "Kenyan national heroes' day — October 20.",
        "event_type": "holiday",
        "date": "2000-10-20",
        "is_annual": True,
        "is_international": False,
        "countries": ["KE"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "MASHUJAA",
        "discount_valid_days": 1,
    },
    {
        "name": "Jamhuri Day",
        "description": "Kenyan independence and republic day — December 12.",
        "event_type": "holiday",
        "date": "2000-12-12",
        "is_annual": True,
        "is_international": False,
        "countries": ["KE"],
        "priority": "high",
        "reminder_days_before": 7,
        "auto_generate_discount": True,
        "discount_percentage": "12.00",
        "discount_code_prefix": "JAMHURI",
        "discount_valid_days": 2,
    },

    # ── Nigeria ──────────────────────────────────────────────────────────────

    {
        "name": "Nigeria Independence Day",
        "description": "Nigerian national day — October 1.",
        "event_type": "holiday",
        "date": "2000-10-01",
        "is_annual": True,
        "is_international": False,
        "countries": ["NG"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "NIGERIA",
        "discount_valid_days": 1,
    },

    # ── South Africa ─────────────────────────────────────────────────────────

    {
        "name": "Freedom Day (South Africa)",
        "description": "South African public holiday marking the end of apartheid — April 27.",
        "event_type": "holiday",
        "date": "2000-04-27",
        "is_annual": True,
        "is_international": False,
        "countries": ["ZA"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "FREEDOM",
        "discount_valid_days": 1,
    },
    {
        "name": "Youth Day (South Africa)",
        "description": "South African public holiday honouring the 1976 Soweto uprising — June 16.",
        "event_type": "holiday",
        "date": "2000-06-16",
        "is_annual": True,
        "is_international": False,
        "countries": ["ZA"],
        "priority": "medium",
        "reminder_days_before": 5,
        "auto_generate_discount": True,
        "discount_percentage": "10.00",
        "discount_code_prefix": "YOUTHDAY",
        "discount_valid_days": 1,
    },

    # ── Global Commerce / Academic ───────────────────────────────────────────

    {
        "name": "Singles' Day (11.11)",
        "description": "World's largest online shopping event originating in China — November 11.",
        "event_type": "special_day",
        "date": "2000-11-11",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "high",
        "reminder_days_before": 10,
        "auto_generate_discount": True,
        "discount_percentage": "11.00",
        "discount_code_prefix": "SINGLES",
        "discount_valid_days": 1,
    },
    {
        "name": "End of Semester",
        "description": "Peak academic writing demand as semester deadlines approach — mid-December.",
        "event_type": "seasonal",
        "date": "2000-12-10",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "critical",
        "reminder_days_before": 14,
        "auto_generate_discount": True,
        "discount_percentage": "15.00",
        "discount_code_prefix": "SEMESTER",
        "discount_valid_days": 10,
    },
    {
        "name": "Mid-Term Rush",
        "description": "Academic mid-term deadline peak — late October.",
        "event_type": "seasonal",
        "date": "2000-10-25",
        "is_annual": True,
        "is_international": True,
        "countries": [],
        "priority": "high",
        "reminder_days_before": 10,
        "auto_generate_discount": True,
        "discount_percentage": "12.00",
        "discount_code_prefix": "MIDTERM",
        "discount_valid_days": 5,
    },
]


# Fields admins are allowed to customise on a seeded record via management cmd update
_ADMIN_EDITABLE = {
    "discount_percentage", "discount_code_prefix", "discount_valid_days",
    "auto_generate_discount", "send_broadcast_reminder", "reminder_days_before",
    "is_active",
}


class Command(BaseCommand):
    help = "Seed pre-defined holidays (idempotent; use --update to refresh admin-editable fields)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Overwrite admin-editable fields (discount %, prefix, valid days) on existing seeded records.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created/updated without writing.",
        )

    def handle(self, *args, **options):
        update   = options["update"]
        dry_run  = options["dry_run"]
        created  = 0
        updated  = 0
        skipped  = 0

        User = __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model()
        admin = (
            User.objects.filter(role="superadmin").first()
            or User.objects.filter(role="admin").first()
        )

        for entry in HOLIDAYS:
            date_rule   = entry.pop("date_rule", None)
            raw_date    = entry.pop("date")
            from datetime import date as _date
            year, month, day = map(int, raw_date.split("-"))
            ref_date = _date(year, month, day)

            existing = SpecialDay.objects.filter(
                name=entry["name"], is_seeded=True
            ).first()

            if existing:
                if update:
                    for field in _ADMIN_EDITABLE:
                        if field in entry:
                            setattr(existing, field, entry[field])
                    if not dry_run:
                        existing.save()
                    self.stdout.write(self.style.SUCCESS(f"  UPDATED  {existing.name}"))
                    updated += 1
                else:
                    self.stdout.write(f"  skip     {entry['name']} (already exists)")
                    skipped += 1
                continue

            if dry_run:
                self.stdout.write(f"  CREATE   {entry['name']}")
                created += 1
                continue

            SpecialDay.objects.create(
                date=ref_date,
                date_rule=date_rule,
                is_seeded=True,
                send_broadcast_reminder=True,
                created_by=admin,
                **entry,
            )
            self.stdout.write(self.style.SUCCESS(f"  CREATED  {entry['name']}"))
            created += 1

        verb = "Would create" if dry_run else "Created"
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{verb}: {created} | Updated: {updated} | Skipped: {skipped}"
            )
        )
