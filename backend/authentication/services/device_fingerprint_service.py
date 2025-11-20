import hashlib
import json
from django.utils import timezone
from authentication.models.fingerprinting import DeviceFingerprint
from django.core.mail import send_mail
from authentication.models.security_alert_log import SecurityAlertLog 
from authentication.models.emails_log import EmailNotificationLog
from authentication.services.alert_service import AdminAlertService

class DeviceFingerprintService:
    """
    Manages device fingerprints, trust decisions, and risk scoring.
    """

    AUTO_TRUST_AFTER = 3

    def __init__(self, user, website, trust_after_logins=5):
        """
        Initialize the service with user and tenant context.

        Args:
            user (User): The user tied to the fingerprint.
            website (Website): Tenant context for multitenancy.
            trust_after_logins (int): Logins required to auto-trust.
        """
        self.user = user
        self.website = website
        self.trust_after_logins = trust_after_logins

    def create_or_update_fingerprint(self, fingerprint_data):
        """
        Create or update a fingerprint.

        Args:
            fingerprint_data (dict): Includes 'user_agent', 'ip_address',
                and 'raw_fingerprint_data'.

        Returns:
            DeviceFingerprint: The updated or created fingerprint.
        """
        fingerprint_hash = self._hash_fingerprint_data(
            fingerprint_data.get("raw_fingerprint_data")
        )

        fp, created = DeviceFingerprint.objects.get_or_create(
            user=self.user,
            website=self.website,
            fingerprint_hash=fingerprint_hash,
            defaults={
                "user_agent": fingerprint_data.get("user_agent", ""),
                "ip_address": fingerprint_data.get("ip_address", ""),
                "trusted": False,
            }
        )

        fp.last_seen = timezone.now()

        if created:
            fp.login_count = 1
        else:
            fp.login_count = getattr(fp, "login_count", 0) + 1
            if fp.login_count >= self.AUTO_TRUST_AFTER:
                fp.trusted = True

        fp.save()
        return fp

    def mark_trusted(self, fingerprint_hash, revoke_others=True):
        """
        Trust a fingerprint and optionally revoke others.

        Args:
            fingerprint_hash (str): The fingerprint hash to trust.
            revoke_others (bool): Revoke trust from other devices.

        Returns:
            bool: True if trust was applied, False if not found.
        """
        try:
            fp = DeviceFingerprint.objects.get(
                user=self.user,
                website=self.website,
                fingerprint_hash=fingerprint_hash
            )
            fp.trusted = True
            fp.save()

            if revoke_others:
                self.revoke_other_trust(fingerprint_hash)

            return True
        except DeviceFingerprint.DoesNotExist:
            return False

    def check_and_autotrust(self, fingerprint_hash, login_count):
        """
        Auto-trust device if login count exceeds threshold.

        Args:
            fingerprint_hash (str): Fingerprint hash.
            login_count (int): Number of logins from this fingerprint.

        Returns:
            bool: True if trusted, False otherwise.
        """
        if login_count >= self.trust_after_logins:
            return self.mark_trusted(fingerprint_hash)
        return False

    def calculate_risk_score(self, fingerprint_hash):
        """
        Compute a risk score for the device.

        Args:
            fingerprint_hash (str): The fingerprint hash.

        Returns:
            float: Risk score from 0.0 (low) to 1.0 (high).
        """
        try:
            fp = DeviceFingerprint.objects.get(
                user=self.user,
                website=self.website,
                fingerprint_hash=fingerprint_hash
            )

            age_hours = (
                timezone.now() - fp.created_at
            ).total_seconds() / 3600

            if fp.trusted:
                return max(0.0, 0.3 - min(age_hours, 48) / 160)

            return min(1.0, 0.6 + min(age_hours, 24) / 48)

        except DeviceFingerprint.DoesNotExist:
            return 1.0

    def revoke_other_trust(self, current_fingerprint_hash):
        """
        Untrust all other fingerprints except the current one.

        Args:
            current_fingerprint_hash (str): Fingerprint to retain trust.
        """
        DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website,
            trusted=True
        ).exclude(
            fingerprint_hash=current_fingerprint_hash
        ).update(trusted=False)

    @staticmethod
    def _hash_fingerprint_data(raw_data):
        """
        Hash raw fingerprint data using SHA-256.

        Args:
            raw_data (dict or str): JSON string or dict.

        Returns:
            str: Hashed string.
        """
        if isinstance(raw_data, dict):
            raw_data = json.dumps(raw_data, sort_keys=True)
        return hashlib.sha256(raw_data.encode()).hexdigest()

    @staticmethod
    def flag_suspicious_devices(
        self,
        current_ip=None,
        current_user_agent=None
    ):
        """
        Detect potentially suspicious fingerprints based
        on IP or user-agent anomalies.

        Args:
            current_ip (str, optional): Current IP address.
            current_user_agent (str, optional): Current user-agent string.

        Returns:
            list[DeviceFingerprint]: List of suspicious fingerprints.
        """
        suspicious = []

        fingerprints = DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website
        )

        for fp in fingerprints:
            reasons = []
            severity = 0

            if current_ip and fp.ip_address != current_ip:
                reasons.append("IP mismatch")
                severity += 0.5

            if current_user_agent and (
                current_user_agent.lower() not in fp.user_agent.lower()
            ):
                reasons.append("User-Agent mismatch")
                severity += 0.4

            if not fp.trusted:
                reasons.append("Untrusted device")
                severity += 0.3

            if reasons:
                suspicious.append({
                    "fingerprint": fp,
                    "reasons": reasons,
                    "severity": round(min(severity, 1.0), 2),
                })

        return suspicious
    
    @staticmethod
    def alert_user_of_suspicious_login(user, reasons, website):
        """
        Notify user of suspicious login activity.

        Args:
            user (User): The affected user.
            reasons (list[str]): Reasons for the suspicion.
            website (Website): Context for multitenant alerting.
        """
        subject = "Suspicious Login Attempt Detected"
        message = (
            "We noticed something unusual about a recent login to your account.\n\n"
            "Reasons:\n" + "\n".join(f"- {reason}" for reason in reasons) +
            "\n\nIf this wasn't you, please secure your account immediately."
        )

        send_mail(
            subject,
            message,
            from_email="security@yourapp.com",
            recipient_list=[user.email]
        )

        # Optional: log it
        EmailNotificationLog.objects.create(
            user=user,
            event="suspicious_login",
            recipient_email=user.email,
        )

    @staticmethod
    def alert_and_log_suspicious_activity(
        user,
        website,
        suspicious_fps
    ):
        """
        Alert user and optionally log suspicious fingerprint events.
        """
        for s in suspicious_fps:
            fingerprint = s["fingerprint"]
            reasons = s["reasons"]
            severity = s["severity"]

            # Save to log if model is in use
            SecurityAlertLog.objects.create(
                user=user,
                website=website,
                fingerprint=fingerprint,
                reasons="\n".join(reasons),
                severity=severity
            )

            # Email alert if severity is high
            if severity >= 0.6:
                send_mail(
                    subject="⚠️ Suspicious Login Attempt Detected",
                    message=(
                        "Hey, we noticed something odd about your recent login:\n\n"
                        "Reasons:\n" + "\n".join(f"- {r}" for r in reasons) +
                        "\n\nIf this wasn’t you, please change your password ASAP."
                    ),
                    from_email="security@yourapp.com",
                    recipient_list=[user.email]
                )

                EmailNotificationLog.objects.create(
                    user=user,
                    event="suspicious_login",
                    recipient_email=user.email
                )

    def evaluate_and_alert_if_risky(self, fingerprint_hash, ip_address):
        """
        Evaluate risk and alert if threshold breached.

        Args:
            fingerprint_hash (str): Hash of fingerprint.
            ip_address (str): IP address of request.

        Returns:
            float: Calculated risk score.
        """
        score = self.calculate_risk_score(fingerprint_hash)
        if score >= 0.8:
            reason = "High risk score"
            AdminAlertService.send_suspicious_login_alert(
                user=self.user,
                ip=ip_address,
                reason=reason,
                website=self.website
            )
        return score