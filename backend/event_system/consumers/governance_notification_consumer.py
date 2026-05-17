from notifications_system.services.notification_service import NotificationService


class GovernanceNotificationConsumer:

    @staticmethod
    def handle(event) -> None:

        if event.event_type == "approval.node.approved":
            NotificationService.notify_role(
                event_key="approval.node.approved",
                website=None,
                role="superadmin",
                context={
                    "message":(
                        f"Approval completed for workflow {event.workflow_id}"
                    ),
                }
            )

        if event.event_type == "approval.node.rejected":
            NotificationService.notify_role(
                event_key="approval.node.rejected",
                role="admin",
                website=None,
                context={
                    "message":f"Approval rejected in workflow {event.workflow_id}",
                }
            )