from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from mass_emails.models import (
    EmailRecipient,
    EmailOpenTracker,
    EmailClickTracker,
    UnsubscribeLog,
)


class CampaignTrendingAnalytics(APIView):
    """
    Returns daily opens, clicks, unsubscribes over time.
    Optional query params:
      - days = 7 | 14 | 30
      - campaign_id=12
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.GET.get('days', 7))
        campaign_id = request.GET.get('campaign_id')
        end_date = now().date()
        start_date = end_date - timedelta(days=days - 1)

        date_range = [
            (start_date + timedelta(days=i)) for i in range(days)
        ]
        labels = [date.isoformat() for date in date_range]

        base_filter = {}
        if campaign_id:
            base_filter["recipient__campaign_id"] = campaign_id

        # Daily opens
        opens = (
            EmailOpenTracker.objects
            .filter(**base_filter, opened_at__date__range=[start_date, end_date])
            .values("opened_at__date")
            .annotate(count=Count("id"))
        )
        open_map = {o["opened_at__date"].isoformat(): o["count"] for o in opens}

        # Daily clicks
        clicks = (
            EmailClickTracker.objects
            .filter(**base_filter, clicked_at__date__range=[start_date, end_date])
            .values("clicked_at__date")
            .annotate(count=Count("id"))
        )
        click_map = {c["clicked_at__date"].isoformat(): c["count"] for c in clicks}

        # Daily unsubscribes
        emails = EmailRecipient.objects.filter(
            campaign_id=campaign_id
        ).values_list("email", flat=True) if campaign_id else None

        unsub_filter = {"unsubscribed_at__date__range": [start_date, end_date]}
        if emails:
            unsub_filter["email__in"] = list(emails)

        unsubs = (
            UnsubscribeLog.objects
            .filter(**unsub_filter)
            .values("unsubscribed_at__date")
            .annotate(count=Count("id"))
        )
        unsub_map = {u["unsubscribed_at__date"].isoformat(): u["count"] for u in unsubs}

        # Build daily data series
        open_series = [open_map.get(date, 0) for date in labels]
        click_series = [click_map.get(date, 0) for date in labels]
        unsub_series = [unsub_map.get(date, 0) for date in labels]

        return Response({
            "labels": labels,
            "opens": open_series,
            "clicks": click_series,
            "unsubscribes": unsub_series
        })