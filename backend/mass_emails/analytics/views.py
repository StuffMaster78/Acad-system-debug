from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from mass_emails.models import (
    EmailRecipient, EmailOpenTracker,
    EmailClickTracker, UnsubscribeLog
)

# Transparent 1x1 pixel for open tracking
TRANSPARENT_PIXEL = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
    b'\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00'
    b'\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
    b'\x44\x01\x00\x3B'
)


def track_open(request, recipient_id):
    recipient = get_object_or_404(EmailRecipient, pk=recipient_id)

    if not hasattr(recipient, 'open_tracker'):
        EmailOpenTracker.objects.create(recipient=recipient)
        recipient.status = 'opened'
        recipient.opened_at = now()
        recipient.save(update_fields=['status', 'opened_at'])

    return HttpResponse(TRANSPARENT_PIXEL, content_type='image/gif')


def track_click(request, recipient_id):
    recipient = get_object_or_404(EmailRecipient, pk=recipient_id)
    url = request.GET.get('url')

    if url:
        EmailClickTracker.objects.create(recipient=recipient, url=url)
        if recipient.status == 'sent':
            recipient.status = 'opened'
            recipient.save(update_fields=['status'])
        return HttpResponseRedirect(url)

    return HttpResponse("Missing 'url' param", status=400)


def unsubscribe(request, recipient_id):
    recipient = get_object_or_404(EmailRecipient, pk=recipient_id)
    UnsubscribeLog.objects.get_or_create(
        email=recipient.email,
        user=recipient.user
    )
    return HttpResponse(
        "You've been unsubscribed. We're sorry to see you go."
    )