from datetime import datetime, time

def is_dnd_now(profile):
    """
    Checks if the current time is within the user's
    Do Not Disturb (DND) period.
    Returns True if the current time is within
    the DND period, otherwise False.
    """
    if not profile or not profile.dnd_start or not profile.dnd_end:
        return False

    now = datetime.now().time()

    if profile.dnd_start < profile.dnd_end:
        return profile.dnd_start <= now < profile.dnd_end
    else:
        # DND spans over midnight
        return now >= profile.dnd_start or now < profile.dnd_end