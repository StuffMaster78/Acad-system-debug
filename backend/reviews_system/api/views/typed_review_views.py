"""
Typed review endpoints — WriterReview, OrderReview, WebsiteReview.

These complement the unified Review model (used by the legacy API) with
concrete models that carry proper FK relationships and power the admin
moderation board and public display surfaces.
"""
from __future__ import annotations

from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews_system.models import OrderReview, WebsiteReview, WriterReview
from reviews_system.serializers import (
    OrderReviewSerializer,
    WebsiteReviewSerializer,
    WriterReviewSerializer,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _website(user):
    return getattr(user, "website", None)


def _require_client(user):
    return getattr(user, "role", "") == "client"


def _sync_writer_reputation(*, writer, website) -> None:
    """
    Recompute and persist a writer's reputation snapshot from approved OrderReviews.

    Called synchronously after a review is created so the snapshot is never stale.
    Errors are swallowed so a reputation hiccup never breaks review submission.
    """
    import logging
    try:
        from decimal import Decimal, ROUND_HALF_UP

        from reviews_system.models.order_review import OrderReview
        from reputation_system.models.writer_reputation_snapshot import (
            WriterReputationSnapshot,
        )
        from writer_management.models.writer_profile import WriterProfile

        # Resolve the writer's stable UUID identity from their WriterProfile.
        try:
            profile = WriterProfile.objects.get(user=writer)
            writer_uuid = profile.public_uuid
        except WriterProfile.DoesNotExist:
            return

        agg = (
            OrderReview.objects
            .filter(writer=writer, is_approved=True)
            .aggregate(avg=Avg("rating"), count=Count("id"))
        )
        avg_rating = agg["avg"]
        review_count = agg["count"] or 0

        if avg_rating is None:
            return

        avg_decimal = Decimal(str(avg_rating)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        WriterReputationSnapshot.objects.update_or_create(
            writer_id=str(writer_uuid),
            defaults={
                "website": website,
                "rating": avg_decimal,
                "review_count": review_count,
            },
        )
    except Exception:
        logging.getLogger(__name__).warning(
            "Failed to sync writer reputation for writer_id=%s",
            getattr(writer, "pk", None),
            exc_info=True,
        )


# ── Order review (submit + fetch) ─────────────────────────────────────────────

class OrderReviewView(APIView):
    """
    GET  /api/v1/orders/orders/{order_id}/review/  — fetch existing review
    POST /api/v1/orders/orders/{order_id}/review/  — submit review (client only)

    Clients may only review their own completed orders. One review per order.
    """

    permission_classes = [permissions.IsAuthenticated]

    def _get_order(self, user, order_id: int):
        from orders.models.orders import Order
        try:
            return Order.objects.get(pk=order_id, client=user)
        except Order.DoesNotExist:
            return None

    def get(self, request, order_id: int):
        order = self._get_order(request.user, order_id)
        if order is None:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            review = OrderReview.objects.select_related("reviewer", "writer").get(
                order=order
            )
            return Response(OrderReviewSerializer(review).data)
        except OrderReview.DoesNotExist:
            return Response(None, status=status.HTTP_200_OK)

    def post(self, request, order_id: int):
        if not _require_client(request.user):
            return Response(
                {"detail": "Only clients may submit order reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = self._get_order(request.user, order_id)
        if order is None:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.status not in {"completed", "approved"}:
            return Response(
                {"detail": "Reviews can only be submitted for completed orders."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if OrderReview.objects.filter(order=order).exists():
            return Response(
                {"detail": "You have already reviewed this order."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = request.data.get("rating")
        comment = request.data.get("body") or request.data.get("comment", "")

        if rating is None:
            return Response({"detail": "rating is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = float(rating)
            if not 0 <= rating <= 5:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"detail": "rating must be a number between 0 and 5."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resolve the writer from the order assignment
        writer = order.assigned_writer  # property on Order

        review = OrderReview.objects.create(
            reviewer=request.user,
            order=order,
            writer=writer,
            website=order.website,
            rating=rating,
            comment=comment,
            submitted_at=timezone.now(),
            is_approved=True,
        )

        # Sync the writer's reputation snapshot so the rating is reflected immediately.
        if writer is not None:
            _sync_writer_reputation(writer=writer, website=order.website)

        return Response(
            OrderReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


# ── Writer reviews (list + summary) ───────────────────────────────────────────

class WriterReviewListView(APIView):
    """
    GET /api/v1/writer-management/writers/{registration_id}/reviews/
    Public — returns approved, non-shadowed writer reviews.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, registration_id: str):
        try:
            from writer_management.models.writer_profile import WriterProfile
            profile = WriterProfile.objects.select_related("user").get(
                registration_id=registration_id
            )
        except Exception:
            return Response({"detail": "Writer not found."}, status=status.HTTP_404_NOT_FOUND)

        reviews = WriterReview.objects.filter(
            writer=profile.user,
            is_approved=True,
            is_shadowed=False,
        ).select_related("reviewer").order_by("-submitted_at")[:50]

        return Response(WriterReviewSerializer(reviews, many=True).data)


class WriterReviewSummaryView(APIView):
    """
    GET /api/v1/writer-management/writers/{registration_id}/reviews/summary/
    Returns aggregated rating stats for a writer.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, registration_id: str):
        try:
            from writer_management.models.writer_profile import WriterProfile
            profile = WriterProfile.objects.select_related("user").get(
                registration_id=registration_id
            )
        except Exception:
            return Response({"detail": "Writer not found."}, status=status.HTTP_404_NOT_FOUND)

        qs = WriterReview.objects.filter(
            writer=profile.user,
            is_approved=True,
            is_shadowed=False,
        )

        agg = qs.aggregate(
            average_rating=Avg("rating"),
            total_reviews=Count("id"),
        )

        # Distribution: count per star value 1-5
        distribution: dict[str, int] = {}
        for star in range(1, 6):
            distribution[str(star)] = qs.filter(
                rating__gte=star - 0.5,
                rating__lt=star + 0.5,
            ).count()

        return Response({
            "writer_registration_id": registration_id,
            "writer_pen_name": getattr(profile, "pen_name", ""),
            "total_reviews": agg["total_reviews"] or 0,
            "average_rating": float(agg["average_rating"] or 0),
            "rating_distribution": distribution,
        })


# ── Website review (submit) ───────────────────────────────────────────────────

class WebsiteReviewSubmitView(APIView):
    """
    POST /api/v1/reviews/website-review/
    Clients submit a rating for the website they're on.
    One review per client per site.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not _require_client(request.user):
            return Response(
                {"detail": "Only clients may submit website reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )

        website = _website(request.user)
        if website is None:
            return Response(
                {"detail": "No website associated with your account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if WebsiteReview.objects.filter(reviewer=request.user, website=website).exists():
            return Response(
                {"detail": "You have already reviewed this website."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating = request.data.get("rating")
        comment = request.data.get("comment", "")
        if rating is None:
            return Response({"detail": "rating is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = float(rating)
            if not 0 <= rating <= 5:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"detail": "rating must be between 0 and 5."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = WebsiteReview.objects.create(
            reviewer=request.user,
            website=website,
            rating=rating,
            comment=comment,
            submitted_at=timezone.now(),
        )
        return Response(
            WebsiteReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )
