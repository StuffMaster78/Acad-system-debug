from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.permissions import IsAdminOrSuperAdmin

from reputation_system.services.reputation_query_service import ReputationQueryService
from reputation_system.services.writer_leaderboard_service import WriterLeaderboardService
from reputation_system.api.serializers import (
    WriterReputationSnapshotSerializer,
    WebsiteReputationSnapshotSerializer,
    LeaderboardEntrySerializer,
    WriterRankSerializer,
)


class WriterReputationView(APIView):
    """GET /api/v1/reputation/writers/<writer_id>/"""
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, writer_id):
        snap = ReputationQueryService.get_writer_reputation(writer_id)
        if snap is None:
            return Response({"detail": "No reputation record found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(WriterReputationSnapshotSerializer(snap).data)


class WebsiteReputationView(APIView):
    """GET /api/v1/reputation/websites/<website_id>/"""
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, website_id):
        snap = ReputationQueryService.get_website_reputation(website_id)
        if snap is None:
            return Response({"detail": "No reputation record found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(WebsiteReputationSnapshotSerializer(snap).data)


class LeaderboardView(APIView):
    """GET /api/v1/reputation/leaderboard/?limit=50&website_id=<id>"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 50)), 200)
        entries = WriterLeaderboardService.global_leaderboard(limit=limit)
        serializer = LeaderboardEntrySerializer(entries, many=True)
        return Response({
            "results": serializer.data,
            "count": len(entries),
        })


class WriterRankView(APIView):
    """GET /api/v1/reputation/writers/<writer_id>/rank/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, writer_id):
        rank = WriterLeaderboardService.writer_rank(writer_id=writer_id)
        percentile = WriterLeaderboardService.percentile_rank(writer_id=writer_id)
        serializer = WriterRankSerializer({
            "writer_id": writer_id,
            "rank": rank,
            "percentile": percentile,
        })
        return Response(serializer.data)
