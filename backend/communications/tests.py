from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from communications.api.serializers import CommunicationThreadCreateSerializer
from communications.constants import CommunicationParticipantRole
from communications.constants import CommunicationThreadKind
from communications.integrations.registry import CommunicationAdapterRegistry
from communications.models import CommunicationMessage
from communications.models import CommunicationParticipant
from communications.models import CommunicationThread
from communications.selectors.message_selectors import CommunicationMessageSelector
from communications.selectors.thread_selectors import CommunicationThreadSelector
from files_management.enums import FileKind
from files_management.enums import FilePurpose
from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.models import ManagedFile
from files_management.policies.message_file_policy import MessageFilePolicy
from tickets.integrations.communication_adapter import TicketCommunicationAdapter
from tickets.models import Ticket
from websites.models.websites import Website


User = get_user_model()


class CommunicationIntegrationTests(TestCase):
    """
    Coverage for communication integration points used by tickets and files.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Gradecrest",
            domain="https://gradecrest.test",
        )
        self.client_user = User.objects.create_user(
            email="client@gradecrest.test",
            username="client",
            password="pass",
            role="client",
            website=self.website,
        )
        self.support_user = User.objects.create_user(
            email="support@gradecrest.test",
            username="support",
            password="pass",
            role="support",
            website=self.website,
        )
        self.outsider = User.objects.create_user(
            email="outsider@gradecrest.test",
            username="outsider",
            password="pass",
            role="client",
            website=self.website,
        )
        self.ticket = Ticket.objects.create(
            website=self.website,
            title="Payment question",
            description="Need help with a payment.",
            created_by=self.client_user,
            assigned_to=self.support_user,
            priority="medium",
            category="payment",
        )
        self.thread = CommunicationThread.objects.create(
            website=self.website,
            target_content_type=ContentType.objects.get_for_model(
                self.ticket,
            ),
            target_object_id=self.ticket.id,
            kind=CommunicationThreadKind.CLIENT_SUPPORT,
            created_by=self.client_user,
            subject=self.ticket.title,
            reference=f"TICKET-{self.ticket.id}",
        )
        CommunicationParticipant.objects.create(
            website=self.website,
            thread=self.thread,
            user=self.client_user,
            role=CommunicationParticipantRole.CLIENT,
        )
        CommunicationParticipant.objects.create(
            website=self.website,
            thread=self.thread,
            user=self.support_user,
            role=CommunicationParticipantRole.SUPPORT,
        )

    def test_thread_create_serializer_resolves_target_object(self) -> None:
        CommunicationAdapterRegistry.register(
            model=Ticket,
            adapter=TicketCommunicationAdapter(),
        )
        serializer = CommunicationThreadCreateSerializer(
            data={
                "target_app_label": "tickets",
                "target_model": "ticket",
                "target_object_id": self.ticket.id,
                "kind": CommunicationThreadKind.CLIENT_SUPPORT,
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["target"], self.ticket)

    def test_thread_and_message_selectors_use_active_participants(self) -> None:
        visible_message = CommunicationMessage.objects.create(
            website=self.website,
            thread=self.thread,
            sender=self.support_user,
            body="We can help.",
        )
        CommunicationMessage.objects.create(
            website=self.website,
            thread=self.thread,
            sender=self.support_user,
            body="Internal only.",
            is_internal=True,
        )

        client_threads = CommunicationThreadSelector.visible_to_user(
            website=self.website,
            user=self.client_user,
        )
        outsider_threads = CommunicationThreadSelector.visible_to_user(
            website=self.website,
            user=self.outsider,
        )
        client_messages = CommunicationMessageSelector.visible_for_thread(
            website=self.website,
            user=self.client_user,
            thread=self.thread,
        )

        self.assertIn(self.thread, client_threads)
        self.assertNotIn(self.thread, outsider_threads)
        self.assertEqual(list(client_messages), [visible_message])

    def test_message_file_policy_recognizes_communication_messages(self) -> None:
        message = CommunicationMessage.objects.create(
            website=self.website,
            thread=self.thread,
            sender=self.support_user,
            body="See the attached reference.",
        )
        managed_file = ManagedFile.objects.create(
            website=self.website,
            uploaded_by=self.support_user,
            file="managed-files/reference.pdf",
            original_name="reference.pdf",
            file_size=128,
            mime_type="application/pdf",
            file_kind=FileKind.DOCUMENT,
            storage_key="managed-files/reference.pdf",
        )
        attachment = FileAttachment.objects.create(
            website=self.website,
            managed_file=managed_file,
            content_object=message,
            purpose=FilePurpose.MESSAGE_ATTACHMENT,
            visibility=FileVisibility.CONVERSATION_PARTICIPANTS,
            attached_by=self.support_user,
        )
        policy = MessageFilePolicy()

        self.assertTrue(policy.supports(attachment=attachment))
        self.assertTrue(
            policy.can_view(user=self.client_user, attachment=attachment),
        )
        self.assertFalse(policy.can_view(user=self.outsider, attachment=attachment))
