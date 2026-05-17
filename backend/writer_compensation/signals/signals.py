from django.dispatch import Signal

# Fired when a window moves to PROCESSING.
# Receivers should notify all writers in the window.
# kwargs: window (CompensationWindow)
window_processing_started = Signal()

# Fired when a PayoutItem moves to PAID.
# Receivers should notify the individual writer.
# kwargs: item (PayoutItem)
payout_record_paid = Signal()

# Fired when a PayoutItem moves to HELD.
# Receivers should send a GENERIC message to the writer only —
# never expose hold_reason to the writer.
# kwargs: item (PayoutItem)
payout_record_held = Signal()

# Fired when a FINE CompensationEvent is created.
# Receivers should notify the writer with amount + source.
# kwargs: event (CompensationEvent)
fine_event_created = Signal()

# Fired when an ADJUSTMENT CompensationEvent is created.
# Receivers should notify the writer.
# kwargs: event (CompensationEvent)
adjustment_event_created = Signal()