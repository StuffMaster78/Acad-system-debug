from writer_management.models.badges import Badge, WriterBadge
from writer_management.models.profile import WriterProfile
from writer_management.models.metrics import WriterPerformanceMetrics
from django.utils.timezone import now


class AutoBadgeAwardService:
    @staticmethod
    def run(writer: WriterProfile):
        metrics = getattr(writer, "performance_metrics", None)
        if not metrics:
            return []

        awarded = []

        def _award(slug):
            try:
                badge = Badge.objects.get(icon=slug)
            except Badge.DoesNotExist:
                return

            already_awarded = WriterBadge.objects.filter(
                writer=writer, badge=badge, revoked=False
            ).exists()

            if not already_awarded:
                WriterBadge.objects.create(
                    writer=writer,
                    badge=badge,
                    is_auto_awarded=True
                )
                awarded.append(slug)

        # 🧠 Consistent Pro: 3 weeks in top 10
        if metrics.top_10_streak_weeks >= 3:
            _award("🧠")

        # 💼 Big Earner: $1000+ total
        if metrics.total_earned_usd >= 1000:
            _award("💼")

        # 🧹 No Revisions: 10 orders with 0 revisions
        if metrics.zero_revision_orders >= 10:
            _award("🧹")

        # 🧊 Cool Head: 20+ orders, 0 disputes
        if metrics.completed_orders >= 20 and metrics.dispute_rate == 0:
            _award("🧊")

        # 🔥 Hot Streak: 7-day activity streak
        if metrics.activity_streak_days >= 7:
            _award("🔥")

        # 👑 Chosen One: Preferred by 5+ clients
        if metrics.preferred_by_count >= 5:
            _award("👑")

        return awarded