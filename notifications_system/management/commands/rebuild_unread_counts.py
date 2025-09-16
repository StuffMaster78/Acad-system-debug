# notifications_system/management/commands/rebuild_unread_counts.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications_system.utils.unread_rebuild import rebuild_unread

User = get_user_model()

class Command(BaseCommand):
    help = "Rebuild unread counters for all users (global or per-tenant if you adapt it)."

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=int, help="Only rebuild for a single user id")

    def handle(self, *args, **options):
        uid = options.get("user_id")
        if uid:
            u = User.objects.get(id=uid)
            c = rebuild_unread(u)
            self.stdout.write(self.style.SUCCESS(f"[user={uid}] unread={c}"))
            return

        for u in User.objects.all().iterator():
            c = rebuild_unread(u)
            self.stdout.write(f"user={u.id} unread={c}")
        self.stdout.write(self.style.SUCCESS("Done"))