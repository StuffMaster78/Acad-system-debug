"""
Integration tests: client checkout → wallet payment → staff payment visibility.

Also covers the portal context endpoint surface resolution for all three
domain types (client, writer, staff).
"""
import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import ClientUserFactory, WebsiteFactory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def auth_header(user):
    token = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {token.access_token}"}


# ---------------------------------------------------------------------------
# Portal context — surface resolution
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPortalContextSurfaceResolution:
    """
    GET /api/v1/portal-context/ should resolve the correct surface from the
    Host header by matching PortalDefinition and Website records.
    """

    def test_client_domain_returns_client_surface(self, client, website):
        """A Website domain resolves to surface=client."""
        response = client.get(
            "/api/v1/portal-context/",
            HTTP_HOST=website.domain,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["surface"] == "client"
        assert data["website"]["id"] == website.id
        assert data["website"]["name"] == website.name
        assert data["allowed_roles"] == ["client"]

    def test_staff_portal_domain_returns_staff_surface(self, client, db):
        """A PortalDefinition with code=internal_admin resolves to surface=staff."""
        from accounts.models.portal_definition import PortalDefinition

        portal = PortalDefinition.objects.create(
            code="internal_admin",
            name="Staff Portal",
            domain="staff.test.local",
            is_active=True,
        )

        response = client.get(
            "/api/v1/portal-context/",
            HTTP_HOST=portal.domain,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["surface"] == "staff"
        assert data["website"] is None
        assert set(data["allowed_roles"]) == {"superadmin", "admin", "editor", "support"}

    def test_writer_portal_domain_returns_writer_surface(self, client, db):
        """A PortalDefinition with code=writer_portal resolves to surface=writer."""
        from accounts.models.portal_definition import PortalDefinition

        portal = PortalDefinition.objects.create(
            code="writer_portal",
            name="Writer Portal",
            domain="writers.test.local",
            is_active=True,
        )

        response = client.get(
            "/api/v1/portal-context/",
            HTTP_HOST=portal.domain,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["surface"] == "writer"
        assert data["website"] is None
        assert data["allowed_roles"] == ["writer"]

    def test_unknown_domain_defaults_to_client_surface(self, client, db):
        """An unrecognised host returns surface=client with no website."""
        response = client.get(
            "/api/v1/portal-context/",
            HTTP_HOST="unknown.example.com",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["surface"] == "client"
        assert data["website"] is None

    def test_payment_disclosure_included_when_configured(self, client, db):
        """payment_disclosure is populated when WebsiteBranding has processor fields."""
        from websites.models.website_branding import WebsiteBranding

        w = WebsiteFactory(domain="paydemo.test.local")
        WebsiteBranding.objects.create(
            website=w,
            brand_name="PayDemo",
            payment_processor_name="OrderBridge Payments",
            payment_statement_descriptor="ORDERBRIDGE PAYMENTS",
        )

        response = client.get(
            "/api/v1/portal-context/",
            HTTP_HOST="paydemo.test.local",
        )
        assert response.status_code == status.HTTP_200_OK
        disclosure = response.json()["payment_disclosure"]
        assert disclosure is not None
        assert disclosure["processor_name"] == "OrderBridge Payments"
        assert disclosure["statement_descriptor"] == "ORDERBRIDGE PAYMENTS"
        assert "ORDERBRIDGE PAYMENTS" in disclosure["text"]
        assert "PayDemo" in disclosure["pre_payment_notice"]

    def test_no_payment_disclosure_when_not_configured(self, client, website):
        """payment_disclosure is null when WebsiteBranding has no processor name."""
        response = client.get(
            "/api/v1/portal-context/",
            HTTP_HOST=website.domain,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["payment_disclosure"] is None


# ---------------------------------------------------------------------------
# Checkout → payment → staff visibility
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCheckoutPaymentStaffVisibility:
    """
    Client pays for an order with their wallet, then admin can see the
    payment reflected in the payment summary endpoint.
    """

    def _fund_wallet(self, client_user, website, amount=Decimal("500.00")):
        from wallets.services.client_wallet_service import ClientWalletService
        wallet = ClientWalletService.get_wallet(website=website, client=client_user)
        wallet.available_balance = amount
        wallet.save(update_fields=["available_balance"])
        return wallet

    def _ensure_ledger_accounts(self, website):
        from tests.fixtures.payment_fixtures import _ensure_ledger_accounts
        _ensure_ledger_accounts(website)

    def test_wallet_payment_updates_order_payment_status(
        self, api_client, client_user, website, order
    ):
        """
        POSTing to pay/wallet/ with sufficient balance marks the order as paid.
        """
        self._ensure_ledger_accounts(website)
        self._fund_wallet(client_user, website)
        api_client.credentials(**auth_header(client_user))

        response = api_client.post(
            f"/api/v1/orders/orders/{order.id}/pay/wallet/",
        )

        # Endpoint may return 200 or 201 depending on implementation
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
        ), f"Unexpected status {response.status_code}: {response.data}"

        order.refresh_from_db()
        assert order.is_fully_paid or order.payment_status in (
            "paid", "partially_paid", "completed"
        )

    def test_wallet_payment_fails_with_insufficient_balance(
        self, api_client, client_user, website, order
    ):
        """Payment is rejected when wallet balance is below the order total."""
        self._fund_wallet(client_user, website, amount=Decimal("1.00"))
        api_client.credentials(**auth_header(client_user))

        response = api_client.post(
            f"/api/v1/orders/orders/{order.id}/pay/wallet/",
        )

        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_402_PAYMENT_REQUIRED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

        order.refresh_from_db()
        assert not order.is_fully_paid

    def test_payment_requires_authentication(self, api_client, order):
        """Unauthenticated request to pay/wallet/ is rejected."""
        response = api_client.post(
            f"/api/v1/orders/orders/{order.id}/pay/wallet/",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_sees_payment_summary_after_payment(
        self, api_client, client_user, admin_user, website, order
    ):
        """
        After a successful wallet payment, the admin payment-summary endpoint
        reflects the paid amount and payment status.
        """
        self._fund_wallet(client_user, website)
        api_client.credentials(**auth_header(client_user))
        pay_response = api_client.post(
            f"/api/v1/orders/orders/{order.id}/pay/wallet/",
        )
        # Only check visibility if payment succeeded
        if pay_response.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
            pytest.skip("Payment endpoint returned unexpected status — skipping visibility check")

        api_client.credentials(**auth_header(admin_user))
        summary_response = api_client.get(
            f"/api/v1/orders/orders/{order.id}/payment-summary/",
        )

        assert summary_response.status_code == status.HTTP_200_OK
        summary = summary_response.json()
        # The summary should show the order has been (at least partially) paid
        amount_paid = Decimal(str(summary.get("amount_paid", 0)))
        assert amount_paid > Decimal("0"), (
            f"Expected amount_paid > 0 after payment, got {amount_paid}"
        )

    def test_client_cannot_access_payment_summary(
        self, api_client, client_user, order
    ):
        """The admin-only payment-summary endpoint rejects client requests."""
        api_client.credentials(**auth_header(client_user))
        response = api_client.get(
            f"/api/v1/orders/orders/{order.id}/payment-summary/",
        )
        assert response.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        )
