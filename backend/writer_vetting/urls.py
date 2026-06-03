from django.urls import path
from . import views

app_name = "writer_vetting"

urlpatterns = [
    # ── Admin — quiz & question management ───────────────────────────────────
    path("quizzes/",                           views.QuizListView.as_view(),        name="quiz-list"),
    path("quizzes/<int:pk>/",                  views.QuizDetailView.as_view(),      name="quiz-detail"),
    path("quizzes/<int:quiz_pk>/questions/",   views.QuestionListView.as_view(),    name="question-list"),
    path("questions/<int:pk>/",                views.QuestionDetailView.as_view(),  name="question-detail"),
    path("choices/<int:pk>/",                  views.ChoiceDetailView.as_view(),    name="choice-detail"),

    # ── Writer — take quizzes ─────────────────────────────────────────────────
    path("my/quizzes/",                        views.WriterMyQuizzesView.as_view(),    name="my-quizzes"),
    path("my/attempts/",                       views.WriterAttemptListView.as_view(),  name="my-attempts"),
    path("quizzes/<int:quiz_pk>/start/",       views.WriterStartAttemptView.as_view(), name="start-attempt"),
    path("attempts/<int:pk>/",                 views.WriterAttemptDetailView.as_view(), name="attempt-detail"),
    path("attempts/<int:pk>/submit/",          views.WriterSubmitAttemptView.as_view(), name="submit-attempt"),

    # ── Admin — review essay attempts ────────────────────────────────────────
    path("admin/pending-reviews/",             views.AdminPendingReviewView.as_view(),  name="pending-reviews"),
    path("admin/attempts/<int:pk>/review/",    views.AdminReviewAttemptView.as_view(),  name="review-attempt"),
]
