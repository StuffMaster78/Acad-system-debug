from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from tips.api.serializers.tip_attribution_serializers import (
    TipAttributionSerializer
)
from tips.models.tip_attribution import TipAttribution


class TipAttributionAPIView(APIView):

    def get(self, request, tip_id: int):

        attribution = TipAttribution.objects.filter(
            tip_id=tip_id
        ).first()

        if not attribution:
            return Response({"detail": "Not found"}, status=404)

        return Response(TipAttributionSerializer(attribution).data)