from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import (
    Ticket, TicketMessage, TicketAttachment,
    TicketLog, TicketStatistics
)
from unittest.mock import patch

User = get_user_model()

class TicketAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.local', username='admin', password='pass', role='admin')
        self.support = User.objects.create_user(email='support@test.local', username='support', password='pass', role='support')
        self.writer = User.objects.create_user(email='writer@test.local', username='writer', password='pass', role='writer')
        self.client_user = User.objects.create_user(email='client@test.local', username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Description",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    def test_ticket_creation_by_client(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('ticket-list')
        data = {
            "title": "New Ticket",
            "description": "Details",
            "priority": "low",
            "category": "general",
            "status": "open"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_by'], self.client_user.id)

    def test_ticket_assignment_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-assign', args=[self.ticket.id])
        response = self.client.post(url, {"assigned_to": self.support.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.support)

    def test_ticket_escalation_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-escalate', args=[self.ticket.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.priority, 'critical')
        self.assertTrue(self.ticket.is_escalated)

    def test_writer_can_only_see_own_tickets(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_admin_can_see_all_tickets(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

class TicketMessageAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.local', username='admin', password='pass', role='admin')
        self.client_user = User.objects.create_user(email='client@test.local', username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Description",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    def test_message_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-message-list')
        data = {
            "ticket": self.ticket.id,
            "content": "Admin reply"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender'], self.admin.id)

    def test_client_can_only_see_own_messages(self):
        msg = TicketMessage.objects.create(ticket=self.ticket, sender=self.admin, content="Admin reply")
        self.client.force_authenticate(user=self.client_user)
        url = reverse('ticket-message-list')
        response = self.client.get(url)
        # Client should not see admin's message (if filtered by sender)
        self.assertEqual(len(response.data), 0)

class TicketAttachmentAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.local', username='admin', password='pass', role='admin')
        self.writer = User.objects.create_user(email='writer@test.local', username='writer', password='pass', role='writer')
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Description",
            created_by=self.writer,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    def test_attachment_upload_by_writer(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-attachment-list')
        with open(__file__, 'rb') as fp:
            data = {
                "ticket": self.ticket.id,
                "file": fp
            }
            response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['uploaded_by'], self.writer.id)

    def test_writer_can_only_see_own_attachments(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-attachment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see own attachments
        for att in response.data:
            self.assertEqual(att['uploaded_by'], self.writer.id)

class TicketNotificationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.local', username='admin', password='pass', role='admin')
        self.support = User.objects.create_user(email='support@test.local', username='support', password='pass', role='support')
        self.client_user = User.objects.create_user(email='client@test.local', username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Notify Ticket",
            description="Test",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    @patch('tickets.views.notify_user')
    def test_escalation_sends_notification(self, mock_notify):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-escalate', args=[self.ticket.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_notify.called)

    @patch('tickets.views.notify_user')
    def test_assignment_sends_notification(self, mock_notify):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-assign', args=[self.ticket.id])
        response = self.client.post(url, {"assigned_to": self.support.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_notify.called)

    @patch('tickets.views.notify_user')
    def test_ticket_closed_sends_notification(self, mock_notify):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-detail', args=[self.ticket.id])
        data = {
            "status": "closed",
            "title": self.ticket.title,
            "description": self.ticket.description,
            "priority": self.ticket.priority,
            "category": self.ticket.category
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_notify.called)

class TicketAttachmentPermissionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.local', username='admin', password='pass', role='admin')
        self.writer = User.objects.create_user(email='writer@test.local', username='writer', password='pass', role='writer')
        self.client_user = User.objects.create_user(email='client@test.local', username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Attachment Ticket",
            description="Test",
            created_by=self.writer,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )
        with open(__file__, 'rb') as fp:
            self.attachment = TicketAttachment.objects.create(
                ticket=self.ticket,
                uploaded_by=self.writer,
                file=fp
            )

    def test_admin_can_download_attachment(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-attachment-detail', args=[self.attachment.id])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_writer_cannot_download_attachment(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-attachment-detail', args=[self.attachment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_cannot_download_attachment(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('ticket-attachment-detail', args=[self.attachment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TicketStatisticsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.client_user = User.objects.create_user(username='client', password='pass', role='client')
        Ticket.objects.create(
            title="Stat Ticket 1",
            description="Test",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='closed'
        )
        Ticket.objects.create(
            title="Stat Ticket 2",
            description="Test",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='high',
            category='general',
            status='open'
        )

    def test_statistics_endpoint(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticketstatistics-generate-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tickets', response.data)
        self.assertIn('resolved_tickets', response.data)


class TicketAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.support = User.objects.create_user(username='support', password='pass', role='support')
        self.writer = User.objects.create_user(username='writer', password='pass', role='writer')
        self.client_user = User.objects.create_user(username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Description",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    def test_ticket_creation_by_client(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('ticket-list')
        data = {
            "title": "New Ticket",
            "description": "Details",
            "priority": "low",
            "category": "general",
            "status": "open"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_by'], self.client_user.id)

    def test_ticket_assignment_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-assign', args=[self.ticket.id])
        response = self.client.post(url, {"assigned_to": self.support.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.support)

    def test_ticket_escalation_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-escalate', args=[self.ticket.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.priority, 'critical')
        self.assertTrue(self.ticket.is_escalated)

    def test_writer_can_only_see_own_tickets(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_admin_can_see_all_tickets(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

class TicketMessageAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.client_user = User.objects.create_user(username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Description",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    def test_message_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-message-list')
        data = {
            "ticket": self.ticket.id,
            "content": "Admin reply"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender'], self.admin.id)

    def test_client_can_only_see_own_messages(self):
        TicketMessage.objects.create(ticket=self.ticket, sender=self.admin, content="Admin reply")
        self.client.force_authenticate(user=self.client_user)
        url = reverse('ticket-message-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)

class TicketAttachmentAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.writer = User.objects.create_user(username='writer', password='pass', role='writer')
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            description="Test Description",
            created_by=self.writer,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    def test_attachment_upload_by_writer(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-attachment-list')
        with open(__file__, 'rb') as fp:
            data = {
                "ticket": self.ticket.id,
                "file": fp
            }
            response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['uploaded_by'], self.writer.id)

    def test_writer_can_only_see_own_attachments(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-attachment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for att in response.data:
            self.assertEqual(att['uploaded_by'], self.writer.id)

class TicketNotificationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.support = User.objects.create_user(username='support', password='pass', role='support')
        self.client_user = User.objects.create_user(username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Notify Ticket",
            description="Test",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    @patch('tickets.views.notify_user')
    def test_escalation_sends_notification(self, mock_notify):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-escalate', args=[self.ticket.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_notify.called)

    @patch('tickets.views.notify_user')
    def test_assignment_sends_notification(self, mock_notify):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-assign', args=[self.ticket.id])
        response = self.client.post(url, {"assigned_to": self.support.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_notify.called)

    @patch('tickets.views.notify_user')
    def test_ticket_closed_sends_notification(self, mock_notify):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-detail', args=[self.ticket.id])
        data = {
            "status": "closed",
            "title": self.ticket.title,
            "description": self.ticket.description,
            "priority": self.ticket.priority,
            "category": self.ticket.category
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_notify.called)

class TicketAttachmentPermissionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.writer = User.objects.create_user(username='writer', password='pass', role='writer')
        self.client_user = User.objects.create_user(username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Attachment Ticket",
            description="Test",
            created_by=self.writer,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )
        with open(__file__, 'rb') as fp:
            self.attachment = TicketAttachment.objects.create(
                ticket=self.ticket,
                uploaded_by=self.writer,
                file=fp
            )

    def test_admin_can_download_attachment(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-attachment-detail', args=[self.attachment.id])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_writer_cannot_download_attachment(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-attachment-detail', args=[self.attachment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_cannot_download_attachment(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('ticket-attachment-detail', args=[self.attachment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TicketStatisticsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.client_user = User.objects.create_user(username='client', password='pass', role='client')
        Ticket.objects.create(
            title="Stat Ticket 1",
            description="Test",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='closed'
        )
        Ticket.objects.create(
            title="Stat Ticket 2",
            description="Test",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='high',
            category='general',
            status='open'
        )

    def test_statistics_endpoint(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticketstatistics-generate-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tickets', response.data)
        self.assertIn('resolved_tickets', response.data)


class TicketEdgeCaseTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.writer = User.objects.create_user(username='writer', password='pass', role='writer')
        self.client_user = User.objects.create_user(username='client', password='pass', role='client')
        self.ticket = Ticket.objects.create(
            title="Edge Ticket",
            description="Edge Description",
            created_by=self.client_user,
            assigned_to=self.admin,
            priority='medium',
            category='general',
            status='open'
        )

    def test_ticket_creation_missing_fields(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('ticket-list')
        data = {"title": "Incomplete Ticket"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_ticket_assignment(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-assign', args=[self.ticket.id])
        response = self.client.post(url, {"assigned_to": self.writer.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_double_assignment(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-assign', args=[self.ticket.id])
        # First assignment
        response1 = self.client.post(url, {"assigned_to": self.writer.id})
        # Second assignment to same user
        response2 = self.client.post(url, {"assigned_to": self.writer.id})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.writer)

    def test_escalate_already_escalated_ticket(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-escalate', args=[self.ticket.id])
        # First escalation
        response1 = self.client.post(url)
        # Second escalation
        response2 = self.client.post(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertTrue(self.ticket.is_escalated)
        self.assertEqual(self.ticket.priority, 'critical')

    def test_ticket_update_by_non_creator(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-detail', args=[self.ticket.id])
        data = {"title": "Hacked Title"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_attachment_upload_invalid_file(self):
        self.client.force_authenticate(user=self.writer)
        url = reverse('ticket-attachment-list')
        # No file provided
        data = {"ticket": self.ticket.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attachment_upload_to_other_users_ticket(self):
        other_ticket = Ticket.objects.create(
            title="Other Ticket",
            description="Other",
            created_by=self.admin,
            assigned_to=self.writer,
            priority='medium',
            category='general',
            status='open'
        )
        self.client.force_authenticate(user=self.client_user)
        url = reverse('ticket-attachment-list')
        with open(__file__, 'rb') as fp:
            data = {"ticket": other_ticket.id, "file": fp}
            response = self.client.post(url, data, format='multipart')
        # Should be forbidden if permissions are enforced
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

    def test_download_nonexistent_attachment(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-attachment-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_statistics_endpoint_unauthenticated(self):
        url = reverse('ticketstatistics-generate-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)