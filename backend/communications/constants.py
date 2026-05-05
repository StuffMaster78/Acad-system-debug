from __future__ import annotations


class CommunicationThreadKind:
    """
    Supported business conversation types.
    """

    CLIENT_SUPPORT = "client_support"
    CLIENT_WRITER = "client_writer"
    WRITER_SUPPORT = "writer_support"
    ADMIN_CLIENT = "admin_client"
    ADMIN_WRITER = "admin_writer"
    INTERNAL_STAFF = "internal_staff"
    REVISION = "revision"
    DISPUTE = "dispute"
    SENSITIVE_COORDINATION = "sensitive_coordination"
    SYSTEM = "system"

    CHOICES = (
        (CLIENT_SUPPORT, "Client support"),
        (CLIENT_WRITER, "Client writer"),
        (WRITER_SUPPORT, "Writer support"),
        (ADMIN_CLIENT, "Admin client"),
        (ADMIN_WRITER, "Admin writer"),
        (INTERNAL_STAFF, "Internal staff"),
        (REVISION, "Revision"),
        (DISPUTE, "Dispute"),
        (SENSITIVE_COORDINATION, "Sensitive coordination"),
        (SYSTEM, "System"),
    )


class CommunicationThreadStatus:
    """
    Thread lifecycle states.
    """

    OPEN = "open"
    LOCKED = "locked"
    ARCHIVED = "archived"
    CLOSED = "closed"

    CHOICES = (
        (OPEN, "Open"),
        (LOCKED, "Locked"),
        (ARCHIVED, "Archived"),
        (CLOSED, "Closed"),
    )


class CommunicationParticipantRole:
    """
    Role of a participant inside one thread.
    """

    CLIENT = "client"
    WRITER = "writer"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    SUPPORT = "support"
    FINANCE = "finance"
    OBSERVER = "observer"
    SYSTEM = "system"

    CHOICES = (
        (CLIENT, "Client"),
        (WRITER, "Writer"),
        (ADMIN, "Admin"),
        (SUPERADMIN, "Superadmin"),
        (SUPPORT, "Support"),
        (FINANCE, "Finance"),
        (OBSERVER, "Observer"),
        (SYSTEM, "System"),
    )


class CommunicationMessageType:
    """
    Message content type.
    """

    USER = "user"
    SYSTEM = "system"
    INTERNAL_NOTE = "internal_note"
    MODERATION_NOTICE = "moderation_notice"

    CHOICES = (
        (USER, "User"),
        (SYSTEM, "System"),
        (INTERNAL_NOTE, "Internal note"),
        (MODERATION_NOTICE, "Moderation notice"),
    )


class CommunicationMessageStatus:
    """
    Message moderation and visibility status.
    """

    ACTIVE = "active"
    HIDDEN = "hidden"
    WITHDRAWN = "withdrawn"
    FLAGGED = "flagged"
    ARCHIVED = "archived"
    DELETED = "deleted"
    HELD_FOR_REVIEW = "held_for_review"

    CHOICES = (
        (ACTIVE, "Active"),
        (HIDDEN, "Hidden"),
        (WITHDRAWN, "Withdrawn"),
        (ARCHIVED, "Archived"),
        (DELETED, "Deleted"),
        (HELD_FOR_REVIEW, "Held for review"),
    )