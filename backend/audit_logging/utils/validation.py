def assert_valid_event_action(action: str) -> None:
    if not action or "." not in action:
        raise ValueError("Invalid audit action format")