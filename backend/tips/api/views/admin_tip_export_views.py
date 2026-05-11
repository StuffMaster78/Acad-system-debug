# tips/api/views/admin_tip_export_views.py

import csv

from django.http import HttpResponse

from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from tips.models.tip import Tip


class AdminTipExportCSVAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        response = HttpResponse(
            content_type="text/csv"
        )

        response[
            "Content-Disposition"
        ] = 'attachment; filename="tips.csv"'

        writer = csv.writer(response)

        writer.writerow([
            "ID",
            "Sender",
            "Receiver",
            "Amount",
            "Status",
            "Created",
        ])

        tips = (
            Tip.objects
            .select_related(
                "sender",
                "receiver",
            )
            .order_by("-created_at")
        )

        for tip in tips:

            writer.writerow([
                tip.pk,
                getattr(
                    tip.sender,
                    "email",
                    "",
                ),
                getattr(
                    tip.receiver,
                    "email",
                    "",
                ),
                tip.gross_amount,
                tip.status,
                tip.created_at,
            ])

        return response


class AdminSettlementExportAPIView(
    APIView
):

    permission_classes = [IsAdminUser]

    def get(self, request):

        response = HttpResponse(
            content_type="text/csv"
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; '
            'filename="settlements.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            "Tip ID",
            "Gross",
            "Writer Share",
            "Platform Fee",
            "Status",
            "Settled At",
        ])

        tips = (
            Tip.objects
            .filter(status="settled")
            .order_by("-created_at")
        )

        for tip in tips:

            writer.writerow([
                tip.pk,
                tip.gross_amount,
                tip.writer_share_cents,
                tip.platform_fee_cents,
                tip.status,
                tip.settled_at,
            ])

        return response