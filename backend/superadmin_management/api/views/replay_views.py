from rest_framework.views import APIView
from rest_framework.response import Response

from audit_logging.models.audit_event import AuditEvent
from governance.policies.models import PolicyDecisionLog
from event_system.models.event_outbox import EventOutbox


class CommandReplayView(APIView):

    def get(self, request, pk):
        audit_logs = AuditEvent.objects.filter(
            object_id=str(pk)
        ).order_by("created_at")

        decisions = PolicyDecisionLog.objects.filter(
            command_id=pk
        )

        events = EventOutbox.objects.filter(
            payload__contains={"command_id": str(pk)}
        )

        timeline = []

        # for a in audit_logs:
        # timeline.append({
        # "type": "audit",
        # "event": a.action,
        # "time": a.created_at,
        # })

        for d in decisions:
            timeline.append({
                "type": "policy",
                "decision": d.decision,
                "risk_score": d.risk_score,
                "time": d.created_at,
            })

        for e in events:
            timeline.append({
                "type": "event",
                "event_type": e.event_type,
                "time": e.created_at,
            })

        timeline.sort(key=lambda x: x["time"])

        return Response({
            "command_id": str(pk),
            "timeline": timeline,
        })