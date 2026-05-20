"""
Canonical serializers package for orders.

Do not eagerly import serializers_legacy here. That module imports legacy model
definitions and can conflict with the current order models during app loading.
Legacy views that still need it should import orders.serializers_legacy
explicitly until they are retired.
"""

from orders.serializers.orders import OrderSerializer

__all__ = ["OrderSerializer"]
