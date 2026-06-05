"""
WSGI config for writing_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import warnings

warnings.filterwarnings(
    "ignore",
    message=r"urllib3 .* or chardet .*charset_normalizer .* doesn't match a supported version!",
)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')

application = get_wsgi_application()
