from __future__ import annotations

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_management.permissions import IsAdmin
from discounts.models.site_promo_display import SitePromoDisplay


def _is_superadmin(user) -> bool:
    return bool(getattr(user, "is_superuser", False) or getattr(user, "role", None) == "superadmin")


def _resolve_website(request):
    website_id = request.query_params.get("website_id") or request.data.get("website_id")
    if website_id and _is_superadmin(request.user):
        from websites.models.websites import Website
        return Website.objects.filter(pk=website_id, is_deleted=False).first()
    return getattr(request, "website", None)


# ── Public ────────────────────────────────────────────────────────────────────

class PublicPromoDisplayView(APIView):
    """GET /api/v1/promos/active/ — returns the currently live promo for this site."""
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def get(self, request):
        website = getattr(request, "website", None)
        if not website:
            return Response({"active": False})

        now = timezone.now()
        promo = (
            SitePromoDisplay.objects
            .filter(website=website, is_active=True, starts_at__lte=now, ends_at__gte=now)
            .select_related("campaign")
            .order_by("-starts_at")
            .first()
        )
        if not promo:
            return Response({"active": False})

        return Response({
            "active": True,
            "id": promo.pk,
            "display_type": promo.display_type,
            "color_scheme": promo.color_scheme,
            "badge_text": promo.badge_text,
            "headline": promo.headline,
            "subtext": promo.subtext,
            "cta_label": promo.cta_label,
            "cta_url": promo.cta_url,
            "discount_code": promo.discount_code,
            "starts_at": promo.starts_at.isoformat(),
            "ends_at": promo.ends_at.isoformat(),
            "campaign_name": promo.campaign.name if promo.campaign else None,
        })


# ── Admin ─────────────────────────────────────────────────────────────────────

class AdminPromoDisplayListCreateView(APIView):
    """
    GET  /api/v1/promos/admin/   — list all promos for this website
    POST /api/v1/promos/admin/   — create a new promo
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        website = _resolve_website(request)
        if not website:
            return Response({"detail": "Website context required."}, status=400)

        promos = SitePromoDisplay.objects.filter(website=website).select_related("campaign").order_by("-starts_at")
        now = timezone.now()
        return Response([self._serialize(p, now) for p in promos])

    def post(self, request):
        website = _resolve_website(request)
        if not website:
            return Response({"detail": "Website context required."}, status=400)

        data = request.data
        errors = {}
        if not data.get("headline"):
            errors["headline"] = "Required."
        if not data.get("starts_at"):
            errors["starts_at"] = "Required."
        if not data.get("ends_at"):
            errors["ends_at"] = "Required."
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        campaign = None
        if data.get("campaign_id"):
            from discounts.models.promotional_campaign import PromotionalCampaign
            campaign = PromotionalCampaign.objects.filter(pk=data["campaign_id"], website=website).first()

        promo = SitePromoDisplay.objects.create(
            website=website,
            campaign=campaign,
            display_type=data.get("display_type", SitePromoDisplay.STRIP),
            color_scheme=data.get("color_scheme", SitePromoDisplay.SCHEME_BRAND),
            badge_text=data.get("badge_text", ""),
            headline=data["headline"],
            subtext=data.get("subtext", ""),
            cta_label=data.get("cta_label", "Order now"),
            cta_url=data.get("cta_url", "/order"),
            discount_code=data.get("discount_code", ""),
            starts_at=data["starts_at"],
            ends_at=data["ends_at"],
            is_active=bool(data.get("is_active", True)),
            created_by=request.user,
        )
        return Response(self._serialize(promo, timezone.now()), status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(p: SitePromoDisplay, now) -> dict:
        return {
            "id": p.pk,
            "display_type": p.display_type,
            "color_scheme": p.color_scheme,
            "badge_text": p.badge_text,
            "headline": p.headline,
            "subtext": p.subtext,
            "cta_label": p.cta_label,
            "cta_url": p.cta_url,
            "discount_code": p.discount_code,
            "starts_at": p.starts_at.isoformat(),
            "ends_at": p.ends_at.isoformat(),
            "is_active": p.is_active,
            "is_live": p.is_active and p.starts_at <= now <= p.ends_at,
            "campaign_id": p.campaign_id,
            "campaign_name": p.campaign.name if p.campaign else None,
            "created_at": p.created_at.isoformat(),
        }


class AdminPromoDisplayDetailView(APIView):
    """
    GET    /api/v1/promos/admin/<pk>/
    PATCH  /api/v1/promos/admin/<pk>/
    DELETE /api/v1/promos/admin/<pk>/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def _get_promo(self, request, pk):
        website = _resolve_website(request)
        if not website:
            return None, Response({"detail": "Website context required."}, status=400)
        try:
            promo = SitePromoDisplay.objects.select_related("campaign").get(pk=pk, website=website)
        except SitePromoDisplay.DoesNotExist:
            return None, Response({"detail": "Not found."}, status=404)
        return promo, None

    def get(self, request, pk):
        promo, err = self._get_promo(request, pk)
        if err:
            return err
        return Response(AdminPromoDisplayListCreateView._serialize(promo, timezone.now()))

    def patch(self, request, pk):
        promo, err = self._get_promo(request, pk)
        if err:
            return err
        data = request.data
        editable = [
            "display_type", "color_scheme", "badge_text", "headline",
            "subtext", "cta_label", "cta_url", "discount_code",
            "starts_at", "ends_at", "is_active",
        ]
        for field in editable:
            if field in data:
                setattr(promo, field, data[field])
        if "campaign_id" in data:
            if data["campaign_id"]:
                from discounts.models.promotional_campaign import PromotionalCampaign
                website = _resolve_website(request)
                promo.campaign = PromotionalCampaign.objects.filter(
                    pk=data["campaign_id"], website=website
                ).first()
            else:
                promo.campaign = None
        promo.save()
        return Response(AdminPromoDisplayListCreateView._serialize(promo, timezone.now()))

    def delete(self, request, pk):
        promo, err = self._get_promo(request, pk)
        if err:
            return err
        promo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
