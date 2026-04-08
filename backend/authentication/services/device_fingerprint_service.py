import hashlib
import json
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from authentication.models.device_fingerprinting import (
    DeviceFingerprint,
)
from authentication.services.auth_service import AuthenticationService

class DeviceFingerprintService:
    """
    Handle device fingerprint persistence, trust state, and risk
    evaluation for a user within a website context.

    This service is responsible for:
        - creating or updating fingerprint records
        - managing trust state
        - calculating simple risk scores
        - identifying suspicious device activity

    Notification delivery and alert logging should be handled by a
    separate alert or notification service.
    """

    DEFAULT_AUTO_TRUST_AFTER_LOGINS = 5
    

    def __init__(
        self,
        user,
        website,
        trust_after_logins: int | None = None,
    ):
        """
        Initialize the device fingerprint service.

        Args:
            user: The user tied to the fingerprint.
            website: The tenant or website context.
            trust_after_logins: Number of successful logins required
                before a device is auto-trusted.
        """
        self.user = user
        self.website = website
        if website is None:
            raise ValidationError("Website context is required.")
        self.trust_after_logins = (
            trust_after_logins
            or self.DEFAULT_AUTO_TRUST_AFTER_LOGINS
        )

    @staticmethod
    def hash_fingerprint_data(raw_data: dict[str, Any] | str) -> str:
        """
        Hash raw fingerprint data using SHA-256.

        Args:
            raw_data: Raw fingerprint payload as a dictionary or string.

        Returns:
            SHA-256 hash of the normalized fingerprint data.

        Raises:
            ValueError: If raw fingerprint data is empty.
        """
        if not raw_data:
            raise ValueError("Fingerprint data cannot be empty.")

        if isinstance(raw_data, dict):
            raw_data = json.dumps(raw_data, sort_keys=True)

        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()


    @transaction.atomic
    def create_or_update_fingerprint(
        self,
        fingerprint_data: dict[str, Any],
    ) -> DeviceFingerprint:
        """
        Create or update a device fingerprint record.

        Args:
            fingerprint_data: Fingerprint payload including:
                - raw_fingerprint_data
                - user_agent
                - device_name
                - ip_address

        Returns:
            The created or updated DeviceFingerprint instance.
        """
        fingerprint_hash = fingerprint_data.get("fingerprint_hash")

        if not fingerprint_hash:
            raw_data = fingerprint_data.get("raw_fingerprint_data")
            if raw_data is None:
                raise ValueError("Missing raw_fingerprint_data")
            fingerprint_hash = self.hash_fingerprint_data(raw_data)

        fingerprint, _ = DeviceFingerprint.objects.get_or_create(
            user=self.user,
            website=self.website,
            fingerprint_hash=fingerprint_hash,
            defaults={
                "user_agent": fingerprint_data.get("user_agent", ""),
                "ip_address": fingerprint_data.get("ip_address"),
                "device_name": fingerprint_data.get("device_name"),
                "is_trusted": False,
                "login_count": 0,
                "last_seen_at": timezone.now(),
            },
        )

        fingerprint.user_agent = fingerprint_data.get("user_agent", "")
        fingerprint.ip_address = fingerprint_data.get("ip_address")
        fingerprint.device_name = fingerprint_data.get("device_name")
        fingerprint.last_seen_at = timezone.now()
        fingerprint.login_count += 1

        if (
            not fingerprint.is_trusted
            and fingerprint.login_count >= self.trust_after_logins
        ):
            fingerprint.is_trusted = True

        fingerprint.save(
            update_fields=[
                "user_agent",
                "ip_address",
                "device_name",
                "last_seen_at",
                "login_count",
                "is_trusted",
            ],
        )

        return fingerprint
    
    @classmethod
    def is_trusted_device(
        cls,
        *,
        user,
        website,
        request=None,
    ) -> bool:
        """
        Determine whether the current request belongs to a trusted
        device fingerprint.

        Args:
            user: User instance.
            website: Website instance.
            request: Optional HTTP request.

        Returns:
            True if trusted fingerprint exists, otherwise False.
        """
        service = cls(user=user, website=website)
        fingerprint_data = AuthenticationService._extract_fingerprint_data(request=request)

        if not fingerprint_data:
            return False

        raw_fingerprint_data = fingerprint_data.get("raw_fingerprint_data")
        if not raw_fingerprint_data:
            return False

        try:
            fingerprint_hash = service.hash_fingerprint_data(
                raw_fingerprint_data,
            )
        except ValueError:
            return False

        fingerprint = service.get_fingerprint_by_hash(
            fingerprint_hash=fingerprint_hash,
        )

        if fingerprint is None:
            return False

        return bool(fingerprint.is_trusted)
    
    @transaction.atomic
    def create_fingerprint(
        self,
        *,
        fingerprint_hash: str,
        ip_address: str | None = None,
        user_agent: str = "",
        device_name: str | None = None,
    ) -> DeviceFingerprint:
        """
        Create a new fingerprint record.
        """
        return DeviceFingerprint.objects.create(
            user=self.user,
            website=self.website,
            fingerprint_hash=fingerprint_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
            is_trusted=False,
            login_count=1,
            last_seen_at=timezone.now(),
        )
    
    @classmethod
    def resolve_or_create(
        cls,
        *,
        user,
        website,
        request=None,
    ) -> DeviceFingerprint:
        """
        Resolve an existing fingerprint for the request or create one.

        Args:
            user: User instance.
            website: Website instance.
            request: Optional HTTP request.

        Returns:
            DeviceFingerprint instance.
        """
        if request is None:
            raise ValidationError("Fingerprint request is required.")

        service = cls(user=user, website=website)
        fingerprint_data = AuthenticationService._extract_fingerprint_data(request=request)

        if not fingerprint_data:
            raise ValidationError("Fingerprint data is required.")

        raw_fingerprint_data = fingerprint_data.get("raw_fingerprint_data")
        if not raw_fingerprint_data:
            raise ValidationError("Fingerprint data is required.")

        fingerprint_hash = service.hash_fingerprint_data(
            raw_fingerprint_data,
        )
        
        return service.create_or_update_fingerprint(
                {
                    "fingerprint_hash": fingerprint_hash,
                    "ip_address": request.META.get("REMOTE_ADDR"),
                    "user_agent": request.headers.get("User-Agent", ""),
                    "device_name": fingerprint_data.get("device_name"),
                }
            )

    @transaction.atomic
    def mark_trusted(
        self,
        *,
        fingerprint_hash: str,
        revoke_others: bool = True,
    ) -> bool:
        """
        Mark a fingerprint as trusted.

        Args:
            fingerprint_hash: Fingerprint hash to trust.
            revoke_others: Whether to revoke trust from all other
                fingerprints for the user on the website.

        Returns:
            True if the fingerprint was found and trusted,
            otherwise False.
        """
        fingerprint = DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website,
            fingerprint_hash=fingerprint_hash,
        ).first()

        if fingerprint is None:
            return False

        if hasattr(fingerprint, "mark_as_trusted"):
            fingerprint.mark_as_trusted()
        else:
            fingerprint.is_trusted = True
            fingerprint.save(update_fields=["is_trusted"])

        if revoke_others:
            self.revoke_other_trust(
                current_fingerprint_hash=fingerprint_hash,
            )

        return True

    @transaction.atomic
    def revoke_other_trust(
        self,
        *,
        current_fingerprint_hash: str,
    ) -> int:
        """
        Revoke trust from all other trusted fingerprints.

        Args:
            current_fingerprint_hash: Fingerprint hash that should
                remain trusted.

        Returns:
            Number of updated fingerprint records.
        """
        updated_count = DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website,
            is_trusted=True,
        ).exclude(
            fingerprint_hash=current_fingerprint_hash,
        ).update(is_trusted=False)

        return updated_count

    def calculate_risk_score(
        self,
        *,
        fingerprint_hash: str,
    ) -> float:
        """
        Calculate a simple risk score for a fingerprint.

        Args:
            fingerprint_hash: Fingerprint hash to evaluate.

        Returns:
            Risk score from 0.0 to 1.0.
        """
        fingerprint = DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website,
            fingerprint_hash=fingerprint_hash,
        ).first()

        if fingerprint is None:
            return 1.0

        age_hours = (
            timezone.now() - fingerprint.created_at
        ).total_seconds() / 3600

        if fingerprint.is_trusted:
            return max(0.0, 0.3 - min(age_hours, 48) / 160)

        return min(1.0, 0.6 + min(age_hours, 24) / 48)

    def find_suspicious_fingerprints(
        self,
        *,
        current_ip: str | None = None,
        current_user_agent: str | None = None,
        exclude_fingerprint_hash: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Identify suspicious fingerprints based on simple anomalies.

        Args:
            current_ip: Current request IP address.
            current_user_agent: Current request user agent.

        Returns:
            A list of suspicious fingerprint findings. Each entry
            includes the fingerprint, reasons, and severity score.
        """
        suspicious: list[dict[str, Any]] = []

        fingerprints = DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website,
        )

        if exclude_fingerprint_hash:
            fingerprints = fingerprints.exclude(
                fingerprint_hash=exclude_fingerprint_hash,
            )

        for fingerprint in fingerprints:
            reasons: list[str] = []
            severity = 0.0

            if current_ip and fingerprint.ip_address != current_ip:
                reasons.append("IP mismatch")
                severity += 0.5

            if (
                current_user_agent
                and current_user_agent.lower()
                not in (fingerprint.user_agent or  "").lower()
            ):
                reasons.append("User-Agent mismatch")
                severity += 0.4

            if not fingerprint.is_trusted:
                reasons.append("Untrusted device")
                severity += 0.3

            if reasons:
                suspicious.append(
                    {
                        "fingerprint": fingerprint,
                        "reasons": reasons,
                        "severity": round(min(severity, 1.0), 2),
                    }
                )

        return suspicious

    def evaluate_risk(
        self,
        *,
        fingerprint_hash: str,
    ) -> dict[str, float | bool]:
        """
        Evaluate the risk level for a fingerprint.

        Args:
            fingerprint_hash: Fingerprint hash to evaluate.

        Returns:
            A dictionary containing the numeric score and whether
            the fingerprint is considered high risk.
        """
        score = self.calculate_risk_score(
            fingerprint_hash=fingerprint_hash,
        )

        return {
            "score": score,
            "is_high_risk": score >= 0.8,
        }
    

    def get_fingerprint_by_hash(
        self,
        *,
        fingerprint_hash: str,
    ) -> DeviceFingerprint | None:
        """
        Retrieve a fingerprint by its hash.

        Args:
            fingerprint_hash: Fingerprint hash.

        Returns:
            Matching DeviceFingerprint or None.
        """
        return DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website,
            fingerprint_hash=fingerprint_hash,
        ).first()
    


    @transaction.atomic
    def mark_untrusted(
        self,
        *,
        fingerprint_hash: str,
    ) -> bool:
        """
        Mark a fingerprint as untrusted.
        """
        fingerprint = DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website,
            fingerprint_hash=fingerprint_hash,
        ).first()

        if fingerprint is None:
            return False

        fingerprint.mark_as_untrusted()
        return True