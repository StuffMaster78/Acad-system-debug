from event_system.registry import EventRegistry
from event_system.consumers.governance_notification_consumer import GovernanceNotificationConsumer
from event_system.consumers.governance_audit_consumer import GovernanceAuditConsumer


def register_governance_events() -> None:

    EventRegistry.register("approval.node.started", GovernanceAuditConsumer.handle)
    EventRegistry.register("approval.node.approved", GovernanceAuditConsumer.handle)
    EventRegistry.register("approval.node.rejected", GovernanceAuditConsumer.handle)

    EventRegistry.register("approval.node.approved", GovernanceNotificationConsumer.handle)
    EventRegistry.register("approval.node.rejected", GovernanceNotificationConsumer.handle)