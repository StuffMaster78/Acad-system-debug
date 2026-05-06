import uuid


def generate_event_id() -> uuid.UUID:
    return uuid.uuid4()