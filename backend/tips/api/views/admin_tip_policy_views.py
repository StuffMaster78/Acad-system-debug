# tips/api/views/admin_tip_policy_views.py
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from tips.models.tip_policy import TipPolicy
from tips.api.serializers.tip_policy_serializers import (
    TipPolicySerializer,
    TipPolicyUpdateSerializer,
)
from tips.services.tip_policy_activation_service import TipPolicyActivationService


class AdminTipPolicyListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = TipPolicy.objects.order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TipPolicyUpdateSerializer
        return TipPolicySerializer


class AdminTipPolicyDetailAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = TipPolicy.objects.all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return TipPolicyUpdateSerializer
        return TipPolicySerializer


class AdminActivateTipPolicyAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            policy = TipPolicy.objects.get(pk=pk)
        except TipPolicy.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        activated_policy = TipPolicyActivationService.activate(
            policy=policy,
            triggered_by=request.user,
        )
        return Response(TipPolicySerializer(activated_policy).data, status=status.HTTP_200_OK)
