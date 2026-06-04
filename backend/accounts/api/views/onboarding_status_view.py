"""
User-facing onboarding status endpoint.

Returns a checklist of steps and their completion state for the current user.
Each step is computed live from existing data — no separate onboarding-step model needed.
"""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def _client_checklist(user, website):
    """Build client onboarding checklist by checking real platform state."""
    from orders.models.orders import Order

    has_profile = bool(getattr(user, "first_name", "")) and bool(getattr(user, "last_name", ""))
    has_order = Order.objects.filter(client=user, website=website).exists()

    try:
        from wallets.services.client_wallet_service import ClientWalletService
        wallet = ClientWalletService.get_wallet(website=website, client=user)
        has_funded_wallet = wallet.total_credited > 0
    except Exception:
        has_funded_wallet = False

    try:
        from reviews_system.models import WebsiteReview
        has_review = WebsiteReview.objects.filter(reviewer=user, website=website).exists()
    except Exception:
        has_review = False

    steps = [
        {
            "key": "complete_profile",
            "label": "Complete your profile",
            "description": "Add your first and last name.",
            "done": has_profile,
            "link": "/client/account",
        },
        {
            "key": "place_first_order",
            "label": "Place your first order",
            "description": "Start a new writing order to get matched with a writer.",
            "done": has_order,
            "link": "/client/new-order",
        },
        {
            "key": "add_funds",
            "label": "Add funds to your wallet",
            "description": "Top up your wallet so you can pay for orders instantly.",
            "done": has_funded_wallet,
            "link": "/client/wallet",
        },
        {
            "key": "leave_review",
            "label": "Rate the platform",
            "description": "Help us improve by leaving a brief rating.",
            "done": has_review,
            "link": "/client/feedback",
        },
    ]

    completed = sum(1 for s in steps if s["done"])
    return {"role": "client", "steps": steps, "completed": completed, "total": len(steps)}


def _writer_checklist(user, website):
    """Build writer onboarding checklist."""
    try:
        from writer_management.models.writer_profile import WriterProfile
        profile = WriterProfile.objects.get(user=user, website=website)
        has_bio = bool(getattr(profile, "bio", ""))
        has_availability = getattr(profile, "is_accepting_orders", False)
    except Exception:
        has_bio = False
        has_availability = False

    try:
        from writer_vetting.models import WriterTestAttempt
        passed_quiz = WriterTestAttempt.objects.filter(
            writer=user, status="passed"
        ).exists()
    except Exception:
        passed_quiz = False

    try:
        from orders.models.orders import Order
        has_assignment = Order.objects.filter(
            assignments__writer=user, assignments__is_current=True
        ).exists()
    except Exception:
        has_assignment = False

    steps = [
        {
            "key": "complete_bio",
            "label": "Write your bio",
            "description": "Tell clients about your expertise and writing style.",
            "done": has_bio,
            "link": "/writer/account",
        },
        {
            "key": "pass_quiz",
            "label": "Pass the writing test",
            "description": "Complete the required vetting quiz to unlock order access.",
            "done": passed_quiz,
            "link": "/writer/vetting",
        },
        {
            "key": "set_availability",
            "label": "Open for assignments",
            "description": "Enable your availability to start receiving order invitations.",
            "done": has_availability,
            "link": "/writer",
        },
        {
            "key": "first_assignment",
            "label": "Take your first order",
            "description": "Browse the order queue and take an assignment.",
            "done": has_assignment,
            "link": "/writer/available",
        },
    ]

    completed = sum(1 for s in steps if s["done"])
    return {"role": "writer", "steps": steps, "completed": completed, "total": len(steps)}


class OnboardingStatusView(APIView):
    """
    GET /api/v1/accounts/onboarding-status/
    Returns the current user's onboarding checklist for their role.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        website = getattr(request, "website", None)
        role = getattr(user, "role", "")

        if role == "client":
            return Response(_client_checklist(user, website))
        if role == "writer":
            return Response(_writer_checklist(user, website))

        return Response({"role": role, "steps": [], "completed": 0, "total": 0})
