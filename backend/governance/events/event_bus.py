from event_system.services.event_dispatcher_service import EventDispatcherService


class GovernanceEventBus:
    """
    Bridge:
    governance → event_system
    """

    @staticmethod
    def emit(event) -> None:

        EventDispatcherService.dispatch(
            event_type=event.event_type,
            payload={
                "workflow_id": event.workflow_id,
                "node_id": event.node_id,
                "actor_id": event.actor_id,
                "data": event.payload,
            },
            tenant_id=event.tenant_id,
            actor=event.actor,
            # idempotency_key=idempotency_key,
        )