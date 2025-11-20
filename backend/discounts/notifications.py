# from notifications_system.services.dispatcher import notify_user, notify_users
# from orders.models import Order
# from discounts.models import Discount


# notify_user(
#     user=target_user,
#     subject="Discount Applied!",
#     category="discount",
#     message="A new discount has been applied to your order.",
#     event="discount_notification",
#     channels=["email", "push", "websocket"],
#     tenant=order.website,
#     actor=order.user,
#     template_name="discount_notification",
#     priority=5,
#     is_critical=True,
#     is_digest=False,
#     is_silent=False,
#     email_override=None,
#     context={
#         "order_id": order.id,
#         "discount_amount": order.discount_amount,
#         "total_amount": order.total_amount,
#     },
#     template="discount_notification",
# )   