# notifications_system/webhooks/views.py
import hmac, hashlib, json
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def ingest(request, source: str):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    raw = request.body
    secret_map = getattr(settings, "NOTIFICATION_WEBHOOK_SECRETS", {})
    secret = secret_map.get(source)
    if secret:
        sig = request.headers.get("X-Hub-Signature-256")
        if not sig:
            return HttpResponseBadRequest("Missing signature")
        digest = "sha256=" + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, digest):
            return HttpResponseBadRequest("Bad signature")

    event = json.loads(raw.decode("utf-8"))
    # Map → internal event if desired
    # handle_event.delay(...)
    return HttpResponse("ok")