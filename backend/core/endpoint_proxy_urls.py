"""
URL patterns for the endpoint proxy
"""
from django.urls import path
from core.endpoint_proxy import endpoint_proxy

urlpatterns = [
    path('<path:masked_path>', endpoint_proxy, name='endpoint-proxy'),
]

