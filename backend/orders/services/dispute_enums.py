class DisputeStatus:
    OPEN = "open"
    IN_REVIEW = "in_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class ResolutionOutcome:
    WRITER_WINS = "writer_wins"
    CLIENT_WINS = "client_wins"
    EXTEND_DEADLINE = "extend_deadline"
    REASSIGN = "reassign"
