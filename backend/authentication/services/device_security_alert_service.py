from typing import Any

from authentication.models.emails_log import EmailNotificationLog
from authentication.models.security_alert_log import SecurityAlertLog
from authentication.services.security_alert_service import (
    SecurityAlertService,
)
from notifications_system.services.notification_service import (
    NotificationService,
)


class DeviceSecurityAlertService:
    """
    Handle logging and notification for suspicious device and
    fingerprint-related activity.

    This service is responsible for:
        - logging suspicious fingerprint findings
        - notifying users about suspicious login activity
        - escalating high-severity alerts to admins or webhooks

    Risk scoring and suspicious-device detection should be handled by
    the fingerprint service. This service reacts to those findings.
    """

    USER_ALERT_THRESHOLD = 0.6
    ADMIN_ALERT_THRESHOLD = 0.8

    @staticmethod
    def log_suspicious_fingerprint(
        *,
        user,
        website,
        fingerprint,
        reasons: list[str],
        severity: float,
    ) -> SecurityAlertLog:
        """
        Persist a suspicious fingerprint finding.

        Args:
            user: User associated with the suspicious activity.
            website: Website or tenant context.
            fingerprint: DeviceFingerprint instance.
            reasons: List of reasons why the fingerprint is suspicious.
            severity: Severity score from 0.0 to 1.0.

        Returns:
            Created SecurityAlertLog instance.
        """
        return SecurityAlertLog.objects.create(
            user=user,
            website=website,
            fingerprint=fingerprint,
            reasons="\n".join(reasons),
            severity=severity,
        )

    @staticmethod
    def alert_user_of_suspicious_login(
        *,
        user,
        website,
        reasons: list[str],
        severity: float,
    ) -> None:
        """
        Notify a user about suspicious login activity.

        Args:
            user: User receiving the alert.
            website: Website or tenant context.
            reasons: Reasons for the suspicious activity.
            severity: Severity score from 0.0 to 1.0.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.suspicious_login_detected",
            context={
                "user": user,
                "reasons": reasons,
                "severity": severity,
            },
            channels = ["email", "in_app"],
        )

        EmailNotificationLog.objects.create(
            user=user,
            event="suspicious_login",
            recipient_email=user.email,
        )

    @staticmethod
    def alert_admins_of_suspicious_login(
        *,
        user,
        website,
        ip_address: str | None,
        reasons: list[str],
        severity: float,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Send an admin or webhook alert for suspicious login activity.

        Args:
            user: User associated with the suspicious activity.
            website: Website or tenant context.
            ip_address: Source IP address, if available.
            reasons: Reasons for the suspicious activity.
            severity: Severity score from 0.0 to 1.0.
            metadata: Optional additional context.

        Returns:
            True if the outbound alert was sent successfully,
            otherwise False.
        """
        return SecurityAlertService.send_suspicious_login_alert(
            website=website,
            user=user,
            ip_address=ip_address,
            reason=", ".join(reasons),
            metadata={
                "severity": severity,
                "reasons": reasons,
                **(metadata or {}),
            },
        )

    @classmethod
    def process_suspicious_fingerprints(
        cls,
        *,
        user,
        website,
        suspicious_findings: list[dict[str, Any]],
        ip_address: str | None = None,
    ) -> list[SecurityAlertLog]:
        """
        Process suspicious fingerprint findings by logging them and
        sending notifications based on severity thresholds.

        Args:
            user: User associated with the findings.
            website: Website or tenant context.
            suspicious_findings: List of suspicious fingerprint results.
            ip_address: Source IP address, if available.

        Returns:
            List of created SecurityAlertLog instances.
        """
        created_logs: list[SecurityAlertLog] = []

        for finding in suspicious_findings:
            fingerprint = finding["fingerprint"]
            reasons = finding["reasons"]
            severity = finding["severity"]

            log_entry = cls.log_suspicious_fingerprint(
                user=user,
                website=website,
                fingerprint=fingerprint,
                reasons=reasons,
                severity=severity,
            )
            created_logs.append(log_entry)

            if severity >= cls.USER_ALERT_THRESHOLD:
                cls.alert_user_of_suspicious_login(
                    user=user,
                    website=website,
                    reasons=reasons,
                    severity=severity,
                )

            if severity >= cls.ADMIN_ALERT_THRESHOLD:
                cls.alert_admins_of_suspicious_login(
                    user=user,
                    website=website,
                    ip_address=ip_address,
                    reasons=reasons,
                    severity=severity,
                    metadata={
                        "fingerprint_id": getattr(
                            fingerprint,
                            "pk",
                            None,
                        ),
                    },
                )

        return created_logs

    @classmethod
    def evaluate_and_alert_if_risky(
        cls,
        *,
        user,
        website,
        fingerprint_service,
        fingerprint_hash: str,
        ip_address: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> float:
        """
        Evaluate fingerprint risk and trigger admin alert if the risk
        score crosses the high-risk threshold.

        Args:
            user: User associated with the fingerprint.
            website: Website or tenant context.
            fingerprint_service: DeviceFingerprintService instance.
            fingerprint_hash: Hash of the fingerprint to evaluate.
            ip_address: Source IP address, if available.
            metadata: Optional additional context.

        Returns:
            Calculated risk score.
        """
        risk_result = fingerprint_service.evaluate_risk(
            fingerprint_hash=fingerprint_hash,
        )
        score = float(risk_result["score"])

        if score >= cls.ADMIN_ALERT_THRESHOLD:
            cls.alert_admins_of_suspicious_login(
                user=user,
                website=website,
                ip_address=ip_address,
                reasons=["High risk score"],
                severity=score,
                metadata=metadata,
            )

        return score