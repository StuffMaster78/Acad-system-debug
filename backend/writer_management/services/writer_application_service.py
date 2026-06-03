"""
writer_management/services/writer_application_service.py

Owns the full WriterApplication lifecycle.

PIPELINE
--------
submit() → WriterApplication (status=PENDING)
mark_under_review() → status=UNDER_REVIEW
approve() → status=APPROVED
                       1. AccountCreationService.create_account_profile()
                       2. WriterOnboardingService.complete_onboarding()
                       3. WriterProfileService.create_for_approved_application()
reject() → status=REJECTED
withdraw() → status=WITHDRAWN

NOTIFICATION STRATEGY
---------------------
NotificationService.notify() requires an authenticated User instance.
It validates is_authenticated before queuing.

This creates a challenge for submission and rejection — at those
points the applicant may not have a User account yet.

Resolution by event:

    submitted → notify_role("admin", ...) to alert admins
                  No notification to applicant — they get a confirmation
                  email from the form submission layer (not this service)

    under_review → notify_role("admin", ...) — already reviewing
                   No applicant notification at this stage

    approved → User exists by this point (created in approve())
                  notify(recipient=user, ...) — standard path

    rejected → If User exists: notify(recipient=user, ...)
                  If no User: send direct email via platform email backend
                  (NotificationService requires authenticated User)

    withdrawn → If User exists: notify(recipient=user, ...)
                  If no User: nothing — they withdrew themselves

EVENT KEY REGISTRATION
----------------------
All event keys used here must be registered in
notifications_system.enums.NotificationEvent.
is_valid_event() is called inside notify() — unregistered keys
are silently skipped with a warning log.

Required registrations:
    writer.application.submitted
    writer.application.approved
    writer.application.rejected
    writer.application.withdrawn
"""

import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.timezone import now

from writer_management.models.writer_application import WriterApplication

User = get_user_model()
logger = logging.getLogger(__name__)



