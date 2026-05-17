from rest_framework import viewsets
from rest_framework.response import Response

from superadmin_management.commands.models import Command


class CommandViewSet(viewsets.ViewSet):

    def list(self, request):
        commands = Command.objects.all().order_by("-created_at")
        return Response([self._serialize(c) for c in commands])

    def retrieve(self, request, pk=None):
        command = Command.objects.get(id=pk)
        return Response(self._serialize(command))

    def _serialize(self, c):
        return {
            "id": str(c.id),
            "type": c.command_type,
            "status": c.status,
            "payload": c.payload,
            "requires_approval": c.requires_approval,
            "tenant_id": c.tenant_id,
            "actor_id": c.actor_id,
        }