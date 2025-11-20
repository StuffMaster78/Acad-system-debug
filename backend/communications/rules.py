def get_visibility_flags(sender_role: str, recipient_role: str) -> tuple[bool, bool]:
    """
    Determine whether a message should be visible to client or writer.

    Args:
        sender_role (str): Role of the sender.
        recipient_role (str): Role of the recipient.

    Returns:
        tuple: (visible_to_client, visible_to_writer)
    """
    staff_roles = {"admin", "superadmin", "support", "editor"}

    visible_to_client = not (
        sender_role in staff_roles and recipient_role == "writer"
    )
    visible_to_writer = not (
        sender_role in staff_roles and recipient_role == "client"
    )

    return visible_to_client, visible_to_writer