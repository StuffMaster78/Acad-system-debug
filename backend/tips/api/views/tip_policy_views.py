from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from tips.api.serializers.tip_policy_serializers import TipPolicySerializer
from tips.models.tip_policy import TipPolicy
from rest_framework.permissions import IsAdminUser


class TipPolicyUpdateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, policy_id: int):
        policy = TipPolicy.objects.get(id=policy_id)

        serializer = TipPolicySerializer(
            policy,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    

class TipPolicyAPIView(APIView):

    def get(self, request):
        policy = TipPolicy.objects.filter(is_active=True).first()
        return Response(TipPolicySerializer(policy).data)