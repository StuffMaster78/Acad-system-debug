import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.http import HttpResponse
from mass_emails.models import (
    EmailCampaign,
    EmailOpenTracker,
    EmailClickTracker,
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
        start_date = parse_date(request.GET.get('start'))
        end_date = parse_date(request.GET.get('end'))
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

            rows.append({
                "Campaign ID": campaign.id,
                "Title": campaign.title,
                "Sent Time": campaign.sent_time,
                "Recipients": recipient_count,
                "Opens": opens,
                "Clicks": clicks,
                "Unsubscribes": unsubscribes,
                "Open Rate (%)": round(opens / recipient_count * 100, 2)
                if recipient_count else 0,
                "Click Rate (%)": round(clicks / recipient_count * 100, 2)
                if recipient_count else 0,
                "Unsubscribe Rate (%)": round(unsubscribes / recipient_count * 100, 2)
                if recipient_count else 0,
            })

            # The Export logic
            if export_format in ["csv", "xlsx"]:
                df = pd.DataFrame(rows)
                if export_format == "csv":
                    response = HttpResponse(content_type="text/csv")
                    response["Content-Disposition"] = "attachment; filename=campaign-analytics.csv"
                    df.to_csv(path_or_buf=response, index=False)
                    return response
                elif export_format == "xlsx":
                    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    response["Content-Disposition"] = "attachment; filename=campaign-analytics.xlsx"
                    df.to_excel(response, index=False, engine='openpyxl')
                    return response

        return Response({
            "filters": {
                "start": start_date,
                "end": end_date,
            },
            "results": rows
        })