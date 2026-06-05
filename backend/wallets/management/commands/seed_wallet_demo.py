from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models.portal_definition import PortalDefinition
from accounts.models import AccountRole, PermissionDefinition, RoleDefinition, RolePermission
from accounts.services.portal_access_service import PortalAccessService
from accounts.services.tenant_access_service import TenantAccessService
from accounts.services.account_service import AccountService
from wallets.constants import WalletEntryType, WalletStatus, WalletType
from wallets.models import Wallet, WalletEntry, WalletHold
from wallets.services.wallet_hold_service import WalletHoldService
from wallets.services.wallet_service import WalletService
from websites.models.websites import Website


REFERENCE_TYPE = "wallet_demo_seed"


@dataclass(frozen=True)
class DemoWalletSpec:
    email: str
    first_name: str
    last_name: str
    role: str
    wallet_type: str
    credits: tuple[tuple[str, Decimal, str], ...]
    debits: tuple[tuple[str, Decimal, str], ...] = ()
    hold: tuple[Decimal, str, str] | None = None
    status: str = WalletStatus.ACTIVE


DEMO_WALLETS: tuple[DemoWalletSpec, ...] = (
    DemoWalletSpec(
        email="demo.client.ada@example.com",
        first_name="Ada",
        last_name="Client",
        role="client",
        wallet_type=WalletType.CLIENT,
        credits=(
            ("DEMO-ADA-TOPUP-001", Decimal("250.00"), "Card wallet top-up for order checkout"),
            ("DEMO-ADA-REFUND-001", Decimal("42.00"), "Partial refund returned to wallet"),
        ),
        debits=(("DEMO-ADA-ORDER-001", Decimal("118.00"), "Order payment captured from wallet"),),
    ),
    DemoWalletSpec(
        email="demo.client.noah@example.com",
        first_name="Noah",
        last_name="Client",
        role="client",
        wallet_type=WalletType.CLIENT,
        credits=(("DEMO-NOAH-TOPUP-001", Decimal("640.00"), "Bulk top-up for upcoming class orders"),),
        debits=(("DEMO-NOAH-ORDER-001", Decimal("185.00"), "Order payment captured from wallet"),),
        hold=(Decimal("120.00"), "Pending split-payment review", "DEMO-NOAH-HOLD-001"),
    ),
    DemoWalletSpec(
        email="demo.client.mira@example.com",
        first_name="Mira",
        last_name="Client",
        role="client",
        wallet_type=WalletType.CLIENT,
        credits=(("DEMO-MIRA-TOPUP-001", Decimal("75.00"), "Manual admin goodwill credit"),),
    ),
    DemoWalletSpec(
        email="demo.writer.eli@example.com",
        first_name="Eli",
        last_name="Writer",
        role="writer",
        wallet_type=WalletType.WRITER,
        credits=(
            ("DEMO-ELI-EARNING-001", Decimal("180.00"), "Writer earning posted for approved order"),
            ("DEMO-ELI-BONUS-001", Decimal("25.00"), "Quality bonus posted by admin"),
        ),
        debits=(("DEMO-ELI-PAYOUT-001", Decimal("60.00"), "Writer payout debit"),),
    ),
    DemoWalletSpec(
        email="demo.writer.zara@example.com",
        first_name="Zara",
        last_name="Writer",
        role="writer",
        wallet_type=WalletType.WRITER,
        credits=(("DEMO-ZARA-EARNING-001", Decimal("410.00"), "Writer earning posted for completed class work"),),
        hold=(Decimal("85.00"), "Payout reserve under review", "DEMO-ZARA-HOLD-001"),
    ),
    DemoWalletSpec(
        email="demo.writer.kai@example.com",
        first_name="Kai",
        last_name="Writer",
        role="writer",
        wallet_type=WalletType.WRITER,
        credits=(("DEMO-KAI-EARNING-001", Decimal("95.00"), "Writer earning posted for approved diagram work"),),
        debits=(("DEMO-KAI-PENALTY-001", Decimal("15.00"), "Admin penalty adjustment"),),
        status=WalletStatus.SUSPENDED,
    ),
)


