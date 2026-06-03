from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_management.permissions import IsAdmin
from .models import VettingChoice, VettingQuestion, VettingQuiz, WriterTestAttempt, WriterTestAnswer
from .serializers import (
    VettingChoiceWriteSerializer,
    VettingQuestionSerializer,
    VettingQuestionWriteSerializer,
    VettingQuizDetailSerializer,
    VettingQuizListSerializer,
    WriterAttemptDetailSerializer,
    WriterAttemptSerializer,
    WriterQuizDetailSerializer,
    WriterQuizSerializer,
    SubmitAnswerSerializer,
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


# ── Writer-facing views ───────────────────────────────────────────────────────

def _get_writer_profile(request):
    """Return the WriterProfile for the requesting user, or None."""
    try:
        from writer_management.utils import get_writer_profile_for_website
        website = _resolve_website(request)
        return get_writer_profile_for_website(request.user, website)
    except Exception:
        return None


class WriterMyQuizzesView(APIView):
    """
    GET /vetting/my/quizzes/
    List all active quizzes on the writer's website plus their latest attempt
    status for each.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        website = _resolve_website(request)
        quizzes = VettingQuiz.objects.filter(website=website, is_active=True).prefetch_related("questions")

        writer = _get_writer_profile(request)

        results = []
        for quiz in quizzes:
            quiz_data = WriterQuizSerializer(quiz).data
            quiz_data["question_count"] = quiz.questions.filter(is_active=True).count()

            latest_attempt = None
            attempts_used = 0
            if writer:
                qs = WriterTestAttempt.objects.filter(quiz=quiz, writer=writer).order_by("-started_at")
                attempts_used = qs.count()
                latest = qs.first()
                if latest:
                    latest_attempt = WriterAttemptSerializer(latest).data

            quiz_data["latest_attempt"] = latest_attempt
            quiz_data["attempts_used"]  = attempts_used
            quiz_data["can_attempt"]    = (
                writer is not None and
                (quiz.max_attempts == 0 or attempts_used < quiz.max_attempts) and
                (latest_attempt is None or latest_attempt["status"] not in ("in_progress",))
            )
            results.append(quiz_data)

        return Response(results)


class WriterStartAttemptView(APIView):
    """
    POST /vetting/quizzes/<quiz_pk>/start/
    Start a new attempt. Returns the quiz with questions (choices hide is_correct).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_pk):
        writer = _get_writer_profile(request)
        if not writer:
            return Response({"detail": "Writer profile not found."}, status=403)

        try:
            quiz = VettingQuiz.objects.prefetch_related(
                "questions__choices"
            ).get(pk=quiz_pk, is_active=True)
        except VettingQuiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=404)

        # Enforce max attempt limit
        existing = WriterTestAttempt.objects.filter(quiz=quiz, writer=writer)
        if quiz.max_attempts > 0 and existing.count() >= quiz.max_attempts:
            return Response({"detail": "Maximum attempts reached."}, status=400)

        # Block if an in-progress attempt exists
        in_progress = existing.filter(status="in_progress").first()
        if in_progress:
            return Response(
                WriterAttemptDetailSerializer(in_progress).data,
                status=status.HTTP_200_OK,
            )

        attempt = WriterTestAttempt.objects.create(
            quiz=quiz,
            writer=writer,
            attempt_number=existing.count() + 1,
            status="in_progress",
        )

        data = WriterAttemptSerializer(attempt).data
        data["quiz_detail"] = WriterQuizDetailSerializer(quiz).data
        return Response(data, status=status.HTTP_201_CREATED)


class WriterSubmitAttemptView(APIView):
    """
    POST /vetting/attempts/<pk>/submit/
    Submit all answers. MCQ/T-F quizzes are auto-scored immediately.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        writer = _get_writer_profile(request)
        if not writer:
            return Response({"detail": "Writer profile not found."}, status=403)

        try:
            attempt = WriterTestAttempt.objects.select_related("quiz").get(
                pk=pk, writer=writer, status="in_progress"
            )
        except WriterTestAttempt.DoesNotExist:
            return Response({"detail": "Active attempt not found."}, status=404)

        answers_data = request.data.get("answers", [])
        answer_serializer = SubmitAnswerSerializer(data=answers_data, many=True)
        answer_serializer.is_valid(raise_exception=True)

        from django.utils import timezone

        for item in answer_serializer.validated_data:
            question = VettingQuestion.objects.filter(
                pk=item["question_id"], quiz=attempt.quiz, is_active=True
            ).first()
            if not question:
                continue

            choice = None
            if item.get("selected_choice_id") and question.question_type in ("multiple_choice", "true_false"):
                choice = VettingChoice.objects.filter(
                    pk=item["selected_choice_id"], question=question
                ).first()

            is_correct = None
            points_earned = 0
            if choice is not None:
                is_correct = choice.is_correct
                points_earned = question.points if is_correct else 0

            WriterTestAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    "selected_choice": choice,
                    "essay_response": item.get("essay_response", ""),
                    "essay_file_id":   item.get("essay_file_id", ""),
                    "essay_file_name": item.get("essay_file_name", ""),
                    "is_correct": is_correct,
                    "points_earned": points_earned,
                },
            )

        attempt.submitted_at = timezone.now()
        attempt.save(update_fields=["submitted_at"])

        # Auto-score (sets status to passed/failed/pending_review)
        attempt.auto_score()

        return Response(WriterAttemptDetailSerializer(attempt).data)


class WriterAttemptListView(APIView):
    """GET /vetting/my/attempts/  — list all my attempts."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        writer = _get_writer_profile(request)
        if not writer:
            return Response([])
        attempts = WriterTestAttempt.objects.filter(writer=writer).select_related("quiz").order_by("-started_at")
        return Response(WriterAttemptSerializer(attempts, many=True).data)