class WriterApplicationService:

    # ----------------------------------------------------------------
    # SUBMISSION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def submit(
        *,
        website,
        full_name: str,
        email: str,
        application_text: str = "",
        phone_number: str = "",
        country: str = "",
        education_level: str = "",
        years_of_experience: int = 0,
        subjects: list | None = None,
        resume=None,
        sample_work=None,
    ) -> WriterApplication:
        """
        Submit a new writer application.

        Args:
            website: Website the applicant is applying to.
            full_name: Applicant's full name.
            email: Contact email address.
            application_text: Cover letter or motivation text.
            phone_number: Optional.
            country: Applicant's country.
            education_level: Highest education completed.
            years_of_experience: Years of writing experience.
            subjects: List of subject area strings.
            resume: Uploaded resume file or None.
            sample_work: Uploaded sample file or None.

        Returns:
            WriterApplication (status=PENDING).

        Raises:
            ValueError: If an active application already exists
                        for this email on this website.
        """
        existing = WriterApplication.objects.filter(
            email__iexact=email.strip(),
            website=website,
            status__in=[
                WriterApplication.Status.PENDING,
                WriterApplication.Status.UNDER_REVIEW,
                WriterApplication.Status.APPROVED,
            ],
        ).first()

        if existing:
            raise ValueError(
                f"An active application already exists for '{email}' "
                f"on this website (status: {existing.status}). "
                "Withdraw the existing application before reapplying."
            )

        application = WriterApplication.objects.create(
            website=website,
            full_name=full_name.strip(),
            email=email.strip().lower(),
            phone_number=phone_number.strip(),
            country=country.strip(),
            education_level=education_level.strip(),
            years_of_experience=max(0, years_of_experience),
            subjects=subjects or [],
            application_text=application_text.strip(),
            resume=resume,
            sample_work=sample_work,
            status=WriterApplication.Status.PENDING,
        )

        logger.info(
            "WriterApplication submitted: pk=%s email=%s website=%s",
            application.pk,
            application.email,
            website.pk,
        )

        # Notify admins — they need to know a new application arrived.
        # Applicant receives a confirmation from the form submission
        # layer (view/serializer), not here.
        WriterApplicationService._notify_admins(
            event_key="writer.application.submitted",
            website=website,
            context={
                "full_name": application.full_name,
                "email": application.email,
                "application_id": application.pk,
                "website_name": getattr(website, "name", str(website.pk)),
            },
        )

        return application

    # ----------------------------------------------------------------
    # MARK UNDER REVIEW
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def mark_under_review(
        *,
        application: WriterApplication,
        reviewed_by,
    ) -> WriterApplication:
        """
        Mark a PENDING application as UNDER_REVIEW.

        Args:
            application: WriterApplication (must be PENDING).
            reviewed_by: Admin User taking ownership.

        Returns:
            Updated WriterApplication.

        Raises:
            ValueError: If application is not PENDING.
        """
        if application.status != WriterApplication.Status.PENDING:
            raise ValueError(
                f"Cannot mark application {application.pk} as under review. "
                f"Current status: {application.status}. "
                "Expected: pending."
            )

        application.status = WriterApplication.Status.UNDER_REVIEW
        application.reviewed_by = reviewed_by
        application.save(update_fields=[
            "status", "reviewed_by", "updated_at"
        ])

        logger.info(
            "WriterApplication under review: pk=%s by=%s",
            application.pk,
            getattr(reviewed_by, "pk", "?"),
        )

        return application

    # ----------------------------------------------------------------
    # APPROVAL
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def approve(
        *,
        application: WriterApplication,
        reviewed_by,
        initial_level=None,
        require_review: bool = True,
    ):
        """
        Approve a writer application.

        Full pipeline — all atomic:
            1. Validate application state
            2. Get or create User for this email
            3. Create AccountProfile (accounts.AccountCreationService)
            4. Complete platform onboarding (accounts.WriterOnboardingService)
               - assigns 'writer' role
               - grants 'writer_portal' access
               - grants tenant access
               - completes OnboardingSession
               - sets AccountProfile.onboarding_status = COMPLETED
               - sets AccountProfile.status = UNDER_REVIEW | ACTIVE
               - logs AccountAuditEvent
            5. Create WriterProfile (WriterProfileService)
               - sets WriterProfile.onboarding_status = IN_PROGRESS
               - bootstraps satellite rows via signal
            6. Link AccountProfile to application
            7. Update application status to APPROVED
            8. Notify writer (User now exists — notify() works)

        Args:
            application: WriterApplication to approve.
            reviewed_by: Admin User approving.
            initial_level: Optional WriterLevel. None = unassigned.
            require_review: True → AccountProfile.status = UNDER_REVIEW.
                            False → AccountProfile.status = ACTIVE.

        Returns:
            Created WriterProfile instance.

        Raises:
            ValueError: If application is not approvable.
        """
        if application.status not in (
            WriterApplication.Status.PENDING,
            WriterApplication.Status.UNDER_REVIEW,
        ):
            raise ValueError(
                f"Cannot approve application {application.pk}. "
                f"Current status: {application.status}. "
                "Only pending or under_review applications can be approved."
            )

        # Step 1b: Quiz gate — block approval if required quizzes are not passed
        WriterApplicationService._check_required_quizzes(application)

        from accounts.exceptions import AccountProfileAlreadyExistsError
        from accounts.models import AccountProfile
        from accounts.services.account_creation_service import (
            AccountCreationService,
        )
        from accounts.services.writer_onboarding_service import (
            WriterOnboardingService,
        )
        from writer_management.services.writer_profile_service import (
            WriterProfileService,
        )

        # Step 2: Resolve User
        user = WriterApplicationService._get_or_create_user(application)

        # Step 3: Create AccountProfile
        try:
            account_profile = AccountCreationService.create_account_profile(
                website=application.website,
                user=user,
                actor=reviewed_by,
                metadata={
                    "source": "writer_application",
                    "application_id": application.pk,
                },
            )
        except AccountProfileAlreadyExistsError:
            account_profile = AccountProfile.objects.get(
                website=application.website,
                user=user,
            )
            logger.warning(
                "AccountProfile already exists: user=%s website=%s pk=%s.",
                user.pk,
                application.website.pk,
                account_profile.pk,
            )

        # Step 4: Platform onboarding — accounts owns this entirely
        WriterOnboardingService.complete_onboarding(
            account_profile=account_profile,
            actor=reviewed_by,
            require_review=require_review,
            metadata={"application_id": application.pk},
        )

        # Step 5: Writer domain profile
        writer_profile = WriterProfileService.create_for_approved_application(
            account_profile=account_profile,
            application=application,
            initial_level=initial_level,
        )

        # Steps 6+7: Link and close application
        application.account_profile = account_profile # type: ignore[assignment]
        application.status = WriterApplication.Status.APPROVED
        application.reviewed_by = reviewed_by
        application.reviewed_at = now()
        application.save(update_fields=[
            "account_profile",
            "status",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ])

        logger.info(
            "WriterApplication approved: pk=%s email=%s writer=%s by=%s",
            application.pk,
            application.email,
            writer_profile.registration_id,
            getattr(reviewed_by, "pk", "?"),
        )

        # Step 8: Notify writer — User exists now, notify() works
        WriterApplicationService._notify_user(
            event_key="writer.application.approved",
            user=user,
            website=application.website,
            context={
                "full_name": application.full_name,
                "registration_id": writer_profile.registration_id,
                "email": application.email,
            },
        )

        return writer_profile

    # ----------------------------------------------------------------
    # REJECTION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def reject(
        *,
        application: WriterApplication,
        reviewed_by,
        rejection_reason: str,
        admin_notes: str = "",
    ) -> WriterApplication:
        """
        Reject a writer application.

        Args:
            application: WriterApplication to reject.
            reviewed_by: Admin User rejecting.
            rejection_reason: Required — shown to applicant.
            admin_notes: Optional internal notes.

        Returns:
            Updated WriterApplication.

        Raises:
            ValueError: If terminal state or reason blank.
        """
        if application.is_terminal:
            raise ValueError(
                f"Cannot reject application {application.pk}. "
                f"Already terminal: {application.status}."
            )

        if not rejection_reason.strip():
            raise ValueError(
                "rejection_reason is required when rejecting an application."
            )

        application.status = WriterApplication.Status.REJECTED
        application.reviewed_by = reviewed_by
        application.reviewed_at = now()
        application.rejection_reason = rejection_reason.strip()
        application.admin_notes = admin_notes.strip()
        application.save(update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "rejection_reason",
            "admin_notes",
            "updated_at",
        ])

        logger.info(
            "WriterApplication rejected: pk=%s email=%s by=%s",
            application.pk,
            application.email,
            getattr(reviewed_by, "pk", "?"),
        )

        # Notify — User may or may not exist at rejection time
        WriterApplicationService._notify_applicant(
            event_key="writer.application.rejected",
            email=application.email,
            website=application.website,
            context={
                "full_name": application.full_name,
                "email": application.email,
                "rejection_reason": rejection_reason.strip(),
            },
        )

        return application

    # ----------------------------------------------------------------
    # WITHDRAWAL
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def withdraw(*, application: WriterApplication) -> WriterApplication:
        """
        Candidate withdraws their own application.

        Only possible while PENDING or UNDER_REVIEW.

        Args:
            application: WriterApplication to withdraw.

        Raises:
            ValueError: If not in an active state.
        """
        if not application.is_active:
            raise ValueError(
                f"Cannot withdraw application {application.pk}. "
                f"Current status: {application.status}. "
                "Only pending or under_review applications can be withdrawn."
            )

        application.status = WriterApplication.Status.WITHDRAWN
        application.save(update_fields=["status", "updated_at"])

        logger.info(
            "WriterApplication withdrawn: pk=%s email=%s",
            application.pk,
            application.email,
        )

        # Notify only if a User account exists for this email
        WriterApplicationService._notify_applicant(
            event_key="writer.application.withdrawn",
            email=application.email,
            website=application.website,
            context={
                "full_name": application.full_name,
                "email": application.email,
            },
        )

        return application

    # ----------------------------------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _get_or_create_user(application: WriterApplication):
        """
        Get existing User for this email or create a new one.

        New users are created with an unusable password.
        They set their password via the onboarding email link.
        """
        email = application.email.strip().lower()

        try:
            user = User.objects.get(email=email)
            logger.info(
                "Found existing User: email=%s pk=%s", email, user.pk
            )
            return user
        except User.DoesNotExist:
            pass

        user = User(email=email)
        if hasattr(user, "username"):
            user.username = email
        user.set_unusable_password()
        user.save()

        logger.info(
            "Created User for approved application: email=%s pk=%s",
            email,
            user.pk,
        )

        return user

    @staticmethod
    def _notify_user(
        event_key: str,
        user,
        website,
        context: dict,
        triggered_by=None,
        is_critical: bool = False,
    ) -> None:
        """
        Notify a known User instance via NotificationService.notify().

        Used when we are certain the User account exists.
        notify() requires is_authenticated — only call this
        after the User has been created and saved.
        """
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify(
                event_key=event_key,
                recipient=user,
                website=website,
                context=context,
                triggered_by=triggered_by,
                is_critical=is_critical,
            )
        except Exception as exc:
            logger.exception(
                "_notify_user failed: event=%s user=%s: %s",
                event_key,
                getattr(user, "pk", "?"),
                exc,
            )

    @staticmethod
    def _notify_admins(
        event_key: str,
        website,
        context: dict,
        triggered_by=None,
        is_critical: bool = False,
    ) -> None:
        """
        Notify all admin users on a website via notify_role().

        Used for events that admins need to act on
        (new application, threshold crossed, etc.).
        """
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify_role(
                event_key=event_key,
                role="admin",
                website=website,
                context=context,
                triggered_by=triggered_by,
                is_critical=is_critical,
            )
        except Exception as exc:
            logger.exception(
                "_notify_admins failed: event=%s website=%s: %s",
                event_key,
                getattr(website, "pk", "?"),
                exc,
            )

    @staticmethod
    def _notify_applicant(
        event_key: str,
        email: str,
        website,
        context: dict,
    ) -> None:
        """
        Notify an applicant who may or may not have a User account.

        Strategy:
            1. Try to find a User with this email.
               If found → use notify() (full pipeline, dedup, preferences).
            2. If no User → send a direct transactional email.
               NotificationService.notify() cannot be used without
               an authenticated User instance.

        This covers rejection (before approval) and withdrawal.
        """
        # Try User-based notification first
        try:
            user = User.objects.get(email=email)
            WriterApplicationService._notify_user(
                event_key=event_key,
                user=user,
                website=website,
                context=context,
            )
            return
        except User.DoesNotExist:
            pass

        # No User account — fall back to direct transactional email
        # This uses the platform's email backend directly,
        # bypassing NotificationService (which requires a User).
        WriterApplicationService._send_transactional_email(
            event_key=event_key,
            email=email,
            website=website,
            context=context,
        )

    @staticmethod
    def _send_transactional_email(
        event_key: str,
        email: str,
        website,
        context: dict,
    ) -> None:
        """
        Send a transactional email to an address with no User account.

        NotificationService.notify() cannot be used here because it
        requires an authenticated User instance.

        Uses EmailService.send_rendered() directly — the same backend
        that NotificationService uses downstream, ensuring the correct
        provider (SendGrid, Mailgun, SES) is used per website config.

        The rendered dict is constructed here manually because these
        are simple plain-text transactional emails (rejection, withdrawal)
        that do not require the full template rendering pipeline.
        When the notifications_system rendering layer is confirmed,
        replace the manual rendered dict with a TemplateRenderer call.

        Args:
            event_key: Notification event key (for subject resolution).
            email: Recipient email address.
            website: Website instance (for provider resolution).
            context: Template variables.
        """
        from notifications_system.services.email_service import EmailService

        subject_map: dict[str, str] = {
            "writer.application.rejected": "Update on your writer application",
            "writer.application.withdrawn": "Application withdrawal confirmed",
            "writer.application.submitted": "Application received",
        }

        subject = subject_map.get(event_key, "Writer application update")

        full_name = context.get("full_name", "")
        body_text = f"Hi {full_name},\n\n"

        if event_key == "writer.application.rejected":
            rejection_reason = context.get("rejection_reason", "")
            body_text += (
                "Thank you for applying to write with us.\n\n"
                "After reviewing your application, we are unable to "
                "proceed at this time.\n\n"
            )
            if rejection_reason:
                body_text += f"Reason: {rejection_reason}\n\n"
            body_text += (
                "You are welcome to reapply in the future.\n\n"
                "Best regards"
            )

        elif event_key == "writer.application.withdrawn":
            body_text += (
                "This confirms that your writer application has been "
                "withdrawn successfully.\n\n"
                "If this was done in error, please contact support.\n\n"
                "Best regards"
            )

        elif event_key == "writer.application.submitted":
            body_text += (
                "We have received your application and will review it "
                "shortly. You will hear from us once a decision has "
                "been made.\n\n"
                "Best regards"
            )

        else:
            action = event_key.split(".")[-1].replace("_", " ").title()
            body_text += f"Status update: {action}\n\nBest regards"

        rendered: dict[str, str] = {
            "subject": subject,
            "body_text": body_text,
            "body_html": "", # Plain text only — no HTML template yet
        }

        try:
            EmailService.send_rendered(
                to_email=email,
                rendered=rendered,
                website=website,
            )
            logger.info(
                "_send_transactional_email sent: event=%s email=%s",
                event_key,
                email,
            )
        except Exception as exc:
            logger.exception(
                "_send_transactional_email failed: event=%s email=%s: %s",
                event_key,
                email,
                exc,
            )

    @staticmethod
    def _django_fallback_email(
        event_key: str,
        email: str,
        context: dict,
    ) -> None:
        """
        Absolute fallback — Django send_mail for critical application emails.

        Only used when EmailService is unavailable.
        Subject and body are minimal — this is a safety net, not a
        polished template.
        """
        from django.core.mail import send_mail
        from django.conf import settings as django_settings

        subject_map = {
            "writer.application.rejected": "Your writer application",
            "writer.application.withdrawn": "Application withdrawal confirmed",
        }

        subject = subject_map.get(event_key, "Writer application update")
        body = (
            f"Hi {context.get('full_name', '')},\n\n"
            f"This is an update regarding your writer application.\n\n"
            f"Status: {event_key.split('.')[-1].replace('_', ' ').title()}\n"
        )

        if "rejection_reason" in context:
            body += f"\nReason: {context['rejection_reason']}\n"

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            logger.info(
                "Fallback email sent: event=%s email=%s",
                event_key,
                email,
            )
        except Exception as exc:
            logger.exception(
                "Fallback email failed: event=%s email=%s: %s",
                event_key,
                email,
                exc,
            )
    @staticmethod
    def _check_required_quizzes(application) -> None:
        """
        Raise ValueError if any website-scoped quiz marked is_required_for_approval
        does not have a passing attempt from this applicant's email.

        Called at the top of approve() so the gate runs before any DB writes.
        """
        try:
            from writer_vetting.models import VettingQuiz, WriterTestAttempt
            from users.models.user import User as _User

            required = VettingQuiz.objects.filter(
                website=application.website,
                is_active=True,
                is_required_for_approval=True,
            )
            if not required.exists():
                return  # no required quizzes — gate open

            # Find the applicant's User if they already have an account
            try:
                applicant = _User.objects.get(email=application.email)
            except _User.DoesNotExist:
                # No account yet → no attempts → fail all required quizzes
                titles = ", ".join(q.title for q in required)
                raise ValueError(
                    f"Applicant has not taken the required quiz(es): {titles}. "
                    "They must create an account and pass all required quizzes first."
                )

            # Check each required quiz for a passing attempt by this writer
            failed_quizzes = []
            for quiz in required:
                passed = WriterTestAttempt.objects.filter(
                    quiz=quiz,
                    status="passed",
                ).filter(
                    writer__account_profile__user=applicant
                ).exists()
                if not passed:
                    failed_quizzes.append(quiz.title)

            if failed_quizzes:
                raise ValueError(
                    f"Cannot approve application — the following required quiz(es) "
                    f"have not been passed: {', '.join(failed_quizzes)}."
                )
        except ValueError:
            raise
        except Exception as exc:
            import logging as _log
            _log.getLogger(__name__).warning(
                "Quiz gate check error for application=%s: %s — skipping gate.",
                application.pk, exc,
            )