class Command(BaseCommand):
    help = "Seed tenant-scoped demo wallet data for admin and superadmin wallet UI review."

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            default="http://localhost",
            help="Website domain to seed against. Defaults to http://localhost.",
        )
        parser.add_argument(
            "--name",
            default="Wallet Demo Website",
            help="Website name to create when the domain does not exist.",
        )

    def handle(self, *args, **options):
        website = self._get_or_create_website(
            domain=options["domain"],
            name=options["name"],
        )
        actor = self._get_or_create_user(
            website=website,
            email="demo.wallet.admin@example.com",
            first_name="Demo",
            last_name="Admin",
            role="admin",
            is_staff=True,
        )
        self._grant_staff_access(user=actor, website=website)

        seeded_wallets: list[Wallet] = []
        for spec in DEMO_WALLETS:
            user = self._get_or_create_user(
                website=website,
                email=spec.email,
                first_name=spec.first_name,
                last_name=spec.last_name,
                role=spec.role,
            )
            wallet = WalletService.get_or_create_wallet(
                website=website,
                owner_user=user,
                wallet_type=spec.wallet_type,
                currency="USD",
            )
            self._reset_demo_wallet(wallet)

            for reference, amount, description in spec.credits:
                WalletService.credit_wallet(
                    wallet=wallet,
                    website=website,
                    amount=amount,
                    entry_type=self._credit_entry_type(spec.wallet_type, description),
                    created_by=actor,
                    description=description,
                    reference=reference,
                    reference_type=REFERENCE_TYPE,
                    metadata={"seeded": True},
                )

            for reference, amount, description in spec.debits:
                WalletService.debit_wallet(
                    wallet=wallet,
                    website=website,
                    amount=amount,
                    entry_type=self._debit_entry_type(description),
                    created_by=actor,
                    description=description,
                    reference=reference,
                    reference_type=REFERENCE_TYPE,
                    metadata={"seeded": True},
                )

            if spec.hold:
                amount, reason, reference = spec.hold
                WalletHoldService.create_hold(
                    wallet=wallet,
                    website=website,
                    amount=amount,
                    reason=reason,
                    created_by=actor,
                    reference=reference,
                    reference_type=REFERENCE_TYPE,
                    expires_at=timezone.now() + timezone.timedelta(days=7),
                    metadata={"seeded": True},
                )

            wallet.refresh_from_db()
            if spec.status != WalletStatus.ACTIVE:
                wallet.status = spec.status
                wallet.save(update_fields=["status", "updated_at"])
                wallet.refresh_from_db()
            seeded_wallets.append(wallet)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(seeded_wallets)} demo wallets for {website.name} "
                f"({website.domain})."
            )
        )
        for wallet in seeded_wallets:
            owner = wallet.owner_user
            self.stdout.write(
                f"- #{wallet.id} {wallet.wallet_type} {owner.email}: "
                f"available={wallet.available_balance} pending={wallet.pending_balance} "
                f"status={wallet.status}"
            )

    def _get_or_create_website(self, *, domain: str, name: str) -> Website:
        website = Website.objects.filter(domain=domain).first()
        if website is None:
            base_name = name
            suffix = 1
            while Website.objects.filter(name=name).exists():
                suffix += 1
                name = f"{base_name} {suffix}"
            website = Website.objects.create(
                domain=domain,
                name=name,
                is_active=True,
                is_deleted=False,
                allow_registration=True,
            )
        else:
            Website.objects.filter(pk=website.pk).update(
                is_active=True,
                is_deleted=False,
                allow_registration=True,
            )
            website.refresh_from_db()
        return website

    def _get_or_create_user(
        self,
        *,
        website: Website,
        email: str,
        first_name: str,
        last_name: str,
        role: str,
        is_staff: bool = False,
    ):
        User = get_user_model()
        user, _created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "website": website,
                "is_active": True,
                "is_staff": is_staff,
            },
        )
        User.objects.filter(pk=user.pk).update(
            username=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            website=website,
            is_active=True,
            is_staff=is_staff,
            is_superuser=role == "superadmin",
        )
        user.refresh_from_db()
        return user

    def _grant_staff_access(self, *, user, website: Website) -> None:
        portal, _created = PortalDefinition.objects.get_or_create(
            code="internal_admin",
            defaults={
                "name": "Internal Admin",
                "domain": "ordermanagement.com",
                "is_active": True,
            },
        )
        if not portal.is_active:
            portal.is_active = True
            portal.save(update_fields=["is_active"])
        PortalAccessService.grant_portal_access(
            user=user,
            portal_code="internal_admin",
            granted_by=user,
        )
        TenantAccessService.grant_access(
            user=user,
            website=website,
            granted_by=user,
        )
        profile = AccountService.get_or_create_account_profile(
            website=website,
            user=user,
            actor=user,
            is_primary=True,
            metadata={"source": "wallet_demo_seed"},
        )
        role, _created = RoleDefinition.objects.update_or_create(
            website=website,
            key="admin",
            defaults={
                "name": "Admin",
                "description": "Tenant administrator.",
                "is_system_role": True,
                "is_active": True,
            },
        )
        AccountRole.objects.update_or_create(
            website=website,
            account_profile=profile,
            role=role,
            defaults={
                "is_active": True,
                "assigned_by": user,
                "metadata": {"source": "wallet_demo_seed"},
            },
        )
        for code, name in (
            ("wallets.view", "View Wallets"),
            ("wallets.adjust", "Adjust Wallets"),
            ("wallets.manage_holds", "Manage Wallet Holds"),
            ("wallets.reconcile", "Reconcile Wallets"),
            ("ledger.view", "View Ledger"),
            ("payments.view", "View Payments"),
        ):
            permission, _created = PermissionDefinition.objects.update_or_create(
                code=code,
                defaults={"name": name, "is_active": True},
            )
            RolePermission.objects.update_or_create(
                role=role,
                permission=permission,
                defaults={"is_active": True},
            )

    def _reset_demo_wallet(self, wallet: Wallet) -> None:
        WalletHold.objects.filter(wallet=wallet, reference_type=REFERENCE_TYPE).delete()
        WalletEntry.objects.filter(wallet=wallet, reference_type=REFERENCE_TYPE).delete()
        Wallet.objects.filter(pk=wallet.pk).update(
            status=WalletStatus.ACTIVE,
            available_balance=Decimal("0.00"),
            pending_balance=Decimal("0.00"),
            total_credited=Decimal("0.00"),
            total_debited=Decimal("0.00"),
            last_activity_at=None,
        )
        wallet.refresh_from_db()

    def _credit_entry_type(self, wallet_type: str, description: str) -> str:
        lowered = description.lower()
        if wallet_type == WalletType.WRITER:
            if "bonus" in lowered:
                return WalletEntryType.BONUS
            return WalletEntryType.EARNING
        if "refund" in lowered:
            return WalletEntryType.ORDER_REFUND
        return WalletEntryType.FUNDING

    def _debit_entry_type(self, description: str) -> str:
        lowered = description.lower()
        if "penalty" in lowered:
            return WalletEntryType.PENALTY
        if "payout" in lowered:
            return WalletEntryType.PAYOUT_SETTLED
        return WalletEntryType.ORDER_PAYMENT