class WriterAttemptDetailView(APIView):
    """GET /vetting/attempts/<pk>/  — single attempt with answers (post-submission)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        writer = _get_writer_profile(request)
        if not writer:
            return Response({"detail": "Writer profile not found."}, status=403)
        try:
            attempt = WriterTestAttempt.objects.prefetch_related(
                "answers__question__choices", "answers__selected_choice"
            ).get(pk=pk, writer=writer)
        except WriterTestAttempt.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        return Response(WriterAttemptDetailSerializer(attempt).data)


# ── Admin review of pending essay attempts ────────────────────────────────────

class AdminReviewAttemptView(APIView):
    """
    POST /vetting/admin/attempts/<pk>/review/
    Admin grades a pending-review (essay) attempt.
    Body: { passed: bool, reviewer_notes: str }
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            attempt = WriterTestAttempt.objects.get(pk=pk, status="pending_review")
        except WriterTestAttempt.DoesNotExist:
            return Response({"detail": "Not found or already reviewed."}, status=404)

        passed = request.data.get("passed")
        if passed is None:
            return Response({"detail": "'passed' (bool) is required."}, status=400)

        from django.utils import timezone
        attempt.passed         = bool(passed)
        attempt.status         = "passed" if attempt.passed else "failed"
        attempt.reviewed_by    = request.user
        attempt.reviewed_at    = timezone.now()
        attempt.reviewer_notes = request.data.get("reviewer_notes", "")
        attempt.save(update_fields=["passed", "status", "reviewed_by", "reviewed_at", "reviewer_notes", "updated_at"])
        return Response(WriterAttemptSerializer(attempt).data)


class AdminPendingReviewView(APIView):
    """GET /vetting/admin/pending-reviews/  — list essay attempts awaiting grading."""
    permission_classes = [IsAdmin]

    def get(self, request):
        website = _resolve_website(request)
        attempts = WriterTestAttempt.objects.filter(
            quiz__website=website, status="pending_review"
        ).select_related("quiz", "writer").order_by("started_at")
        return Response(WriterAttemptSerializer(attempts, many=True).data)


class AdminApplicationQuizStatusView(APIView):
    """
    GET /vetting/admin/application-status/?email=<email>&website_id=<id>
    Returns required quizzes and the applicant's best attempt for each.
    Used by the applications view to show pass/fail before approving.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        email      = request.query_params.get("email", "").strip()
        website_id = request.query_params.get("website_id")
        website    = _resolve_website(request)

        if website_id:
            from websites.models.websites import Website
            try:
                website = Website.objects.get(pk=website_id)
            except Website.DoesNotExist:
                pass

        required_quizzes = VettingQuiz.objects.filter(
            website=website,
            is_active=True,
            is_required_for_approval=True,
        )

        result = []
        applicant = None
        if email:
            from django.contrib.auth import get_user_model
            _User = get_user_model()
            try:
                applicant = _User.objects.get(email__iexact=email)
            except _User.DoesNotExist:
                pass

        for quiz in required_quizzes:
            best_attempt = None
            if applicant:
                attempt = WriterTestAttempt.objects.filter(
                    quiz=quiz,
                    writer__account_profile__user=applicant,
                ).order_by("-started_at").first()
                if attempt:
                    best_attempt = {
                        "id":         attempt.id,
                        "status":     attempt.status,
                        "score":      str(attempt.score) if attempt.score is not None else None,
                        "passed":     attempt.passed,
                        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                    }

            result.append({
                "quiz_id":    quiz.id,
                "quiz_title": quiz.title,
                "quiz_type":  quiz.quiz_type,
                "pass_score": quiz.pass_score,
                "required":   True,
                "passed":     best_attempt.get("passed") if best_attempt else None,
                "attempt":    best_attempt,
            })

        all_passed = all(r["passed"] for r in result) if result else True
        return Response({
            "required_quizzes": result,
            "all_required_passed": all_passed,
            "has_required_quizzes": bool(result),
        })
