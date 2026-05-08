def assert_valid_event_action(action: str) -> None:
    if not isinstance(action, str):
        raise ValueError("action must be string")

    if "." not in action:
        raise ValueError("Invalid audit action format")

    domain, event = action.split(".", 1)

    if not domain or not event:
        raise ValueError("Invalid audit action structure")