from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_management.permissions import IsAdmin
from .models import VettingChoice, VettingQuestion, VettingQuiz
from .serializers import (
    VettingChoiceWriteSerializer,
    VettingQuestionSerializer,
    VettingQuestionWriteSerializer,
    VettingQuizDetailSerializer,
    VettingQuizListSerializer,
)


def _resolve_website(request):
    website = getattr(request, "website", None)
    if website:
        return website
    try:
        return request.user.account_profiles.order_by("pk").first().website
    except Exception:
        return None


# ── Quizzes ──────────────────────────────────────────────────────────────────

class QuizListView(APIView):
    """
    GET  /vetting/quizzes/          list
    POST /vetting/quizzes/          create
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        website = _resolve_website(request)
        qs = VettingQuiz.objects.filter(website=website)

        quiz_type = request.query_params.get("quiz_type")
        if quiz_type:
            qs = qs.filter(quiz_type=quiz_type)

        is_active = request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")

        return Response(VettingQuizListSerializer(qs, many=True).data)

    def post(self, request):
        website = _resolve_website(request)
        serializer = VettingQuizListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save(website=website, created_by=request.user)
        return Response(
            VettingQuizListSerializer(quiz).data,
            status=status.HTTP_201_CREATED,
        )


class QuizDetailView(APIView):
    """
    GET    /vetting/quizzes/<pk>/    detail with questions
    PATCH  /vetting/quizzes/<pk>/    update
    DELETE /vetting/quizzes/<pk>/    delete
    """
    permission_classes = [IsAdmin]

    def _get(self, pk):
        try:
            return VettingQuiz.objects.prefetch_related(
                "questions__choices"
            ).get(pk=pk)
        except VettingQuiz.DoesNotExist:
            return None

    def get(self, request, pk):
        quiz = self._get(pk)
        if not quiz:
            return Response({"detail": "Not found."}, status=404)
        return Response(VettingQuizDetailSerializer(quiz).data)

    def patch(self, request, pk):
        quiz = self._get(pk)
        if not quiz:
            return Response({"detail": "Not found."}, status=404)
        serializer = VettingQuizListSerializer(quiz, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        quiz = self._get(pk)
        if not quiz:
            return Response({"detail": "Not found."}, status=404)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Questions ────────────────────────────────────────────────────────────────

class QuestionListView(APIView):
    """
    GET  /vetting/quizzes/<quiz_pk>/questions/    list
    POST /vetting/quizzes/<quiz_pk>/questions/    create
    """
    permission_classes = [IsAdmin]

    def get(self, request, quiz_pk):
        qs = VettingQuestion.objects.filter(
            quiz_id=quiz_pk, is_active=True
        ).prefetch_related("choices").order_by("order", "id")
        return Response(VettingQuestionSerializer(qs, many=True).data)

    def post(self, request, quiz_pk):
        try:
            VettingQuiz.objects.get(pk=quiz_pk)
        except VettingQuiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=404)

        data = {**request.data, "quiz": quiz_pk}
        serializer = VettingQuestionWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        return Response(
            VettingQuestionSerializer(question).data,
            status=status.HTTP_201_CREATED,
        )


class QuestionDetailView(APIView):
    """
    GET    /vetting/questions/<pk>/    detail
    PATCH  /vetting/questions/<pk>/    update (replaces choices)
    DELETE /vetting/questions/<pk>/    delete
    """
    permission_classes = [IsAdmin]

    def _get(self, pk):
        try:
            return VettingQuestion.objects.prefetch_related("choices").get(pk=pk)
        except VettingQuestion.DoesNotExist:
            return None

    def get(self, request, pk):
        q = self._get(pk)
        if not q:
            return Response({"detail": "Not found."}, status=404)
        return Response(VettingQuestionSerializer(q).data)

    def patch(self, request, pk):
        q = self._get(pk)
        if not q:
            return Response({"detail": "Not found."}, status=404)
        serializer = VettingQuestionWriteSerializer(q, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(VettingQuestionSerializer(q).data)

    def delete(self, request, pk):
        q = self._get(pk)
        if not q:
            return Response({"detail": "Not found."}, status=404)
        q.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Choices (direct update) ──────────────────────────────────────────────────

class ChoiceDetailView(APIView):
    """
    PATCH  /vetting/choices/<pk>/
    DELETE /vetting/choices/<pk>/
    """
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            choice = VettingChoice.objects.get(pk=pk)
        except VettingChoice.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        serializer = VettingChoiceWriteSerializer(choice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            choice = VettingChoice.objects.get(pk=pk)
        except VettingChoice.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        choice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
