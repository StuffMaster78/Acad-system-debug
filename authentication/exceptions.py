from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        scope = getattr(context['request'], 'throttled_scope', 'default')
        custom_messages = {
            'user': "Too many requests. Chill for a bit.",
            'anon': "You're hitting this too hard. Try again later.",
            'login': "Login attempts exceeded. Wait a minute before trying again.",
            'magic_link': "Too many magic link requests. Give your inbox a break.",
            'default': "Too many requests. Please slow down.",
        }
        message = custom_messages.get(scope, custom_messages['default'])

        return Response(
            data={"detail": message, "wait": exc.wait},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
        logger.warning(f"[THROTTLED] Scope: {scope} | Path: {context['request'].path} | IP: {context['request'].META.get('REMOTE_ADDR')}")

    return response