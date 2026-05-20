import pandas as pd
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mass_emails.models import (
    EmailCampaign,
    EmailClickTracker,
    EmailOpenTracker,
    UnsubscribeLog,
)


class CampaignAnalyticsDashboard(APIView):
    """
    Provides summary analytics for email campaigns.
    Includes open/click/unsubscribe counts and rates.
    CSV/Excel export.
    Query params:
      - start=YYYY-MM-DD
      - end=YYYY-MM-DD
      - export=csv | xlsx
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_raw = request.GET.get('start')
        end_raw = request.GET.get('end')
        start_date = parse_date(start_raw) if isinstance(
            start_raw, str) else None
        end_date = parse_date(end_raw) if isinstance(end_raw, str) else None
        export_format = request.GET.get('export')

        campaigns = EmailCampaign.objects.all()
        if start_date and end_date:
            campaigns = campaigns.filter(
                sent_time__date__gte=start_date,
                sent_time__date__lte=end_date
            )
        rows = []

        for campaign in campaigns:
            recipients = campaign.recipients.all()
            recipient_count = recipients.count()

            opens = EmailOpenTracker.objects.filter(
                recipient__in=recipients
            ).count()

            clicks = EmailClickTracker.objects.filter(
                recipient__in=recipients
            ).count()

            unsubscribes = UnsubscribeLog.objects.filter(
                email__in=recipients.values_list('email', flat=True)
            ).count()

            sent_time = None
            if campaign.sent_time:
                sent_time = campaign.sent_time.isoformat()

            open_rate = 0
            click_rate = 0
            unsubscribe_rate = 0
            if recipient_count:
                open_rate = round(opens / recipient_count * 100, 2)
                click_rate = round(clicks / recipient_count * 100, 2)
                unsubscribe_rate = round(
                    unsubscribes / recipient_count * 100,
                    2,
                )

            rows.append(
                {
                    "campaign_id": campaign.id,
                    "title": campaign.title,
                    "sent_time": sent_time,
                    "recipients": recipient_count,
                    "opens": opens,
                    "clicks": clicks,
                    "unsubscribes": unsubscribes,
                    "open_rate": open_rate,
                    "click_rate": click_rate,
                    "unsubscribe_rate": unsubscribe_rate,
                }
            )

            # The Export logic
            if export_format in ["csv", "xlsx"]:
                df = pd.DataFrame(rows)
                if export_format == "csv":
                    response = HttpResponse(content_type="text/csv")
                    response["Content-Disposition"] = (
                        "attachment; filename=campaign-analytics.csv"
                    )
                    df.to_csv(path_or_buf=response, index=False)
                    return response
                elif export_format == "xlsx":
                    response = HttpResponse(
                        content_type=(
                            "application/vnd.openxmlformats-"
                            "officedocument.spreadsheetml.sheet"
                        )
                    )
                    response["Content-Disposition"] = (
                        "attachment; filename=campaign-analytics.xlsx"
                    )
                    df.to_excel(response, index=False, engine='openpyxl')
                    return response

        return Response({
            "filters": {
                "start": start_date,
                "end": end_date,
            },
            "results": rows
        })
