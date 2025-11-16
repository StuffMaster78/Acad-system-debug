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
        wait_time = int(exc.wait) if exc.wait else 0
        
        custom_messages = {
            'user': f"Too many requests. Please wait {wait_time} seconds.",
            'anon': f"You're hitting this too hard. Try again in {wait_time} seconds.",
            'login': f"Login attempts exceeded. Wait {wait_time} seconds before trying again.",
            'magic_link': f"Too many magic link requests. Please wait {wait_time} seconds before requesting another link.",
            'default': f"Too many requests. Please wait {wait_time} seconds.",
        }
        message = custom_messages.get(scope, custom_messages['default'])

        logger.warning(f"[THROTTLED] Scope: {scope} | Path: {context['request'].path} | IP: {context['request'].META.get('REMOTE_ADDR')} | Wait: {wait_time}s")

        return Response(
            data={"detail": message, "wait": wait_time},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    return response