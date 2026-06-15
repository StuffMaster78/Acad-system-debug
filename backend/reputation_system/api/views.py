from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.permissions import IsAdminOrSuperAdmin

from reputation_system.services.reputation_query_service import ReputationQueryService
from reputation_system.services.writer_leaderboard_service import WriterLeaderboardService


def _snap_to_dict(snap):
    if snap is None:
        return None
    return {
        "writer_id": str(snap.writer_id),
        "rating": str(snap.rating),
        "review_count": snap.review_count,
        "verified_review_count": snap.verified_review_count,
        "trust_score": str(snap.trust_score),
        "metadata": snap.metadata,
        "updated_at": snap.updated_at.isoformat() if snap.updated_at else None,
    }


class WriterReputationView(APIView):
    """GET /api/v1/reputation/writers/<writer_id>/"""
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, writer_id):
        snap = ReputationQueryService.get_writer_reputation(writer_id)
        if snap is None:
            return Response({"detail": "No reputation record found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(_snap_to_dict(snap))


class WebsiteReputationView(APIView):
    """GET /api/v1/reputation/websites/<website_id>/"""
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, website_id):
        snap = ReputationQueryService.get_website_reputation(website_id)
        if snap is None:
            return Response({"detail": "No reputation record found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "website_id": website_id,
            "rating": str(snap.rating),
            "review_count": snap.review_count,
            "updated_at": snap.updated_at.isoformat() if snap.updated_at else None,
        })


class LeaderboardView(APIView):
    """GET /api/v1/reputation/leaderboard/?limit=50&website_id=<id>"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 50)), 200)
        website_id = request.query_params.get("website_id")

        entries = WriterLeaderboardService.global_leaderboard(limit=limit)
        return Response({
            "results": [
                {
                    "rank": e.rank,
                    "writer_id": str(e.writer_id),
                    "rating": str(e.rating),
                    "review_count": e.review_count,
                    "trust_score": str(e.trust_score),
                }
                for e in entries
            ],
            "count": len(entries),
        })


class WriterRankView(APIView):
    """GET /api/v1/reputation/writers/<writer_id>/rank/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, writer_id):
        rank = WriterLeaderboardService.writer_rank(writer_id=writer_id)
        percentile = WriterLeaderboardService.percentile_rank(writer_id=writer_id)
        return Response({
            "writer_id": str(writer_id),
            "rank": rank,
            "percentile": str(percentile) if percentile is not None else None,
        })
