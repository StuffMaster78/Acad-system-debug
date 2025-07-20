EVENT_PRIORITIES = {
    'order.late': 'high',
    'order.completed': 'normal',
    'order.reviewed': 'low',
}

EVENT_FANOUT_CONFIG = {
    'order.assigned': 'group_team',  # Or 'individual'
}

def get_priority(event_key: str) -> str:
    return EVENT_PRIORITIES.get(event_key, 'normal')