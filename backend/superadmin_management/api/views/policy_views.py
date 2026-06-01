from rest_framework import viewsets
from rest_framework.response import Response

from governance.policies.models import Policy


class PolicyViewSet(viewsets.ViewSet):

    def list(self, request):
        policies = Policy.objects.filter(is_active=True)
        return Response([self._serialize(p) for p in policies])

    def retrieve(self, request, pk=None):
        policy = Policy.objects.get(id=pk)
        return Response(self._serialize(policy))

    def create(self, request):
        policy = Policy.objects.create(
            name=request.data["name"],
            rule=request.data["rule"], # graph JSON
            effect=request.data["effect"],
            tenant_id=request.data.get("tenant_id"),
        )
        return Response(self._serialize(policy))

    def update(self, request, pk=None):
        policy = Policy.objects.get(id=pk)
        policy.rule = request.data.get("rule", policy.rule)
        policy.effect = request.data.get("effect", policy.effect)
        policy.save()
        return Response(self._serialize(policy))

    def _serialize(self, policy):
        return {
            "id": str(policy.id),
            "name": policy.name,
            "rule": policy.rule, # graph editor uses this
            "effect": policy.effect,
            "version": policy.version,
            "priority": policy.priority,
        }