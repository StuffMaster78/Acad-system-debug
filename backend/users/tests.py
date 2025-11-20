from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now
from rest_framework.test import APIClient
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile

User = get_user_model()


class UserSignalsTest(TestCase):
    """
    Tests for user-related signals.
    """

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="clientuser",
            email="client@example.com",
            password="password123",
            role="client",
        )
        self.writer_user = User.objects.create_user(
            username="writeruser",
            email="writer@example.com",
            password="password123",
            role="writer",
        )
        self.editor_user = User.objects.create_user(
            username="editoruser",
            email="editor@example.com",
            password="password123",
            role="editor",
        )
        self.support_user = User.objects.create_user(
            username="supportuser",
            email="support@example.com",
            password="password123",
            role="support",
        )

    def test_client_profile_created(self):
        self.assertTrue(
            ClientProfile.objects.filter(user=self.client_user).exists(),
            "Client profile should be created when a user with role 'client' is created.",
        )

    def test_writer_profile_created(self):
        self.assertTrue(
            WriterProfile.objects.filter(user=self.writer_user).exists(),
            "Writer profile should be created when a user with role 'writer' is created.",
        )

    def test_editor_profile_created(self):
        self.assertTrue(
            EditorProfile.objects.filter(user=self.editor_user).exists(),
            "Editor profile should be created when a user with role 'editor' is created.",
        )

    def test_support_profile_created(self):
        self.assertTrue(
            SupportProfile.objects.filter(user=self.support_user).exists(),
            "Support profile should be created when a user with role 'support' is created.",
        )


class UserGeolocationTest(TestCase):
    """
    Tests for geolocation updates on login.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role="client",
        )

    def test_geolocation_update_on_login(self):
        self.client.login(username="testuser", password="password123")
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_active, "Last active timestamp should be updated on login.")

    def test_geolocation_country_update(self):
        self.client.login(username="testuser", password="password123")
        self.user.refresh_from_db()
        self.assertTrue(
            hasattr(self.user.client_profile, "country"),
            "Country field in the client profile should be updated during login.",
        )


class UserModelTest(TestCase):
    """
    Tests for User model methods.
    """

    def test_suspension_methods(self):
        user = User.objects.create_user(username="testuser", role="client")
        user.suspend(reason="Violation of terms")
        self.assertTrue(user.is_suspended, "User should be suspended.")
        self.assertEqual(user.suspension_reason, "Violation of terms", "Suspension reason should be saved.")

        user.lift_suspension()
        self.assertFalse(user.is_suspended, "User suspension should be lifted.")
        self.assertIsNone(user.suspension_reason, "Suspension reason should be cleared after lifting.")

    def test_probation_methods(self):
        user = User.objects.create_user(username="testuser", role="client")
        user.place_on_probation(reason="Poor performance")
        self.assertTrue(user.is_on_probation, "User should be placed on probation.")
        self.assertEqual(user.probation_reason, "Poor performance", "Probation reason should be saved.")

        user.remove_from_probation()
        self.assertFalse(user.is_on_probation, "User should be removed from probation.")
        self.assertIsNone(user.probation_reason, "Probation reason should be cleared after removal.")

    def test_freeze_account(self):
        user = User.objects.create_user(username="testuser", role="client")
        user.freeze_account()
        self.assertFalse(user.is_active, "User account should be inactive after freezing.")
        self.assertTrue(user.is_frozen, "User account should be marked as frozen.")
        self.assertIsNotNone(user.deletion_date, "Deletion date should be set after freezing.")

    def test_reinstate_account(self):
        user = User.objects.create_user(username="testuser", role="client")
        user.freeze_account()
        user.reinstate_account()
        self.assertTrue(user.is_active, "User account should be active after reinstating.")
        self.assertFalse(user.is_frozen, "User account should not be frozen after reinstating.")
        self.assertIsNone(user.deletion_date, "Deletion date should be cleared after reinstating.")

    def test_impersonation_methods(self):
        admin = User.objects.create_user(username="adminuser", role="admin")
        user = User.objects.create_user(username="testuser", role="client")
        user.impersonate(admin)
        self.assertTrue(user.is_impersonated, "User should be marked as impersonated.")
        self.assertEqual(user.impersonated_by, admin, "Impersonator should be saved.")

        user.stop_impersonation()
        self.assertFalse(user.is_impersonated, "User impersonation should be stopped.")
        self.assertIsNone(user.impersonated_by, "Impersonator should be cleared after stopping impersonation.")